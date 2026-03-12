"""
Base scanner classes and infrastructure.

Provides foundation for all security scanners with plugin architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Type
from pathlib import Path
import logging

from .vulnerability import VulnerabilityFinding, ComplianceViolation, RiskAssessment


logger = logging.getLogger(__name__)


@dataclass
class SecurityContext:
    """Context for security scanning operations."""
    workspace_root: Path
    included_paths: List[Path] = field(default_factory=lambda: [Path(".")])
    excluded_paths: List[Path] = field(default_factory=lambda: [
        Path(".git"),
        Path(".venv"),
        Path("node_modules"),
        Path(".env"),
        Path("__pycache__"),
        Path("build"),
        Path("dist"),
    ])
    language_hints: List[str] = field(default_factory=lambda: ["python", "java", "javascript", "go"])
    max_file_size: int = 1_000_000  # 1MB
    follow_symlinks: bool = False
    scan_git_history: bool = False
    git_depth: int = 50  # Number of commits to scan
    check_env_files: bool = True
    check_config_files: bool = True
    verbose: bool = False
    
    def get_files_to_scan(self) -> List[Path]:
        """Get all files that should be scanned."""
        files = []
        
        for included_path in self.included_paths:
            full_path = self.workspace_root / included_path
            if full_path.is_file():
                files.append(full_path)
            elif full_path.is_dir():
                for item in full_path.rglob("*"):
                    if item.is_file() and self._should_scan_file(item):
                        files.append(item)
        
        return files
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if a file should be scanned."""
        # Check size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return False
        except (OSError, IOError):
            return False
        
        # Check excluded paths
        for excluded in self.excluded_paths:
            if excluded in file_path.parents or file_path.name == excluded.name:
                return False
        
        # Check if binary file
        try:
            file_path.read_text(errors='ignore')
        except Exception:
            return False
        
        return True


class BaseScanner(ABC):
    """Base class for all security scanners."""
    
    def __init__(self, context: SecurityContext):
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)
        self.findings: List[VulnerabilityFinding] = []
        self.violations: List[ComplianceViolation] = []
    
    @abstractmethod
    def scan(self) -> List[VulnerabilityFinding]:
        """Execute the scan and return findings."""
        pass
    
    @abstractmethod
    def get_scanner_name(self) -> str:
        """Return the name of this scanner."""
        pass
    
    @abstractmethod
    def get_scanner_description(self) -> str:
        """Return description of what this scanner does."""
        pass
    
    def scan_file(self, file_path: Path) -> List[VulnerabilityFinding]:
        """Scan a single file."""
        try:
            content = file_path.read_text(errors='ignore')
            return self.scan_content(content, file_path)
        except Exception as e:
            self.logger.error(f"Error scanning {file_path}: {e}")
            return []
    
    def scan_content(self, content: str, file_path: Path) -> List[VulnerabilityFinding]:
        """Scan content string. Override in subclasses as needed."""
        return []
    
    def add_finding(self, finding: VulnerabilityFinding) -> None:
        """Add a vulnerability finding."""
        self.findings.append(finding)
    
    def add_violation(self, violation: ComplianceViolation) -> None:
        """Add a compliance violation."""
        self.violations.append(violation)
    
    def get_findings(self) -> List[VulnerabilityFinding]:
        """Get all findings from this scanner."""
        return self.findings
    
    def get_violations(self) -> List[ComplianceViolation]:
        """Get all compliance violations from this scanner."""
        return self.violations
    
    def clear(self) -> None:
        """Clear all findings and violations."""
        self.findings = []
        self.violations = []


class ScannerRegistry:
    """Registry for security scanners with plugin support."""
    
    def __init__(self):
        self._scanners: Dict[str, Type[BaseScanner]] = {}
        self._instances: Dict[str, BaseScanner] = {}
    
    def register(self, name: str, scanner_class: Type[BaseScanner]) -> None:
        """Register a scanner class."""
        if not issubclass(scanner_class, BaseScanner):
            raise TypeError(f"{scanner_class} must be a subclass of BaseScanner")
        self._scanners[name] = scanner_class
        self.logger.info(f"Registered scanner: {name}")
    
    def instantiate(self, name: str, context: SecurityContext) -> BaseScanner:
        """Create an instance of a registered scanner."""
        if name not in self._scanners:
            raise ValueError(f"Scanner '{name}' not registered")
        return self._scanners[name](context)
    
    def get_all_scanners(self, context: SecurityContext) -> Dict[str, BaseScanner]:
        """Get all registered scanner instances."""
        return {name: self.instantiate(name, context) for name in self._scanners.keys()}
    
    def get_scanner_names(self) -> List[str]:
        """Get all registered scanner names."""
        return list(self._scanners.keys())
    
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(self.__class__.__name__)
