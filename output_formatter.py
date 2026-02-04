"""Module for formatting and saving results in multiple formats."""

import os
import json
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER


class OutputFormatter:
    """Handles saving results in multiple formats."""

    def __init__(self, base_output_dir: str = "outputs"):
        """Initialize the output formatter.

        Args:
            base_output_dir: Base directory for all outputs
        """
        self.base_output_dir = base_output_dir
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = os.path.join(base_output_dir, f"run_{self.run_timestamp}")

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

    def save_all_formats(self, results: Dict[str, dict], metadata: dict = None) -> dict:
        """Save results in JSON and PDF formats, plus prompts file.

        Args:
            results: Dictionary mapping questions to dict with 'answer', 'chunks', and 'prompt'
            metadata: Optional metadata about the run (e.g., transcripts used)

        Returns:
            Dictionary of file paths created
        """
        file_paths = {}

        # Save JSON
        file_paths['json'] = self._save_json(results, metadata)

        # Save PDF with chunks
        file_paths['pdf_with_chunks'] = self._save_pdf(results, metadata, include_chunks=True)

        # Save PDF without chunks (answers only)
        file_paths['pdf_answers_only'] = self._save_pdf(results, metadata, include_chunks=False)

        # Save prompts file
        file_paths['prompts'] = self._save_prompts(results)

        # Save metadata file
        file_paths['metadata'] = self._save_metadata(metadata)

        return file_paths

    def _save_json(self, results: Dict[str, dict], metadata: dict = None) -> str:
        """Save results as JSON with chunks."""
        filepath = os.path.join(self.output_dir, "results.json")

        output = {
            "run_timestamp": self.run_timestamp,
            "metadata": metadata or {},
            "results": results
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return filepath

    def _save_pdf(self, results: Dict[str, dict], metadata: dict = None, include_chunks: bool = True) -> str:
        """Save results as PDF with or without chunks.

        Args:
            results: Dictionary mapping questions to result data
            metadata: Optional metadata about the run
            include_chunks: If True, includes chunk excerpts; if False, answers only

        Returns:
            Path to the saved PDF file
        """
        if include_chunks:
            filepath = os.path.join(self.output_dir, "results_with_chunks.pdf")
        else:
            filepath = os.path.join(self.output_dir, "results_answers_only.pdf")

        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.75*inch, bottomMargin=0.75*inch)

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#1a1a1a',
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        question_style = ParagraphStyle(
            'Question',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='#2c5aa0',
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )

        answer_style = ParagraphStyle(
            'Answer',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='#333333',
            spaceAfter=12,
            alignment=TA_LEFT,
            leftIndent=20
        )

        chunk_header_style = ParagraphStyle(
            'ChunkHeader',
            parent=styles['Heading3'],
            fontSize=9,
            textColor='#666666',
            spaceAfter=4,
            spaceBefore=8,
            fontName='Helvetica-Bold',
            leftIndent=20
        )

        chunk_style = ParagraphStyle(
            'Chunk',
            parent=styles['BodyText'],
            fontSize=8,
            textColor='#555555',
            spaceAfter=8,
            alignment=TA_LEFT,
            leftIndent=30,
            rightIndent=10,
            borderColor='#cccccc',
            borderWidth=1,
            borderPadding=5,
            backColor='#f9f9f9'
        )

        metadata_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=9,
            textColor='#666666',
            spaceAfter=6
        )

        story = []

        # Title
        story.append(Paragraph("Earnings Transcript Analysis Results", title_style))
        story.append(Spacer(1, 0.2*inch))

        # Metadata
        if metadata:
            story.append(Paragraph(f"<b>Run Date:</b> {self.run_timestamp}", metadata_style))
            if 'transcripts' in metadata:
                story.append(Paragraph(f"<b>Transcripts Analyzed:</b> {len(metadata['transcripts'])}", metadata_style))
                for transcript in metadata['transcripts']:
                    story.append(Paragraph(f"  • {transcript['company']} {transcript['quarter']}", metadata_style))
            story.append(Paragraph(f"<b>Total Chunks in Vector Store:</b> {metadata.get('total_chunks', 'N/A')}", metadata_style))
            story.append(Spacer(1, 0.3*inch))

        # Questions and Answers
        for i, (question, result_data) in enumerate(results.items(), 1):
            answer = result_data['answer']
            chunks = result_data['chunks']

            story.append(Paragraph(f"Question {i}: {question}", question_style))
            story.append(Paragraph(answer, answer_style))

            # Add chunks section only if include_chunks is True
            if include_chunks:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(f"<b>Source Chunks Used ({len(chunks)} retrieved):</b>", chunk_header_style))

                for j, chunk in enumerate(chunks, 1):
                    chunk_text = chunk['content'][:500] + ('...' if len(chunk['content']) > 500 else '')
                    # Escape XML special characters
                    chunk_text = chunk_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

                    chunk_info = f"<i>Chunk {j} - {chunk['company']} {chunk['quarter']}</i>"
                    story.append(Paragraph(chunk_info, chunk_header_style))
                    story.append(Paragraph(chunk_text, chunk_style))

            story.append(Spacer(1, 0.2*inch))

        doc.build(story)
        return filepath

    def _save_metadata(self, metadata: dict = None) -> str:
        """Save run metadata as a separate JSON file."""
        filepath = os.path.join(self.output_dir, "run_metadata.json")

        meta_info = {
            "run_timestamp": self.run_timestamp,
            "output_directory": self.output_dir,
            **(metadata or {})
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(meta_info, f, indent=2, ensure_ascii=False)

        return filepath

    def _save_prompts(self, results: Dict[str, dict]) -> str:
        """Save all prompts to a text file for use with other LLMs.

        Args:
            results: Dictionary mapping questions to result data including prompts

        Returns:
            Path to the saved prompts file
        """
        filepath = os.path.join(self.output_dir, "prompts_for_llm.txt")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write("PROMPTS FOR EXTERNAL LLM (e.g., Claude)\n")
            f.write("=" * 100 + "\n\n")
            f.write("Instructions: Copy each prompt below and paste it into your LLM of choice.\n")
            f.write("Each prompt contains the full context and question.\n\n")
            f.write("=" * 100 + "\n\n")

            for i, (question, result_data) in enumerate(results.items(), 1):
                prompt = result_data.get('prompt', '')

                f.write(f"\n{'=' * 100}\n")
                f.write(f"QUESTION {i}\n")
                f.write(f"{'=' * 100}\n\n")
                f.write(f"{prompt}\n\n")
                f.write(f"{'=' * 100}\n\n")

        return filepath
