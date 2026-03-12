"""
Cross-Site Scripting (XSS) vulnerability scanner.

Detects common XSS patterns in web application code.
"""

import re
from pathlib import Path
from typing import List, Optional
from ..core.vulnerability import VulnerabilityFinding, VulnerabilityType, Severity, Location
from ..core.scanner import BaseScanner, SecurityContext


class XSSScanner(BaseScanner):
    """Detects cross-site scripting (XSS) vulnerabilities."""
    
    # Patterns indicating potential XSS vulnerabilities
    VULNERABLE_PATTERNS = {
        "python": [
            # Unescaped template variables
            (r'{{.*}}|{%.*%}', "Template variable without escaping"),
            (r'render_template_string\s*\(.*\+', "Template concatenation"),
            (r'\.format\s*\(\s*.*request\..*\)', "User input in format string"),
            (r'(innerHTML|dangerouslySetInnerHTML)\s*=\s*', "Direct HTML assignment"),
        ],
        "javascript": [
            # innerHTML assignments with user input
            (r'\.innerHTML\s*=\s*["`\'].*\$\{.*\}`', "innerHTML with template literal"),
            (r'\.innerHTML\s*=\s*.*\+.*request\.', "innerHTML with concatenation"),
            # insertAdjacentHTML
            (r'insertAdjacentHTML\s*\(\s*["\'].*["\'],\s*.*request\.', "insertAdjacentHTML with user input"),
            # dangerouslySetInnerHTML in React
            (r'dangerouslySetInnerHTML\s*=\s*\{.*\}', "dangerouslySetInnerHTML"),
            # eval-like functions
            (r'(eval|Function)\s*\(\s*.*request\.', "eval with user input"),
            # jQuery methods
            (r'\$\(["\'].*["\']\)\.html\s*\(.*request\.', "jQuery html() with user input"),
        ],
        "java": [
            # JSP/template expression language
            (r'\$\{.*\}|\${.*\}', "Expression language without escaping"),
            # Response.sendRedirect with user input
            (r'sendRedirect\s*\(\s*.*request\.getParameter', "sendRedirect with user input"),
        ],
        "html": [
            # Inline scripts with user variables
            (r'<script>.*\${.*}</script>', "Script tag with user variable"),
            # Event handlers with user input
            (r'on\w+\s*=\s*["\'].*\$\{.*\}["\']', "Event handler with template variable"),
        ],
    }
    
    # Safe escaping patterns
    SAFE_FILTERS = {
        "python": [
            r'html\.escape\s*\(',
            r'escape\s*\(',
            r'markupsafe\.escape\s*\(',
            r'django\.utils\.html\.escape\s*\(',
            r'\|escape',  # Template filter
            r'\|striptags',
        ],
        "javascript": [
            r'textContent\s*=',  # textContent is safer than innerHTML
            r'escapeHtml\s*\(',
            r'DOMPurify\.sanitize\s*\(',
            r'sanitizeHtml\s*\(',
            r'xss\s*\(',  # XSS library
        ],
        "java": [
            r'StringEscapeUtils\.escapeHtml\(',
            r'ESAPI\.encoder\.encodeForHTML\(',
        ],
    }
    
    REMEDIATION = """Use proper output encoding and sanitization:

Python (Flask):
  # ❌ Vulnerable
  {{ user_input }}
  
  # ✅ Safe - Jinja2 auto-escapes by default
  {{ user_input }}
  
  # For HTML content:
  from markupsafe import escape
  html_content = escape(user_input)

JavaScript:
  // ❌ Vulnerable
  element.innerHTML = userInput;
  
  // ✅ Safe - use textContent for text
  element.textContent = userInput;
  
  // ✅ Safe - sanitize for HTML
  import DOMPurify from 'dompurify';
  element.innerHTML = DOMPurify.sanitize(userInput);

Java:
  // ❌ Vulnerable
  response.getWriter().println(request.getParameter("name"));
  
  // ✅ Safe
  from org.apache.commons.lang3.StringEscapeUtils;
  response.getWriter().println(StringEscapeUtils.escapeHtml4(request.getParameter("name")));
"""
    
    def get_scanner_name(self) -> str:
        return "XSS (Cross-Site Scripting) Scanner"
    
    def get_scanner_description(self) -> str:
        return "Detects cross-site scripting vulnerabilities from unescaped user input in templates and DOM"
    
    def scan(self) -> List[VulnerabilityFinding]:
        """Scan workspace for XSS vulnerabilities."""
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
        """Scan file content for XSS vulnerabilities."""
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
                    # Check if line uses safe escaping
                    if self._is_safe_context(line, language):
                        continue
                    
                    self._add_xss_finding(
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        description=description,
                    )
    
    def _is_safe_context(self, line: str, language: str) -> bool:
        """Check if line uses safe output encoding."""
        for pattern in self.SAFE_FILTERS.get(language, []):
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        # Check for text-only assignments (safer than HTML)
        if re.search(r'\.text\s*=|\.textContent\s*=|\.innerText\s*=', line):
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
            '.jsx.js': 'javascript',
            '.html': 'html',
            '.jinja': 'python',
            '.jinja2': 'python',
            '.erb': 'ruby',
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
        elif language == 'html':
            return stripped.startswith('<!--')
        
        return False
    
    def _add_xss_finding(
        self,
        file_path: Path,
        line_number: int,
        line_content: str,
        description: str,
    ) -> None:
        """Add an XSS finding."""
        finding = VulnerabilityFinding(
            id=f"xss_{file_path.name}_{line_number}",
            vulnerability_type=VulnerabilityType.XSS_CROSS_SITE_SCRIPTING,
            severity=Severity.HIGH,
            title="Cross-Site Scripting (XSS) Vulnerability",
            description=description,
            location=Location(
                file_path=str(file_path),
                line_number=line_number,
                line_content=line_content,
            ),
            cwe_id="CWE-79",
            remediation=self.REMEDIATION,
            confidence=0.80,
            tags={"xss", "injection", "cwe-79", "owasp-a03", "web", "high"},
        )
        self.add_finding(finding)
