"""
SARIF (Static Analysis Results Format) report generator.

SARIF is a standard format for security and quality tool results.
See: https://sarifweb.azurewebsites.net/
"""

import json
from pathlib import Path
from datetime import datetime
from ..core.vulnerability import RiskAssessment


class SARIFReporter:
    """Generates SARIF format reports for security findings."""
    
    SARIF_VERSION = "2.1.0"
    TOOL_NAME = "Security & Compliance Scanner"
    TOOL_VERSION = "1.0.0"
    
    def generate_report(self, assessment: RiskAssessment) -> str:
        """Generate SARIF report string."""
        sarif_data = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": self.SARIF_VERSION,
            "runs": [self._create_run(assessment)]
        }
        return json.dumps(sarif_data, indent=2)
    
    def save_report(self, assessment: RiskAssessment, output_path: Path) -> None:
        """Save SARIF report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(self.generate_report(assessment))
    
    def _create_run(self, assessment: RiskAssessment) -> dict:
        """Create SARIF run object."""
        return {
            "tool": self._create_tool(),
            "invocations": [self._create_invocation(assessment)],
            "results": self._create_results(assessment),
            "properties": {
                "riskScore": assessment.risk_score,
                "riskLevel": assessment.overall_risk_level,
                "scannedFiles": assessment.scanned_files,
                "scanDuration": assessment.scan_duration_seconds,
            }
        }
    
    def _create_tool(self) -> dict:
        """Create SARIF tool object."""
        return {
            "driver": {
                "name": self.TOOL_NAME,
                "version": self.TOOL_VERSION,
                "informationUri": "https://github.com/yourusername/security-scanner",
                "rules": self._create_rules(),
            }
        }
    
    def _create_invocation(self, assessment: RiskAssessment) -> dict:
        """Create SARIF invocation object."""
        return {
            "startTimeUtc": assessment.timestamp.isoformat() + "Z",
            "endTimeUtc": datetime.utcnow().isoformat() + "Z",
            "executionSuccessful": True,
            "properties": {
                "executionDuration": assessment.scan_duration_seconds,
            }
        }
    
    def _create_results(self, assessment: RiskAssessment) -> list:
        """Create SARIF results array."""
        results = []
        
        # Add vulnerability findings
        for finding in assessment.vulnerability_findings:
            results.append(self._create_result_from_finding(finding))
        
        # Add compliance violations
        for violation in assessment.compliance_violations:
            results.append(self._create_result_from_violation(violation))
        
        return results
    
    def _create_result_from_finding(self, finding) -> dict:
        """Create SARIF result from vulnerability finding."""
        level = self._severity_to_level(finding.severity)
        
        result = {
            "ruleId": finding.id,
            "level": level,
            "message": {
                "text": finding.description,
                "markdown": f"**{finding.title}**\n\n{finding.description}",
            },
            "locations": [
                {
                    "physicalLocation": {
                        "fileLocation": {
                            "uri": finding.location.file_path,
                        },
                        "region": {
                            "startLine": finding.location.line_number,
                        }
                    }
                }
            ],
            "properties": {
                "confidence": finding.confidence * 100,
            }
        }
        
        # Add code snippet if available
        if finding.location.line_content:
            result["locations"][0]["physicalLocation"]["region"]["snippet"] = {
                "text": finding.location.line_content,
            }
        
        # Add remediation if available
        if finding.remediation:
            result["fixes"] = [{
                "description": {
                    "text": "Remediation steps",
                },
                "artifactChanges": [{
                    "artifactLocation": {
                        "uri": finding.location.file_path,
                    },
                    "replacements": [{
                        "deletedRegion": {
                            "startLine": finding.location.line_number,
                        },
                        "insertedContent": {
                            "text": finding.remediation,
                        }
                    }]
                }]
            }]
        
        # Add CWE reference
        if finding.cwe_id:
            result["taxa"] = [{
                "id": "CWE",
                "index": self._cwe_to_index(finding.cwe_id),
                "toolComponent": {
                    "name": "CWE"
                }
            }]
        
        return result
    
    def _create_result_from_violation(self, violation) -> dict:
        """Create SARIF result from compliance violation."""
        level = self._severity_to_level(violation.severity)
        
        result = {
            "ruleId": violation.id,
            "level": level,
            "message": {
                "text": violation.violation_description,
                "markdown": (
                    f"**{violation.framework.value.upper()}**\n\n"
                    f"**Requirement:** {violation.requirement}\n\n"
                    f"{violation.violation_description}"
                ),
            },
            "locations": [
                {
                    "physicalLocation": {
                        "fileLocation": {
                            "uri": loc.file_path,
                        },
                        "region": {
                            "startLine": loc.line_number,
                        }
                    }
                } for loc in violation.affected_locations
            ],
            "properties": {
                "framework": violation.framework.value,
                "requirement": violation.requirement,
                "affectedDataCategories": list(violation.affected_data_categories),
            }
        }
        
        # Add remediation
        if violation.remediation_steps:
            result["fixes"] = [{
                "description": {
                    "text": "Remediation steps",
                    "markdown": "\n".join(f"- {step}" for step in violation.remediation_steps),
                },
            }]
        
        return result
    
    def _severity_to_level(self, severity) -> str:
        """Convert severity to SARIF level."""
        severity_map = {
            "Severity.CRITICAL": "error",
            "Severity.HIGH": "error",
            "Severity.MEDIUM": "warning",
            "Severity.LOW": "note",
            "Severity.INFO": "none",
        }
        return severity_map.get(str(severity), "warning")
    
    def _create_rules(self) -> list:
        """Create SARIF rules definitions."""
        return [
            {
                "id": "sql_injection",
                "shortDescription": {
                    "text": "SQL Injection Vulnerability",
                },
                "fullDescription": {
                    "text": "SQL Injection occurs when an attacker is able to manipulate SQL queries "
                            "through user input without proper parameterization.",
                },
                "messageStrings": {
                    "default": {
                        "text": "{0}",
                    }
                },
                "defaultConfiguration": {
                    "level": "error"
                }
            },
            {
                "id": "xss_cross_site_scripting",
                "shortDescription": {
                    "text": "Cross-Site Scripting (XSS) Vulnerability",
                },
                "fullDescription": {
                    "text": "XSS occurs when an attacker injects malicious scripts into web pages "
                            "by exploiting insufficient output encoding.",
                },
                "defaultConfiguration": {
                    "level": "error"
                }
            },
            {
                "id": "exposed_credential",
                "shortDescription": {
                    "text": "Exposed Credential",
                },
                "fullDescription": {
                    "text": "Credentials such as passwords, API keys, or tokens should not be "
                            "hardcoded in source code.",
                },
                "defaultConfiguration": {
                    "level": "error"
                }
            },
            {
                "id": "gdpr_violation",
                "shortDescription": {
                    "text": "GDPR Compliance Violation",
                },
                "fullDescription": {
                    "text": "The code may violate the General Data Protection Regulation (GDPR).",
                },
                "defaultConfiguration": {
                    "level": "error"
                }
            },
            {
                "id": "hipaa_violation",
                "shortDescription": {
                    "text": "HIPAA Compliance Violation",
                },
                "fullDescription": {
                    "text": "The code may violate Health Insurance Portability and Accountability Act (HIPAA).",
                },
                "defaultConfiguration": {
                    "level": "error"
                }
            },
        ]
    
    def _cwe_to_index(self, cwe_id: str) -> int:
        """Extract numeric index from CWE ID."""
        return int(cwe_id.replace("CWE-", ""))
