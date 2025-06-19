"""Data models for FASTQ file analysis."""

import statistics
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class FASTQRead(BaseModel):
    """Represents a single read from a FASTQ file."""

    identifier: str = Field(..., description="Read identifier (header line)")
    sequence: str = Field(..., description="DNA/RNA sequence")
    quality_scores: List[int] = Field(..., description="Phred quality scores")

    @property
    def length(self) -> int:
        """Length of the sequence."""
        return len(self.sequence)

    @property
    def average_quality(self) -> float:
        """Average quality score for this read."""
        return statistics.mean(self.quality_scores) if self.quality_scores else 0.0

    @property
    def min_quality(self) -> int:
        """Minimum quality score in this read."""
        return min(self.quality_scores) if self.quality_scores else 0

    @property
    def gc_content(self) -> float:
        """GC content percentage."""
        if not self.sequence:
            return 0.0
        gc_count = self.sequence.upper().count("G") + self.sequence.upper().count("C")
        return (gc_count / len(self.sequence)) * 100


class FASTQMetrics(BaseModel):
    """Summary metrics for a FASTQ file."""

    total_reads: int = Field(..., description="Total number of reads")
    total_bases: int = Field(..., description="Total number of bases")
    average_read_length: float = Field(..., description="Average read length")
    min_read_length: int = Field(..., description="Minimum read length")
    max_read_length: int = Field(..., description="Maximum read length")
    average_quality: float = Field(
        ..., description="Average quality score across all reads"
    )
    gc_content: float = Field(..., description="Overall GC content percentage")
    quality_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Quality score distribution"
    )
    length_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Read length distribution"
    )


class FASTQData(BaseModel):
    """Complete FASTQ file data and metrics."""

    filename: str = Field(..., description="Original filename")
    reads: List[FASTQRead] = Field(default_factory=list, description="Individual reads")
    metrics: Optional[FASTQMetrics] = Field(None, description="Summary metrics")

    def calculate_metrics(self) -> FASTQMetrics:
        """Calculate summary metrics from reads."""
        if not self.reads:
            return FASTQMetrics(
                total_reads=0,
                total_bases=0,
                average_read_length=0.0,
                min_read_length=0,
                max_read_length=0,
                average_quality=0.0,
                gc_content=0.0,
            )

        lengths = [read.length for read in self.reads]
        qualities = [read.average_quality for read in self.reads]

        # Quality distribution (binned)
        quality_bins: Dict[str, int] = {}
        for read in self.reads:
            for score in read.quality_scores:
                bin_key = f"{(score // 5) * 5}-{(score // 5) * 5 + 4}"
                quality_bins[bin_key] = quality_bins.get(bin_key, 0) + 1

        # Length distribution (binned)
        length_bins: Dict[str, int] = {}
        for length in lengths:
            bin_key = f"{(length // 50) * 50}-{(length // 50) * 50 + 49}"
            length_bins[bin_key] = length_bins.get(bin_key, 0) + 1

        self.metrics = FASTQMetrics(
            total_reads=len(self.reads),
            total_bases=sum(lengths),
            average_read_length=statistics.mean(lengths),
            min_read_length=min(lengths),
            max_read_length=max(lengths),
            average_quality=statistics.mean(qualities),
            gc_content=statistics.mean([read.gc_content for read in self.reads]),
            quality_distribution=quality_bins,
            length_distribution=length_bins,
        )

        return self.metrics
