"""
Django management command to ingest PDF guidelines into the vector store.

Memory-efficient: opens PDF per page, closes immediately after extraction.
"""

import gc
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import pdfplumber
from pathlib import Path
import tiktoken

from thyroid.rag.vectorstore import get_vectorstore


class Command(BaseCommand):
    help = 'Ingest PDF guidelines into the ChromaDB vector store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing collection before ingesting',
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=800,
            help='Target chunk size in tokens (default: 800)',
        )
        parser.add_argument(
            '--chunk-overlap',
            type=int,
            default=120,
            help='Overlap between chunks in tokens (default: 120)',
        )

    def handle(self, *args, **options):
        assets_dir = settings.ASSETS_DIR

        if not assets_dir.exists():
            raise CommandError(f"Assets directory not found: {assets_dir}")

        pdf_files = list(assets_dir.glob("*.pdf"))

        if not pdf_files:
            raise CommandError(f"No PDF files found in {assets_dir}")

        self.stdout.write(f"Found {len(pdf_files)} PDF files to process")

        vectorstore = get_vectorstore()

        if options['reset']:
            self.stdout.write("Resetting vector store...")
            vectorstore.delete_collection()

        try:
            tokenizer = tiktoken.encoding_for_model("gpt-4")
        except Exception:
            tokenizer = tiktoken.get_encoding("cl100k_base")

        chunk_size = options['chunk_size']
        chunk_overlap = options['chunk_overlap']

        total_chunks = 0

        for pdf_path in pdf_files:
            self.stdout.write(f"\nProcessing: {pdf_path.name}")

            try:
                added = self._process_pdf_page_by_page(
                    pdf_path, vectorstore, tokenizer,
                    chunk_size, chunk_overlap
                )
                total_chunks += added
                self.stdout.write(self.style.SUCCESS(
                    f"  Done: {added} chunks added"
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {str(e)}"))

            gc.collect()

        self.stdout.write(self.style.SUCCESS(
            f"\nIngestion complete. Total chunks: {total_chunks}"
        ))

        count = vectorstore.count()
        self.stdout.write(f"Vector store now contains {count} documents")

    def _get_page_count(self, pdf_path):
        """Open PDF only to get page count, then close immediately."""
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)

    def _extract_single_page(self, pdf_path, page_index):
        """Open PDF, extract one page's text, close immediately."""
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_index]
            text = page.extract_text()
        return text

    def _process_pdf_page_by_page(
        self, pdf_path, vectorstore, tokenizer, chunk_size, chunk_overlap
    ):
        """
        Process PDF one page at a time. Opens and closes the file
        for each page to keep memory flat.
        """
        doc_id = pdf_path.name
        total_pages = self._get_page_count(pdf_path)
        self.stdout.write(f"  Pages: {total_pages}")
        added = 0

        for page_num in range(total_pages):
            # Open PDF, grab one page, close PDF
            text = self._extract_single_page(pdf_path, page_num)

            if not text or not text.strip():
                continue

            text = self._clean_text(text)

            page_chunks = self._chunk_text(
                text, tokenizer, chunk_size, chunk_overlap
            )

            if not page_chunks:
                continue

            chunks = []
            metadatas = []
            ids = []

            for chunk_idx, chunk_text in enumerate(page_chunks):
                chunk_id = f"{doc_id.replace('.pdf', '')}_{page_num + 1}_{chunk_idx:02d}"
                chunks.append(chunk_text)
                metadatas.append({
                    'doc_id': doc_id,
                    'page': page_num + 1,
                    'chunk_id': chunk_id,
                })
                ids.append(chunk_id)

            vectorstore.add_documents(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            added += len(chunks)

            # Log every 50 pages to reduce output noise
            if (page_num + 1) % 50 == 0 or page_num == total_pages - 1:
                self.stdout.write(
                    f"  Progress: {page_num + 1}/{total_pages} pages, "
                    f"{added} chunks stored"
                )

            # Free everything and collect garbage every 10 pages
            del chunks, metadatas, ids, page_chunks, text
            if (page_num + 1) % 10 == 0:
                gc.collect()

        return added

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _chunk_text(
        self,
        text: str,
        tokenizer,
        chunk_size: int,
        chunk_overlap: int
    ) -> list:
        """Split text into overlapping chunks based on token count."""
        tokens = tokenizer.encode(text)

        if len(tokens) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))

            chunk_tokens = tokens[start:end]
            chunk_text = tokenizer.decode(chunk_tokens)

            chunk_text = chunk_text.strip()
            if chunk_text:
                chunks.append(chunk_text)

            start = end - chunk_overlap

            if start >= len(tokens) - chunk_overlap:
                break

        return chunks
