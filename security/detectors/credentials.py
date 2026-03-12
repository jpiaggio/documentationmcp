"""
Exposed credential and secret detection scanner.

Detects hardcoded credentials, API keys, tokens, and other sensitive data.
"""

import re
import os
from pathlib import Path
from typing import List, Optional, Set, Dict
from ..core.vulnerability import VulnerabilityFinding, VulnerabilityType, Severity, Location
from ..core.scanner import BaseScanner, SecurityContext


class CredentialScanner(BaseScanner):
    """Detects exposed credentials and secrets in code."""
    
    # Credential patterns to detect
    CREDENTIAL_PATTERNS = {
        "api_key": {
            "pattern": r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_API_KEY,
        },
        "password": {
            "pattern": r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{8,})["\']',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_PASSWORD,
        },
        "aws_key": {
            "pattern": r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[=:]\s*["\']([A-Z0-9]{20})\s*["\']',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_API_KEY,
        },
        "ssh_private_key": {
            "pattern": r'-----BEGIN (RSA|DSA|EC|PGP|OPENSSH) PRIVATE KEY-----',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_PRIVATE_KEY,
        },
        "github_token": {
            "pattern": r'(?i)(github[_-]?token|ghp_[a-zA-Z0-9]{36,})',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_TOKEN,
        },
        "slack_token": {
            "pattern": r'(xox[baprs]-[a-zA-Z0-9]{10,48}[a-zA-Z0-9-]{0,})',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_TOKEN,
        },
        "stripe_key": {
            "pattern": r'(?i)(sk_live|pk_live)_[a-zA-Z0-9]{24,}',
            "severity": Severity.CRITICAL,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_API_KEY,
        },
        "jwt_token": {
            "pattern": r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.([a-zA-Z0-9_-]{40,}|[a-zA-Z0-9_-]{43,})',
            "severity": Severity.HIGH,
            "cwe": "CWE-798",
            "type": VulnerabilityType.EXPOSED_TOKEN,
        },
        "db_connection_string": {
            "pattern": r'(?i)(password\s*[=:]\s*[^;@\s]+|server=.*password=)',
            "severity": Severity.HIGH,
            "cwe": "CWE-798",
            "type": VulnerabilityType.HARDCODED_CREDENTIAL,
        },
        "hardcoded_credential": {
            "pattern": r'(?i)(secret|credential|auth|token)\s*[=:]\s*["\']([a-zA-Z0-9!@#$%^&*_\-=+]{15,})["\']',
            "severity": Severity.MEDIUM,
            "cwe": "CWE-798",
            "type": VulnerabilityType.HARDCODED_CREDENTIAL,
        },
    }
    
    # False positive suppressions
    FALSE_POSITIVES: Set[str] = {
        "demo_key",
        "test_key",
        "example_",
        "placeholder",
        "TODO",
        "FIXME",
        "CHANGEME",
        "your_",
        "[password]",
        "<password>",
    }
    
    REMEDIATION = """Move credentials to environment variables or secrets management:

Python:
  # ❌ Vulnerable
  API_KEY = 'sk_live_abc123xyz'
  PASSWORD = 'mypassword123'
  
  # ✅ Safe
  import os
  from dotenv import load_dotenv
  
  load_dotenv()
  API_KEY = os.getenv('API_KEY')
  PASSWORD = os.getenv('DB_PASSWORD')

JavaScript:
  // ❌ Vulnerable
  const API_KEY = 'sk_live_abc123xyz';
  
  // ✅ Safe
  const API_KEY = process.env.API_KEY;

Java:
  // ❌ Vulnerable
  String password = "mypassword123";
  
  // ✅ Safe
  String password = System.getenv("DB_PASSWORD");

Recommended tools:
  - AWS Secrets Manager
  - HashiCorp Vault
  - GitHub Secrets
  - GitLab CI/CD Variables
  - Kubernetes Secrets
  - 1Password / LastPass
"""
    
    def get_scanner_name(self) -> str:
        return "Credential & Secret Scanner"
    
    def get_scanner_description(self) -> str:
        return "Detects exposed API keys, passwords, tokens, SSH keys, and other credentials"
    
    def scan(self) -> List[VulnerabilityFinding]:
        """Scan workspace for exposed credentials."""
        self.findings = []
        
        # Scan source files
        files_to_scan = self.context.get_files_to_scan()
        for file_path in files_to_scan:
            try:
                content = file_path.read_text(errors='ignore')
                self._scan_file_content(content, file_path)
            except Exception as e:
                self.logger.error(f"Error scanning {file_path}: {e}")
        
        # Scan config files if enabled
        if self.context.check_config_files:
            self._scan_config_files()
        
        # Scan environment if enabled
        if self.context.check_env_files:
            self._scan_env_variables()
        
        # Scan git history if enabled
        if self.context.scan_git_history:
            self._scan_git_history()
        
        return self.findings
    
    def _scan_file_content(self, content: str, file_path: Path) -> None:
        """Scan file content for exposed credentials."""
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments in known languages
            if self._is_comment_line(line):
                continue
            
            # Check against all credential patterns
            for cred_type, pattern_info in self.CREDENTIAL_PATTERNS.items():
                matches = re.finditer(pattern_info["pattern"], line)
                
                for match in matches:
                    # Check for false positives
                    if self._is_false_positive(match.group(0)):
                        continue
                    
                    self._add_credential_finding(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=self._redact_line(line),
                        credential_type=cred_type,
                        pattern_info=pattern_info,
                    )
    
    def _scan_config_files(self) -> None:
        """Scan configuration files for credentials."""
        config_extensions = {'.env', '.ini', '.conf', '.yaml', '.yml', '.json', '.toml'}
        
        for root, dirs, files in os.walk(self.context.workspace_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if Path(d) not in self.context.excluded_paths]
            
            for file in files:
                if Path(file).suffix in config_extensions:
                    file_path = Path(root) / file
                    if self.context._should_scan_file(file_path):
                        try:
                            content = file_path.read_text(errors='ignore')
                            self._scan_file_content(content, file_path)
                        except Exception as e:
                            self.logger.error(f"Error scanning config {file_path}: {e}")
    
    def _scan_env_variables(self) -> None:
        """Scan environment variables for sensitive data."""
        sensitive_env_vars = {
            "PASSWORD", "SECRET", "TOKEN", "KEY", "API_KEY",
            "AWS_SECRET", "DATABASE_PASSWORD", "PRIVATE_KEY"
        }
        
        for var_name, var_value in os.environ.items():
            if any(sensitive in var_name.upper() for sensitive in sensitive_env_vars):
                if var_value and not self._is_false_positive(var_value):
                    self._add_credential_finding(
                        file_path=Path("<environment>"),
                        line_number=0,
                        line_content=f"{var_name}=***",
                        credential_type="environment_variable",
                        pattern_info={
                            "severity": Severity.HIGH,
                            "cwe": "CWE-798",
                            "type": VulnerabilityType.HARDCODED_CREDENTIAL,
                        },
                    )
    
    def _scan_git_history(self) -> None:
        """Scan git history for exposed credentials (limited depth)."""
        try:
            import subprocess
            git_dir = self.context.workspace_root / ".git"
            if not git_dir.exists():
                return
            
            # Get recent commits
            cmd = [
                "git",
                "-C", str(self.context.workspace_root),
                "log",
                f"-n {self.context.git_depth}",
                "--oneline",
                "-p"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self._scan_file_content(result.stdout, Path("<git-history>"))
        
        except Exception as e:
            self.logger.warning(f"Could not scan git history: {e}")
    
    def _is_comment_line(self, line: str) -> bool:
        """Check if line is a comment."""
        stripped = line.strip()
        return (stripped.startswith('#') or 
                stripped.startswith('//') or 
                stripped.startswith('/*') or 
                stripped.startswith('*') or
                stripped.startswith('--'))
    
    def _is_false_positive(self, match: str) -> bool:
        """Check if match is a false positive."""
        for fp in self.FALSE_POSITIVES:
            if fp.lower() in match.lower():
                return True
        return False
    
    def _redact_line(self, line: str) -> str:
        """Redact sensitive information from line for reporting."""
        # Redact quoted strings
        result = re.sub(r'(["\'])([^"\']+)(["\'])', r'\1***\3', line)
        return result.strip()
    
    def _add_credential_finding(
        self,
        file_path: Path,
        line_number: int,
        line_content: str,
        credential_type: str,
        pattern_info: Dict,
    ) -> None:
        """Add a credential finding."""
        finding = VulnerabilityFinding(
            id=f"credential_{credential_type}_{file_path.name}_{line_number}",
            vulnerability_type=pattern_info["type"],
            severity=pattern_info["severity"],
            title=f"Exposed {credential_type.replace('_', ' ').title()}",
            description=f"Found {credential_type} in source code",
            location=Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            ),
            cwe_id=pattern_info["cwe"],
            remediation=self.REMEDIATION,
            confidence=0.95,
            tags={"credentials", "secrets", "hardcoded", credential_type, "cwe-798"},
        )
        self.add_finding(finding)
