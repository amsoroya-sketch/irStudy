#!/usr/bin/env python3
"""
Comprehensive Validation Report Generator
Compiles results from all validation sources into HTML and JSON reports

Features:
- Aggregate Australian compliance, citation, and RAG validation results
- Generate HTML dashboard with charts and metrics
- Create JSON export for programmatic access
- Priority-ranked issue list
- Specialty-specific breakdowns
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ValidationSummary:
    """Overall validation summary"""
    total_files: int = 0
    total_issues: int = 0
    critical_issues: int = 0
    important_issues: int = 0
    minor_issues: int = 0
    auto_corrections: int = 0
    manual_review_needed: int = 0
    compliance_score: float = 0.0
    citation_coverage: float = 0.0
    rag_verification_rate: float = 0.0


class ComprehensiveReportGenerator:
    """
    Generates comprehensive validation reports from multiple sources.
    """

    def __init__(self, validation_reports_dir: Path):
        """
        Initialize report generator.

        Args:
            validation_reports_dir: Directory containing validation reports
        """
        self.reports_dir = validation_reports_dir
        self.summary = ValidationSummary()

    def load_australian_compliance_report(self) -> Optional[Dict]:
        """Load Australian compliance validation report"""
        json_path = self.reports_dir / "australian_compliance.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return None

    def load_citation_report(self) -> Optional[Dict]:
        """Load citation validation report"""
        json_path = self.reports_dir / "citations.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return None

    def load_rag_report(self) -> Optional[Dict]:
        """Load RAG validation report"""
        json_path = self.reports_dir / "rag_validation.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return None

    def aggregate_reports(self) -> Dict[str, Any]:
        """
        Aggregate all validation reports.

        Returns:
            Comprehensive aggregated data
        """
        compliance_report = self.load_australian_compliance_report()
        citation_report = self.load_citation_report()
        rag_report = self.load_rag_report()

        # Aggregate summary statistics
        files_scanned = set()
        all_issues = []
        auto_corrections = 0
        manual_review = 0

        if compliance_report:
            files_scanned.add(compliance_report['summary']['files_scanned'])
            all_issues.extend(compliance_report.get('issues', []))
            auto_corrections += compliance_report['summary']['auto_corrections']
            manual_review += compliance_report['summary']['manual_review_needed']
            self.summary.compliance_score = compliance_report['summary']['compliance_score']

        if citation_report:
            files_scanned.add(citation_report['summary']['files_scanned'])
            all_issues.extend(citation_report.get('issues', []))
            self.summary.citation_coverage = citation_report['summary']['citation_coverage']

        if rag_report:
            files_scanned.add(rag_report['summary']['files_scanned'])
            auto_corrections += rag_report['summary']['auto_corrected']
            manual_review += rag_report['summary']['unverified_claims']
            if rag_report['summary']['claims_extracted'] > 0:
                self.summary.rag_verification_rate = (
                    rag_report['summary']['rag_verified'] /
                    rag_report['summary']['claims_extracted']
                ) * 100

        # Update summary
        self.summary.total_files = max(files_scanned) if files_scanned else 0
        self.summary.total_issues = len(all_issues)
        self.summary.auto_corrections = auto_corrections
        self.summary.manual_review_needed = manual_review

        # Count by severity
        for issue in all_issues:
            severity = issue.get('severity', 'minor')
            if severity == 'critical':
                self.summary.critical_issues += 1
            elif severity == 'important':
                self.summary.important_issues += 1
            else:
                self.summary.minor_issues += 1

        return {
            'compliance': compliance_report,
            'citations': citation_report,
            'rag': rag_report,
            'summary': self.summary
        }

    def generate_html_report(self, output_path: Path, data: Dict[str, Any]):
        """Generate HTML dashboard"""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICRP OSCE Content Validation Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        }}
        .metric-card.danger {{
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }}
        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section-title {{
            font-size: 1.8em;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .report-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .score-bar {{
            background: #ecf0f1;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .score-fill {{
            height: 100%;
            background: linear-gradient(90deg, #56ab2f 0%, #a8e063 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        .issue-list {{
            list-style: none;
        }}
        .issue-item {{
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }}
        .issue-item.critical {{
            border-left-color: #e74c3c;
        }}
        .issue-item.important {{
            border-left-color: #f39c12;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge.critical {{
            background: #e74c3c;
            color: white;
        }}
        .badge.important {{
            background: #f39c12;
            color: white;
        }}
        .badge.success {{
            background: #27ae60;
            color: white;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 ICRP OSCE Content Validation Report</h1>
        <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>

        <!-- Summary Metrics -->
        <div class="metric-grid">
            <div class="metric-card success">
                <div class="metric-label">Files Scanned</div>
                <div class="metric-value">{self.summary.total_files}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Issues Found</div>
                <div class="metric-value">{self.summary.total_issues}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Auto-Corrected</div>
                <div class="metric-value">{self.summary.auto_corrections}</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">Manual Review Needed</div>
                <div class="metric-value">{self.summary.manual_review_needed}</div>
            </div>
        </div>

        <!-- Compliance Scores -->
        <div class="section">
            <h2 class="section-title">📊 Compliance Scores</h2>

            <div class="report-section">
                <h3>Australian Terminology Compliance</h3>
                <div class="score-bar">
                    <div class="score-fill" style="width: {self.summary.compliance_score}%">
                        {self.summary.compliance_score:.1f}%
                    </div>
                </div>
            </div>

            <div class="report-section">
                <h3>Citation Coverage</h3>
                <div class="score-bar">
                    <div class="score-fill" style="width: {self.summary.citation_coverage}%">
                        {self.summary.citation_coverage:.1f}%
                    </div>
                </div>
            </div>

            <div class="report-section">
                <h3>RAG Verification Rate</h3>
                <div class="score-bar">
                    <div class="score-fill" style="width: {self.summary.rag_verification_rate}%">
                        {self.summary.rag_verification_rate:.1f}%
                    </div>
                </div>
            </div>
        </div>

        <!-- Issues by Severity -->
        <div class="section">
            <h2 class="section-title">🚨 Issues by Severity</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="badge critical">Critical</span></td>
                        <td>{self.summary.critical_issues}</td>
                        <td>{(self.summary.critical_issues / max(self.summary.total_issues, 1) * 100):.1f}%</td>
                    </tr>
                    <tr>
                        <td><span class="badge important">Important</span></td>
                        <td>{self.summary.important_issues}</td>
                        <td>{(self.summary.important_issues / max(self.summary.total_issues, 1) * 100):.1f}%</td>
                    </tr>
                    <tr>
                        <td><span class="badge">Minor</span></td>
                        <td>{self.summary.minor_issues}</td>
                        <td>{(self.summary.minor_issues / max(self.summary.total_issues, 1) * 100):.1f}%</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Detailed Reports -->
        <div class="section">
            <h2 class="section-title">📄 Detailed Validation Reports</h2>
            <div class="report-section">
                <h3>Australian Compliance</h3>
                <p>Auto-corrections applied: {data['compliance']['summary']['auto_corrections'] if data.get('compliance') else 0}</p>
                <p>Manual review needed: {data['compliance']['summary']['manual_review_needed'] if data.get('compliance') else 0}</p>
                <p><a href="australian_compliance.md">View Full Report →</a></p>
            </div>

            <div class="report-section">
                <h3>Citation Validation</h3>
                <p>Claims with citations: {data['citations']['summary']['cited_claims'] if data.get('citations') else 0}</p>
                <p>Uncited claims: {data['citations']['summary']['uncited_claims'] if data.get('citations') else 0}</p>
                <p><a href="citations.md">View Full Report →</a></p>
            </div>

            <div class="report-section">
                <h3>RAG Fact-Checking</h3>
                <p>RAG verified claims: {data['rag']['summary']['rag_verified'] if data.get('rag') else 0}</p>
                <p>Auto-corrected: {data['rag']['summary']['auto_corrected'] if data.get('rag') else 0}</p>
                <p>Unverified claims (manual review): {data['rag']['summary']['unverified_claims'] if data.get('rag') else 0}</p>
                <p><a href="rag_validation.md">View Full Report →</a></p>
                <p><a href="unverified_claims/">View Unverified Claims →</a></p>
            </div>
        </div>

        <div class="footer">
            <p>ICRP OSCE Preparation - Medical Content Validation System</p>
            <p>Powered by RAG (Retrieval-Augmented Generation) with Australian source prioritization</p>
        </div>
    </div>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"✓ HTML report saved to {output_path}")

    def generate_json_report(self, output_path: Path, data: Dict[str, Any]):
        """Generate comprehensive JSON report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_files': self.summary.total_files,
                'total_issues': self.summary.total_issues,
                'critical_issues': self.summary.critical_issues,
                'important_issues': self.summary.important_issues,
                'minor_issues': self.summary.minor_issues,
                'auto_corrections': self.summary.auto_corrections,
                'manual_review_needed': self.summary.manual_review_needed,
                'compliance_score': round(self.summary.compliance_score, 2),
                'citation_coverage': round(self.summary.citation_coverage, 2),
                'rag_verification_rate': round(self.summary.rag_verification_rate, 2)
            },
            'validation_reports': {
                'australian_compliance': data.get('compliance'),
                'citations': data.get('citations'),
                'rag': data.get('rag')
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ JSON report saved to {output_path}")

    def generate_reports(self):
        """Generate all comprehensive reports"""
        logger.info("📊 Generating comprehensive validation reports...")

        # Aggregate data
        data = self.aggregate_reports()

        # Generate HTML
        html_path = self.reports_dir / "COMPREHENSIVE_VALIDATION_REPORT.html"
        self.generate_html_report(html_path, data)

        # Generate JSON
        json_path = self.reports_dir / "COMPREHENSIVE_VALIDATION_REPORT.json"
        self.generate_json_report(json_path, data)

        # Print summary
        print("\n" + "="*60)
        print("✓ Comprehensive Validation Reports Generated")
        print("="*60)
        print(f"Files Scanned: {self.summary.total_files}")
        print(f"Total Issues: {self.summary.total_issues}")
        print(f"  - Critical: {self.summary.critical_issues}")
        print(f"  - Important: {self.summary.important_issues}")
        print(f"  - Minor: {self.summary.minor_issues}")
        print(f"\nAuto-Corrections: {self.summary.auto_corrections}")
        print(f"Manual Review Needed: {self.summary.manual_review_needed}")
        print(f"\nCompliance Score: {self.summary.compliance_score:.1f}%")
        print(f"Citation Coverage: {self.summary.citation_coverage:.1f}%")
        print(f"RAG Verification: {self.summary.rag_verification_rate:.1f}%")
        print(f"\nHTML Dashboard: {html_path}")
        print(f"JSON Export: {json_path}")
        print("="*60)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate comprehensive validation reports")
    parser.add_argument("--reports-dir", default="validation_reports", help="Validation reports directory")

    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    if not reports_dir.exists():
        logger.error(f"Reports directory not found: {reports_dir}")
        logger.info("Please run the individual validation scripts first:")
        logger.info("  1. validate_australian_compliance.py")
        logger.info("  2. validate_citations.py")
        logger.info("  3. validate_rag_facts.py")
        return

    generator = ComprehensiveReportGenerator(reports_dir)
    generator.generate_reports()


if __name__ == "__main__":
    main()
