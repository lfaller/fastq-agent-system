"""FASTQ file parser agent."""

import gzip
from pathlib import Path
from typing import Any, Dict, List, Union

from Bio import SeqIO

from ..models.fastq_data import FASTQData, FASTQRead
from .base import BaseAgent


class FASTQParserAgent(BaseAgent):
    """Agent responsible for parsing FASTQ files and extracting basic metrics."""

    def get_system_prompt(self) -> str:
        return (
            "You are a FASTQ file parser agent. Your role is to: "
            "1. Parse FASTQ files accurately "
            "2. Extract sequence and quality information "
            "3. Identify potential file format issues "
            "4. Provide basic statistics about the parsed data. "
            "You should be thorough but efficient, and flag any unusual "
            "patterns you notice."
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a FASTQ file and return parsed data with metrics."""
        file_path = input_data.get("file_path")
        fast_mode = input_data.get("fast_mode", False)

        if not file_path:
            raise ValueError("file_path is required in input_data")

        self.log(f"Starting to parse FASTQ file: {file_path}")

        try:
            # Parse the FASTQ file
            fastq_data = self._parse_fastq_file(file_path)

            # Calculate metrics
            metrics = fastq_data.calculate_metrics()

            # Use LLM to analyze the basic statistics and flag issues (unless fast mode)
            if fast_mode or metrics.total_reads < 50:
                # Skip AI analysis for small datasets or fast mode
                llm_analysis = f"Successfully parsed {metrics.total_reads} reads. Average quality: {metrics.average_quality:.2f}. No detailed analysis in fast mode."
                self.log("Skipping AI analysis for fast processing")
            else:
                # Use LLM to analyze the basic statistics and flag issues
                analysis_prompt = self._create_analysis_prompt(fastq_data)
                llm_analysis = await self.query_llm(analysis_prompt)

            self.log(f"Successfully parsed {metrics.total_reads} reads")

            return {
                "fastq_data": fastq_data,
                "parsing_status": "success",
                "llm_analysis": llm_analysis,
                "summary": {
                    "total_reads": metrics.total_reads,
                    "average_quality": round(metrics.average_quality, 2),
                    "average_length": round(metrics.average_read_length, 2),
                    "gc_content": round(metrics.gc_content, 2),
                },
            }

        except Exception as e:
            self.log(f"Error parsing FASTQ file: {e}", "ERROR")
            return {
                "fastq_data": None,
                "parsing_status": "error",
                "error_message": str(e),
                "llm_analysis": None,
            }

    def _parse_fastq_file(self, file_path: Union[str, Path]) -> FASTQData:
        """Parse a FASTQ file using BioPython."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"FASTQ file not found: {file_path}")

        # Determine if file is gzipped
        is_gzipped = file_path.suffix.lower() == ".gz"

        reads = []

        try:
            if is_gzipped:
                with gzip.open(file_path, "rt") as handle:
                    records = SeqIO.parse(handle, "fastq")
                    reads = self._convert_biopython_records(records)
            else:
                with open(file_path, "r") as handle:
                    records = SeqIO.parse(handle, "fastq")
                    reads = self._convert_biopython_records(records)

        except Exception as e:
            raise ValueError(f"Error parsing FASTQ file: {e}")

        if not reads:
            raise ValueError("No valid FASTQ reads found in file")

        return FASTQData(filename=str(file_path), reads=reads)

    def _convert_biopython_records(self, records) -> List[FASTQRead]:
        """Convert BioPython SeqRecord objects to FASTQRead objects."""
        fastq_reads = []

        for record in records:
            # Convert Phred quality scores to integers
            quality_scores = record.letter_annotations.get("phred_quality", [])

            fastq_read = FASTQRead(
                identifier=record.id,
                sequence=str(record.seq),
                quality_scores=quality_scores,
            )
            fastq_reads.append(fastq_read)

        return fastq_reads

    def _create_analysis_prompt(self, fastq_data: FASTQData) -> str:
        """Create a prompt for LLM analysis of parsed FASTQ data."""
        metrics = fastq_data.metrics
        if not metrics:
            return "No metrics available for analysis."

        return f"""Analyze this FASTQ file parsing result and provide insights:

File: {fastq_data.filename}
Total reads: {metrics.total_reads:,}
Total bases: {metrics.total_bases:,}
Average read length: {metrics.average_read_length:.1f} bp
Read length range: {metrics.min_read_length} - {metrics.max_read_length} bp
Average quality score: {metrics.average_quality:.2f}
GC content: {metrics.gc_content:.1f}%

Quality distribution (top 5):
{self._format_distribution(metrics.quality_distribution, 5)}

Length distribution (top 5):
{self._format_distribution(metrics.length_distribution, 5)}

Based on these metrics, please provide:
1. Assessment of data quality (good/fair/poor and why)
2. Any unusual patterns or potential issues
3. Brief recommendations for downstream analysis
4. Any red flags that need attention

Keep your response concise but informative."""

    def _format_distribution(self, distribution: Dict[str, int], top_n: int) -> str:
        """Format distribution data for display."""
        if not distribution:
            return "No distribution data available"

        sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        top_items = sorted_items[:top_n]

        formatted = []
        for range_str, count in top_items:
            formatted.append(f"  {range_str}: {count:,}")

        return "\n".join(formatted)
