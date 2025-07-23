"""Data models for analysis reports."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .fastq_data import FASTQMetrics


class ReportFormat(str, Enum):
    """Supported report output formats."""

    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"


class QualityAssessment(str, Enum):
    """Overall quality assessment categories."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAILED = "failed"


class ReportSection(BaseModel):
    """Individual section within a report."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content (HTML/Markdown)")
    charts: List[Dict[str, Any]] = Field(
        default_factory=list, description="Chart data for this section"
    )
    subsections: List["ReportSection"] = Field(
        default_factory=list, description="Nested subsections"
    )


class QualityFlags(BaseModel):
    """Quality flags and warnings for the dataset."""

    low_quality_reads: bool = Field(
        False, description="Significant number of low quality reads"
    )
    uneven_read_lengths: bool = Field(
        False, description="High variation in read lengths"
    )
    poor_gc_content: bool = Field(False, description="GC content outside normal range")
    adapter_contamination: bool = Field(
        False, description="Potential adapter sequences detected"
    )
    overrepresented_sequences: bool = Field(
        False, description="Highly repeated sequences found"
    )
    low_complexity_regions: bool = Field(
        False, description="Regions with low sequence complexity"
    )


class RecommendationItem(BaseModel):
    """Individual recommendation for data processing."""

    category: str = Field(
        ..., description="Category (e.g., 'Quality Filtering', 'Trimming')"
    )
    priority: str = Field(..., description="Priority level: 'high', 'medium', 'low'")
    action: str = Field(..., description="Recommended action to take")
    reason: str = Field(..., description="Explanation of why this is recommended")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Suggested parameter values"
    )


class AnalysisReport(BaseModel):
    """Complete analysis report for a FASTQ file."""

    # Metadata
    report_id: str = Field(..., description="Unique report identifier")
    generated_at: datetime = Field(
        default_factory=datetime.now, description="Report generation timestamp"
    )
    file_path: str = Field(..., description="Path to analyzed FASTQ file")
    file_size_mb: float = Field(..., description="File size in megabytes")

    # Analysis results
    metrics: FASTQMetrics = Field(..., description="Basic FASTQ metrics")
    quality_assessment: QualityAssessment = Field(
        ..., description="Overall quality rating"
    )
    quality_flags: QualityFlags = Field(
        default_factory=QualityFlags, description="Quality warnings and flags"
    )

    # Recommendations
    recommendations: List[RecommendationItem] = Field(
        default_factory=list, description="Processing recommendations"
    )

    # AI Analysis
    ai_summary: str = Field("", description="AI-generated summary of the analysis")
    ai_insights: List[str] = Field(
        default_factory=list, description="Key insights from AI analysis"
    )

    # Charts and visualizations
    chart_data: Dict[str, Any] = Field(
        default_factory=dict, description="Data for generating charts"
    )

    # Report structure
    sections: List[ReportSection] = Field(
        default_factory=list, description="Report sections"
    )

    def add_recommendation(
        self,
        category: str,
        priority: str,
        action: str,
        reason: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a recommendation to the report."""
        recommendation = RecommendationItem(
            category=category,
            priority=priority,
            action=action,
            reason=reason,
            parameters=parameters,
        )
        self.recommendations.append(recommendation)

    def get_high_priority_recommendations(self) -> List[RecommendationItem]:
        """Get only high priority recommendations."""
        return [rec for rec in self.recommendations if rec.priority == "high"]

    def get_recommendations_by_category(
        self, category: str
    ) -> List[RecommendationItem]:
        """Get recommendations for a specific category."""
        return [rec for rec in self.recommendations if rec.category == category]


class ReportTemplate(BaseModel):
    """Template configuration for report generation."""

    name: str = Field(..., description="Template name")
    format: ReportFormat = Field(..., description="Output format")
    template_path: Optional[Path] = Field(None, description="Path to template file")
    include_charts: bool = Field(True, description="Whether to include charts")
    include_raw_data: bool = Field(
        False, description="Whether to include raw data tables"
    )
    style_config: Dict[str, Any] = Field(
        default_factory=dict, description="Styling configuration"
    )


# Update forward reference
ReportSection.model_rebuild()
