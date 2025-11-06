"""Report generation agent for FASTQ analysis."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..models.fastq_data import FASTQData
from ..models.reports import (
    AnalysisReport,
    QualityAssessment,
    QualityFlags,
    RecommendationItem,
    ReportFormat,
    ReportSection,
)
from .base import BaseAgent


class FASTQReportAgent(BaseAgent):
    """Agent responsible for generating comprehensive FASTQ analysis reports."""

    # GC content thresholds
    GC_IDEAL_MIN = 40.0
    GC_IDEAL_MAX = 60.0
    GC_ACCEPTABLE_MIN = 35.0
    GC_ACCEPTABLE_MAX = 65.0

    @staticmethod
    def assess_gc_content(gc_value: float) -> tuple[str, bool]:
        """
        Assess GC content with consistent thresholds.

        Args:
            gc_value: GC content percentage (0-100)

        Returns:
            tuple of (status, should_flag):
            - status: "ideal", "acceptable", or "unusual"
            - should_flag: True if poor_gc_content flag should be set
        """
        if FASTQReportAgent.GC_IDEAL_MIN <= gc_value <= FASTQReportAgent.GC_IDEAL_MAX:
            return "ideal", False
        elif (
            FASTQReportAgent.GC_ACCEPTABLE_MIN
            <= gc_value
            <= FASTQReportAgent.GC_ACCEPTABLE_MAX
        ):
            return "acceptable", False
        else:
            return "unusual", True

    def get_system_prompt(self) -> str:
        return (
            "You are a FASTQ analysis report agent. Your role is to: "
            "1. Analyze FASTQ quality metrics and generate insights "
            "2. Identify quality issues and provide specific recommendations "
            "3. Create clear, actionable summaries for bioinformatics users "
            "4. Suggest appropriate preprocessing steps based on data quality. "
            "Focus on practical, actionable advice that helps users improve "
            "their downstream analysis results."
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        fastq_data = input_data.get("fastq_data")
        output_dir = Path(input_data.get("output_dir", "./reports"))
        report_format = input_data.get("format", ReportFormat.HTML)
        fast_mode = input_data.get("fast_mode", False)

        if not fastq_data:
            raise ValueError("fastq_data is required in input_data")

        self.log(f"Generating {report_format} report for {fastq_data.filename}")
        if fast_mode:
            self.log("Fast mode enabled - skipping detailed AI analysis")

        try:
            # Generate the analysis report
            report = await self._create_analysis_report(fastq_data, fast_mode)

            # Generate charts data
            chart_data = self._generate_chart_data(fastq_data)
            report.chart_data = chart_data

            # Create report sections
            sections = await self._create_report_sections(report)
            report.sections = sections

            # Save the report
            output_path = await self._save_report(report, output_dir, report_format)

            self.log(f"Report generated successfully: {output_path}")

            return {
                "report": report,
                "output_path": str(output_path),
                "status": "success",
                "summary": {
                    "quality_assessment": report.quality_assessment,
                    "total_recommendations": len(report.recommendations),
                    "high_priority_issues": len(
                        report.get_high_priority_recommendations()
                    ),
                },
            }

        except Exception as e:
            self.log(f"Error generating report: {e}", "ERROR")
            return {
                "report": None,
                "output_path": None,
                "status": "error",
                "error_message": str(e),
            }

    async def _create_analysis_report(
        self, fastq_data: FASTQData, fast_mode: bool = False
    ) -> AnalysisReport:
        """Create the core analysis report with AI insights."""

        # Calculate file size (approximate)
        metrics = fastq_data.metrics
        if not metrics:
            # If no metrics, calculate them
            metrics = fastq_data.calculate_metrics()

        file_size_mb = (metrics.total_bases * 4) / (1024 * 1024)  # Rough estimate

        # Assess overall quality first
        quality_assessment = self._assess_overall_quality(metrics)

        # Create base report with required fields
        report = AnalysisReport(
            report_id=str(uuid.uuid4()),
            file_path=fastq_data.filename,
            file_size_mb=round(file_size_mb, 2),
            metrics=metrics,
            quality_assessment=quality_assessment,  # This was missing!
        )

        # Identify quality flags
        report.quality_flags = self._identify_quality_flags(metrics)

        # Generate AI analysis (with performance optimization)
        if fast_mode:
            self.log("Fast mode enabled - using template-based analysis")
            ai_analysis = self._generate_fast_analysis(report)
        elif report.metrics.total_reads < 50:  # Increased threshold
            self.log("Small dataset detected - using fast analysis")
            ai_analysis = self._generate_fast_analysis(report)
        else:
            ai_analysis = await self._generate_ai_analysis(fastq_data, report)

        report.ai_summary = ai_analysis.get("summary", "")
        report.ai_insights = ai_analysis.get("insights", [])

        # Generate recommendations
        recommendations = await self._generate_recommendations(fastq_data, report)
        report.recommendations = recommendations

        return report

    def _assess_overall_quality(self, metrics) -> QualityAssessment:
        """Assess overall quality based on metrics."""
        avg_quality = metrics.average_quality

        if avg_quality >= 35:
            return QualityAssessment.EXCELLENT
        elif avg_quality >= 30:
            return QualityAssessment.GOOD
        elif avg_quality >= 25:
            return QualityAssessment.FAIR
        elif avg_quality >= 20:
            return QualityAssessment.POOR
        else:
            return QualityAssessment.FAILED

    def _identify_quality_flags(self, metrics) -> QualityFlags:
        """Identify quality issues and flags."""
        flags = QualityFlags()

        # Check for low quality reads
        if metrics.average_quality < 25:
            flags.low_quality_reads = True

        # Check for uneven read lengths
        length_variation = metrics.max_read_length - metrics.min_read_length
        if length_variation > 50:
            flags.uneven_read_lengths = True

        # Check GC content using consistent thresholds
        _, should_flag = self.assess_gc_content(metrics.gc_content)
        flags.poor_gc_content = should_flag

        return flags

    def _generate_fast_analysis(self, report: AnalysisReport) -> Dict[str, Any]:
        """Generate analysis without AI for faster processing."""
        metrics = report.metrics

        # Generate template-based summary
        quality_desc = {
            QualityAssessment.EXCELLENT: "exceptional quality with minimal issues",
            QualityAssessment.GOOD: "good quality suitable for most analyses",
            QualityAssessment.FAIR: "acceptable quality with some concerns",
            QualityAssessment.POOR: "poor quality requiring preprocessing",
            QualityAssessment.FAILED: "failed quality checks, significant issues detected",
        }.get(report.quality_assessment, "unknown quality")

        summary = (
            f"This FASTQ dataset contains {metrics.total_reads:,} reads with "
            f"{quality_desc}. Average quality score is {metrics.average_quality:.1f} "
            f"and GC content is {metrics.gc_content:.1f}%."
        )

        # Generate insights based on metrics
        insights = []

        if metrics.average_quality >= 35:
            insights.append(
                "Excellent base call quality indicates reliable sequencing data"
            )
        elif metrics.average_quality >= 25:
            insights.append("Good quality scores suitable for downstream analysis")
        else:
            insights.append("Low quality scores may require filtering or trimming")

        # Use consistent GC content assessment
        gc_status, _ = self.assess_gc_content(metrics.gc_content)
        if gc_status == "ideal":
            insights.append("GC content within ideal range suggests no major bias")
        elif gc_status == "acceptable":
            insights.append(
                f"GC content ({metrics.gc_content:.1f}%) is acceptable but slightly outside ideal range"
            )
        else:
            insights.append(
                f"GC content ({metrics.gc_content:.1f}%) outside typical range may indicate bias or contamination"
            )

        length_var = metrics.max_read_length - metrics.min_read_length
        if length_var <= 5:
            insights.append(
                "Consistent read lengths indicate uniform library preparation"
            )
        elif length_var <= 20:
            insights.append("Moderate read length variation is within acceptable range")
        else:
            insights.append("High read length variation may require length filtering")

        # Add recommendation insight
        if report.recommendations:
            high_priority = len(
                [r for r in report.recommendations if r.priority == "high"]
            )
            if high_priority > 0:
                insights.append(
                    f"{high_priority} high-priority preprocessing steps recommended"
                )
            else:
                insights.append(
                    "Standard preprocessing steps recommended for optimal results"
                )

        # Safely get quality assessment value
        if hasattr(report.quality_assessment, "value"):
            quality_value = report.quality_assessment.value
        else:
            quality_value = str(report.quality_assessment)

        return {
            "summary": summary,
            "insights": insights,
            "suitability": f"Dataset quality rated as {quality_value} - suitable for analysis with appropriate preprocessing",
        }

    async def _generate_ai_analysis(
        self, fastq_data: FASTQData, report: AnalysisReport
    ) -> Dict[str, Any]:
        """Generate AI-powered analysis and insights."""

        # For small datasets, skip AI analysis to improve performance
        if report.metrics.total_reads < 10:
            gc_status, _ = self.assess_gc_content(report.metrics.gc_content)
            gc_description = {
                "ideal": "within ideal range",
                "acceptable": "acceptable but outside ideal range",
                "unusual": "outside typical range",
            }.get(gc_status, "unknown")

            return {
                "summary": f"Small dataset with {report.metrics.total_reads} reads. Quality assessment: {report.quality_assessment.value}. Average quality: {report.metrics.average_quality:.2f}.",
                "insights": [
                    f"Dataset contains {report.metrics.total_reads} reads with average quality {report.metrics.average_quality:.2f}",
                    f"GC content is {report.metrics.gc_content:.1f}%, which is {gc_description}",
                    (
                        f"Read lengths are consistent at {report.metrics.average_read_length:.1f} bp"
                        if report.metrics.max_read_length
                        - report.metrics.min_read_length
                        <= 10
                        else f"Read lengths vary from {report.metrics.min_read_length} to {report.metrics.max_read_length} bp"
                    ),
                ],
                "suitability": f"Suitable for downstream analysis based on {report.quality_assessment.value} quality assessment",
            }

        prompt = f"""Analyze FASTQ data (be concise):

File: {fastq_data.filename}
Reads: {report.metrics.total_reads:,} | Quality: {report.metrics.average_quality:.1f}
GC: {report.metrics.gc_content:.1f}% | Length: {report.metrics.average_read_length:.0f}bp
Assessment: {report.quality_assessment.value}

Flags: {"Low quality" if report.quality_flags.low_quality_reads else ""} {"Uneven lengths" if report.quality_flags.uneven_read_lengths else ""} {"Poor GC" if report.quality_flags.poor_gc_content else ""}

Provide JSON with:
- "summary": 1-2 sentences on data quality
- "insights": array of 2-3 key observations
- "suitability": brief downstream analysis assessment

JSON only, no markdown:"""

        try:
            ai_response = await self.query_llm(prompt)
            # Clean up the response - remove markdown code blocks if present
            cleaned_response = ai_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]  # Remove ```
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```

            # Try to parse as JSON
            try:
                parsed_json = json.loads(cleaned_response.strip())

                # Validate required keys exist
                if all(
                    key in parsed_json for key in ["summary", "insights", "suitability"]
                ):
                    return parsed_json
                else:
                    # Missing keys, create fallback
                    return {
                        "summary": parsed_json.get("summary", cleaned_response),
                        "insights": parsed_json.get("insights", []),
                        "suitability": parsed_json.get(
                            "suitability", "Review recommended"
                        ),
                    }

            except json.JSONDecodeError:
                # If JSON parsing fails, return the response as summary
                return {
                    "summary": cleaned_response,
                    "insights": [],
                    "suitability": "Analysis available in summary",
                }
        except Exception as e:
            self.log(f"AI analysis failed: {e}", "WARNING")
            return {
                "summary": "AI analysis unavailable",
                "insights": [],
                "suitability": "Manual review recommended",
            }

    async def _generate_recommendations(
        self, fastq_data: FASTQData, report: AnalysisReport
    ) -> List:
        """Generate processing recommendations based on analysis."""

        recommendations = []
        metrics = report.metrics
        flags = report.quality_flags

        # Quality-based recommendations
        if flags.low_quality_reads:
            recommendations.append(
                {
                    "category": "Quality Filtering",
                    "priority": "high",
                    "action": "Apply quality filtering",
                    "reason": f"Average quality score ({metrics.average_quality:.1f}) is below recommended threshold (>25)",
                    "parameters": {
                        "min_quality": 20,
                        "min_length": int(metrics.average_read_length * 0.8),
                    },
                }
            )

        # Length-based recommendations
        if flags.uneven_read_lengths:
            recommendations.append(
                {
                    "category": "Length Filtering",
                    "priority": "medium",
                    "action": "Apply length filtering",
                    "reason": f"Read lengths vary significantly ({metrics.min_read_length}-{metrics.max_read_length} bp)",
                    "parameters": {
                        "min_length": metrics.min_read_length + 10,
                        "max_length": metrics.max_read_length - 10,
                    },
                }
            )

        # GC content recommendations
        if flags.poor_gc_content:
            # Determine priority based on severity
            priority = (
                "high"
                if metrics.gc_content < 30 or metrics.gc_content > 70
                else "medium"
            )
            recommendations.append(
                {
                    "category": "Contamination Check",
                    "priority": priority,
                    "action": "Screen for contamination",
                    "reason": f"GC content ({metrics.gc_content:.1f}%) is outside acceptable range ({self.GC_ACCEPTABLE_MIN}-{self.GC_ACCEPTABLE_MAX}%). Ideal range is {self.GC_IDEAL_MIN}-{self.GC_IDEAL_MAX}%",
                    "parameters": {
                        "ideal_gc_range": [self.GC_IDEAL_MIN, self.GC_IDEAL_MAX],
                        "acceptable_gc_range": [
                            self.GC_ACCEPTABLE_MIN,
                            self.GC_ACCEPTABLE_MAX,
                        ],
                    },
                }
            )

        # Always recommend adapter trimming for Illumina data
        if metrics.average_read_length > 50:  # Likely Illumina data
            recommendations.append(
                {
                    "category": "Adapter Trimming",
                    "priority": "medium",
                    "action": "Trim adapter sequences",
                    "reason": "Standard preprocessing step for Illumina sequencing data",
                    "parameters": {
                        "tool": "trimmomatic",
                        "adapter_file": "TruSeq3-PE.fa",
                    },
                }
            )

        # Convert to RecommendationItem objects
        return [RecommendationItem(**rec) for rec in recommendations]

    def _generate_chart_data(self, fastq_data: FASTQData) -> Dict[str, Any]:
        """Generate data for charts and visualizations."""
        metrics = fastq_data.metrics
        if not metrics:
            metrics = fastq_data.calculate_metrics()

        # Quality distribution chart
        quality_chart = {
            "type": "bar",
            "title": "Quality Score Distribution",
            "data": {
                "labels": list(metrics.quality_distribution.keys()),
                "values": list(metrics.quality_distribution.values()),
            },
        }

        # Length distribution chart
        length_chart = {
            "type": "histogram",
            "title": "Read Length Distribution",
            "data": {
                "labels": list(metrics.length_distribution.keys()),
                "values": list(metrics.length_distribution.values()),
            },
        }

        # Summary metrics chart
        summary_chart = {
            "type": "metrics",
            "title": "Summary Statistics",
            "data": {
                "Total Reads": f"{metrics.total_reads:,}",
                "Total Bases": f"{metrics.total_bases:,}",
                "Avg Quality": f"{metrics.average_quality:.2f}",
                "GC Content": f"{metrics.gc_content:.1f}%",
                "Avg Length": f"{metrics.average_read_length:.1f} bp",
            },
        }

        return {
            "quality_distribution": quality_chart,
            "length_distribution": length_chart,
            "summary_metrics": summary_chart,
        }

    async def _create_report_sections(
        self, report: AnalysisReport
    ) -> List[ReportSection]:
        """Create structured report sections."""

        sections = []

        # Executive Summary
        sections.append(
            ReportSection(
                title="Executive Summary",
                content=f"""
            <div class="summary-section">
                <h3>Quality Assessment: {report.quality_assessment.value.title()}</h3>
                <p>{report.ai_summary}</p>
                <p><strong>Recommendations:</strong> {len(report.recommendations)} processing steps suggested,
                   {len(report.get_high_priority_recommendations())} high priority.</p>
            </div>
            """,
            )
        )

        # Dataset Overview
        sections.append(
            ReportSection(
                title="Dataset Overview",
                content=f"""
            <div class="overview-section">
                <table class="metrics-table">
                    <tr><td>File</td><td>{Path(report.file_path).name}</td></tr>
                    <tr><td>Total Reads</td><td>{report.metrics.total_reads:,}</td></tr>
                    <tr><td>Total Bases</td><td>{report.metrics.total_bases:,}</td></tr>
                    <tr><td>File Size</td><td>{report.file_size_mb:.1f} MB</td></tr>
                    <tr><td>Average Quality</td><td>{report.metrics.average_quality:.2f}</td></tr>
                    <tr><td>GC Content</td><td>{report.metrics.gc_content:.1f}%</td></tr>
                </table>
            </div>
            """,
                charts=[report.chart_data["summary_metrics"]],
            )
        )

        # Quality Analysis
        sections.append(
            ReportSection(
                title="Quality Analysis",
                content=self._create_quality_section_content(report),
                charts=[report.chart_data["quality_distribution"]],
            )
        )

        # Recommendations
        if report.recommendations:
            sections.append(
                ReportSection(
                    title="Processing Recommendations",
                    content=self._create_recommendations_content(
                        report.recommendations
                    ),
                )
            )

        return sections

    def _create_quality_section_content(self, report: AnalysisReport) -> str:
        """Create content for quality analysis section."""
        flags = report.quality_flags

        issues = []
        if flags.low_quality_reads:
            issues.append("Low quality reads detected")
        if flags.uneven_read_lengths:
            issues.append("Uneven read length distribution")
        if flags.poor_gc_content:
            issues.append("GC content outside normal range")

        if issues:
            issues_html = (
                "<ul>" + "".join(f"<li>{issue}</li>" for issue in issues) + "</ul>"
            )
        else:
            issues_html = "<p>No significant quality issues detected.</p>"

        return f"""
        <div class="quality-section">
            <h4>Quality Issues:</h4>
            {issues_html}

            <h4>Quality Metrics:</h4>
            <ul>
                <li>Average Quality Score: {report.metrics.average_quality:.2f}</li>
                <li>Read Length Range: {report.metrics.min_read_length}-{report.metrics.max_read_length} bp</li>
                <li>GC Content: {report.metrics.gc_content:.1f}%</li>
            </ul>
        </div>
        """

    def _create_recommendations_content(self, recommendations) -> str:
        """Create content for recommendations section."""

        high_priority = [r for r in recommendations if r.priority == "high"]
        medium_priority = [r for r in recommendations if r.priority == "medium"]

        content = "<div class='recommendations-section'>"

        if high_priority:
            content += "<h4>High Priority Actions:</h4><ul>"
            for rec in high_priority:
                content += f"<li><strong>{rec.action}</strong>: {rec.reason}</li>"
            content += "</ul>"

        if medium_priority:
            content += "<h4>Recommended Actions:</h4><ul>"
            for rec in medium_priority:
                content += f"<li><strong>{rec.action}</strong>: {rec.reason}</li>"
            content += "</ul>"

        content += "</div>"
        return content

    async def _save_report(
        self, report: AnalysisReport, output_dir: Path, format: ReportFormat
    ) -> Path:
        """Save the report in the specified format."""

        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Handle format safely - could be string or enum
        format_str = format.value if hasattr(format, "value") else str(format)
        filename = f"fastq_analysis_{timestamp}.{format_str}"

        output_path = output_dir / filename

        if format == ReportFormat.HTML or format_str == "html":
            await self._save_html_report(report, output_path)
        elif format == ReportFormat.JSON or format_str == "json":
            await self._save_json_report(report, output_path)
        elif format == ReportFormat.MARKDOWN or format_str == "markdown":
            await self._save_markdown_report(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_path

    async def _save_html_report(
        self, report: AnalysisReport, output_path: Path
    ) -> None:
        """Save report as HTML using Jinja2 template."""
        try:
            from jinja2 import BaseLoader, Environment, Template

            # For now, use the embedded template to avoid file path issues
            template_content = self._get_embedded_html_template()

            # Create Jinja2 environment
            env = Environment(loader=BaseLoader())

            # Create template from string
            template = env.from_string(template_content)

            # Prepare template variables with safe quality assessment
            quality_value = (
                report.quality_assessment.value
                if hasattr(report.quality_assessment, "value")
                else str(report.quality_assessment)
            )

            # Render template with version from package metadata
            from .. import __version__

            html_content = template.render(
                report=report, quality_value=quality_value, version=__version__
            )

            output_path.write_text(html_content, encoding="utf-8")

        except ImportError:
            # Fallback to simple HTML if Jinja2 is not available
            await self._save_simple_html_report(report, output_path)
        except Exception as e:
            # If template rendering fails, use simple HTML
            self.log(f"Template rendering failed: {e}, using simple HTML", "WARNING")
            await self._save_simple_html_report(report, output_path)

    def _get_embedded_html_template(self) -> str:
        """Get embedded HTML template as fallback."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>FASTQ Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    margin-bottom: 30px;
                    border-radius: 10px;
                }
                .section {
                    background: white;
                    margin-bottom: 30px;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .metrics-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .metrics-table td { padding: 12px; border-bottom: 1px solid #ddd; }
                .metrics-table th { background: #f8f9fa; padding: 12px; font-weight: bold; }
                .quality-excellent { color: green; font-weight: bold; }
                .quality-good { color: darkgreen; font-weight: bold; }
                .quality-fair { color: orange; font-weight: bold; }
                .quality-poor { color: red; font-weight: bold; }
                .quality-failed { color: darkred; font-weight: bold; }
                .recommendations { list-style: none; padding: 0; }
                .recommendation {
                    background: #f8f9fa;
                    margin-bottom: 15px;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }
                .recommendation.high-priority { border-left-color: #dc3545; }
                .recommendation.medium-priority { border-left-color: #ffc107; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧬 FASTQ Analysis Report</h1>
                <p>Quality Assessment: <span class="quality-{{quality_value}}">{{quality_value | title}}</span></p>
                <p>Generated: {{report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}}</p>
            </div>

            <div class="section">
                <h2>📋 Summary</h2>
                <p>{{report.ai_summary}}</p>
            </div>

            <div class="section">
                <h2>📊 Dataset Overview</h2>
                <table class="metrics-table">
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Reads</td><td>{{"{:,}".format(report.metrics.total_reads)}}</td></tr>
                    <tr><td>Total Bases</td><td>{{"{:,}".format(report.metrics.total_bases)}}</td></tr>
                    <tr><td>Average Quality</td><td>{{"{:.2f}".format(report.metrics.average_quality)}}</td></tr>
                    <tr><td>GC Content</td><td>{{"{:.1f}%".format(report.metrics.gc_content)}}</td></tr>
                    <tr><td>Average Length</td><td>{{"{:.1f} bp".format(report.metrics.average_read_length)}}</td></tr>
                    <tr><td>File Size</td><td>{{"{:.1f} MB".format(report.file_size_mb)}}</td></tr>
                </table>
            </div>

            {% if report.recommendations %}
            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul class="recommendations">
                    {% for rec in report.recommendations %}
                    <li class="recommendation {{rec.priority}}-priority">
                        <strong>{{rec.action}}</strong> ({{rec.priority}} priority)
                        <br><em>{{rec.reason}}</em>
                    </li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}

            <div style="text-align: center; margin-top: 50px; color: #666;">
                <p>Generated by FASTQ Agent System</p>
                <p>Report ID: {{report.report_id}}</p>
            </div>
        </body>
        </html>
        """

    async def _save_simple_html_report(
        self, report: AnalysisReport, output_path: Path
    ) -> None:
        """Save simple HTML report without Jinja2."""

        recommendations_html = ""
        if report.recommendations:
            recommendations_html = "<h2>💡 Recommendations</h2><ul>"
            for rec in report.recommendations:
                recommendations_html += f"<li><strong>{rec.action}</strong> ({rec.priority}): {rec.reason}</li>"
            recommendations_html += "</ul>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FASTQ Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; padding: 20px; border-left: 4px solid #3498db; }}
                .metrics-table {{ width: 100%; border-collapse: collapse; }}
                .metrics-table td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .quality-{report.quality_assessment.value} {{
                    color: {'green' if report.quality_assessment.value in ['excellent', 'good'] else 'orange' if report.quality_assessment.value == 'fair' else 'red'};
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧬 FASTQ Analysis Report</h1>
                <p>Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Quality Assessment: <span class="quality-{report.quality_assessment.value}">{report.quality_assessment.value.title()}</span></p>
            </div>

            <div class="section">
                <h2>📋 Summary</h2>
                <p>{report.ai_summary}</p>
            </div>

            <div class="section">
                <h2>📊 Dataset Overview</h2>
                <table class="metrics-table">
                    <tr><td>File</td><td>{Path(report.file_path).name}</td></tr>
                    <tr><td>Total Reads</td><td>{report.metrics.total_reads:,}</td></tr>
                    <tr><td>Total Bases</td><td>{report.metrics.total_bases:,}</td></tr>
                    <tr><td>Average Quality</td><td>{report.metrics.average_quality:.2f}</td></tr>
                    <tr><td>GC Content</td><td>{report.metrics.gc_content:.1f}%</td></tr>
                </table>
            </div>

            <div class="section">
                {recommendations_html}
            </div>
        </body>
        </html>
        """

        output_path.write_text(html_content, encoding="utf-8")

    async def _save_json_report(
        self, report: AnalysisReport, output_path: Path
    ) -> None:
        """Save report as JSON."""
        # Convert to dict and handle datetime serialization
        report_dict = report.model_dump()
        report_dict["generated_at"] = report.generated_at.isoformat()

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

    async def _save_markdown_report(
        self, report: AnalysisReport, output_path: Path
    ) -> None:
        """Save report as Markdown."""

        md_content = f"""# FASTQ Analysis Report

**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
**File:** {Path(report.file_path).name}
**Quality Assessment:** {report.quality_assessment.value.title()}

## Summary

{report.ai_summary}

## Dataset Overview

| Metric | Value |
|--------|-------|
| Total Reads | {report.metrics.total_reads:,} |
| Total Bases | {report.metrics.total_bases:,} |
| Average Quality | {report.metrics.average_quality:.2f} |
| GC Content | {report.metrics.gc_content:.1f}% |
| Average Length | {report.metrics.average_read_length:.1f} bp |

## Recommendations

"""

        for rec in report.recommendations:
            md_content += f"### {rec.category} ({rec.priority.title()} Priority)\n\n"
            md_content += f"**Action:** {rec.action}\n\n"
            md_content += f"**Reason:** {rec.reason}\n\n"

        output_path.write_text(md_content, encoding="utf-8")
