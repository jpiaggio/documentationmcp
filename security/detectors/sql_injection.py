"""
SQL Injection vulnerability scanner.

Detects common SQL injection patterns in code.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional
from ..core.vulnerability import VulnerabilityFinding, VulnerabilityType, Severity, Location
from ..core.scanner import BaseScanner, SecurityContext


class SQLInjectionScanner(BaseScanner):
    """Detects SQL injection vulnerabilities."""
    
    # Patterns that indicate vulnerable SQL operations
    VULNERABLE_PATTERNS = {
        "python": [
            # String concatenation with user input
            (r'(execute|executescript|query)\s*\(\s*["\'].*[+%s].*?["\']', "String concatenation in SQL"),
            (r'(execute|executescript|query)\s*\(["\'](?!.*\?)[^"\']*\"\s*[+%\s]', "Unparameterized query"),
            # f-string with user input in SQL
            (r'(execute|executescript|query)\s*\(\s*f["\'].*\{.*\}', "f-string with user input in SQL"),
            # Format with user input
            (r'(execute|executescript|query)\s*\(["\'].*\.format\(', "format() with user input in SQL"),
            # % formatting with user input
            (r'(execute|executescript|query)\s*\(["\'].*%\s*\)', "% formatting in SQL query"),
        ],
        "java": [
            # String concatenation in executeQuery
            (r'executeQuery\s*\(\s*["\'].*\"\s*[+\s]', "String concatenation in executeQuery"),
            # Statement instead of PreparedStatement
            (r'Statement\s+\w+\s*=\s*connection\.createStatement\(\)', "Using Statement instead of PreparedStatement"),
            (r'executeQuery\s*\(\s*["\'](?!.*\?)[^"\']+["\']', "Unparameterized query"),
        ],
        "javascript": [
            # String concatenation in queries
            (r'(query|exec)\s*\(\s*["\'].*\"\s*[+\s]', "String concatenation in SQL query"),
            # Template literals with user input
            (r'(query|exec)\s*\(\s*`.*\$\{.*\}`', "Template literal with user input in SQL"),
        ],
    }
    
    # Patterns that indicate safe parameterized queries
    SAFE_PATTERNS = {
        "python": [
            r'execute\s*\(["\'][^"\']*\?\s*["\'],\s*\(',  # ? with parameter tuple
            r'executemany\s*\(["\'][^"\']*\?\s*["\']',    # parameterized executemany
        ],
        "java": [
            r'PreparedStatement\s+\w+\s*=\s*connection\.prepareStatement\(',
            r'setString\s*\(\s*\d+\s*,',  # parameterized setters
        ],
        "javascript": [
            r'\?\s*,',  # Parameterized query indicator
        ],
    }
    
    REMEDIATION = """Use parameterized queries (prepared statements) instead of string concatenation:

Python:
  # ❌ Vulnerable
  cursor.execute("SELECT * FROM users WHERE id = " + user_id)
  
  # ✅ Safe
  cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

Java:
  // ❌ Vulnerable
  stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);
  
  // ✅ Safe
  PreparedStatement pstmt = connection.prepareStatement("SELECT * FROM users WHERE id = ?");
  pstmt.setInt(1, userId);
  pstmt.executeQuery();

JavaScript:
  // ❌ Vulnerable
  db.query("SELECT * FROM users WHERE id = " + userId);
  
  // ✅ Safe
  db.query("SELECT * FROM users WHERE id = ?", [userId]);
"""
    
    def get_scanner_name(self) -> str:
        return "SQL Injection Scanner"
    
    def get_scanner_description(self) -> str:
        return "Detects SQL injection vulnerabilities from unparameterized queries and string concatenation"
    
    def scan(self) -> List[VulnerabilityFinding]:
        """Scan workspace for SQL injection vulnerabilities."""
        self.findings = []
        
        files_to_scan = self.context.get_files_to_scan()
        
        for file_path in files_to_scan:
            try:
                content = file_path.read_text(errors='ignore')
                self._scan_file_content(content, file_path)
            except Exception as e:
                self.logger.error(f"Error scanning {file_path}: {e}")
        
        return self.findings
    
    def _scan_file_content(self, content: str, file_path: Path) -> None:
        """Scan file content for SQL injection vulnerabilities."""
        language = self._detect_language(file_path)
        if language not in self.VULNERABLE_PATTERNS:
            return
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments and docstrings
            if self._is_comment_or_docstring(line, language):
                continue
            
            # Check for vulnerable patterns
            for pattern, description in self.VULNERABLE_PATTERNS[language]:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's actually safe (parameterized)
                    if self._is_safe_query(line, language):
                        continue
                    
                    self._add_sql_injection_finding(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        description=description,
                    )
    
    def _is_safe_query(self, line: str, language: str) -> bool:
        """Check if a line uses safe parameterized queries."""
        for pattern in self.SAFE_PATTERNS.get(language, []):
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        ext_to_lang = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.jsx': 'javascript',
            '.tsx': 'javascript',
            '.go': 'python',  # Golang uses different patterns
        }
        return ext_to_lang.get(file_path.suffix)
    
    def _is_comment_or_docstring(self, line: str, language: str) -> bool:
        """Check if line is a comment or docstring."""
        stripped = line.strip()
        
        if language == 'python':
            return (stripped.startswith('#') or 
                    stripped.startswith('"""') or 
                    stripped.startswith("'''"))
        elif language == 'java':
            return (stripped.startswith('//') or 
                    stripped.startswith('*'))
        elif language == 'javascript':
            return (stripped.startswith('//') or 
                    stripped.startswith('/*'))
        
        return False
    
    def _add_sql_injection_finding(
        self,
        file_path: Path,
        line_number: int,
        line_content: str,
        description: str,
    ) -> None:
        """Add a SQL injection finding."""
        finding = VulnerabilityFinding(
            id=f"sql_injection_{file_path.name}_{line_number}",
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            severity=Severity.CRITICAL,
            title="SQL Injection Vulnerability",
            description=description,
            location=Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            ),
            cwe_id="CWE-89",
            remediation=self.REMEDIATION,
            confidence=0.85,
            tags={"sql", "injection", "cwe-89", "owasp-a03", "critical"},
        )
        self.add_finding(finding)
