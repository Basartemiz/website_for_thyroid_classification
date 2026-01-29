"""
Django management command to ingest PDF guidelines into the vector store.

Memory-efficient: processes and stores one page at a time.
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

        # Initialize vector store
        vectorstore = get_vectorstore()

        if options['reset']:
            self.stdout.write("Resetting vector store...")
            vectorstore.delete_collection()

        # Initialize tokenizer
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
                added = self._process_pdf_streaming(
                    pdf_path,
                    vectorstore,
                    tokenizer,
                    chunk_size,
                    chunk_overlap
                )
                total_chunks += added
                self.stdout.write(self.style.SUCCESS(
                    f"  Done: {added} chunks added"
                ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {str(e)}"))

            # Force garbage collection between PDFs
            gc.collect()

        self.stdout.write(self.style.SUCCESS(
            f"\nIngestion complete. Total chunks: {total_chunks}"
        ))

        # Verify
        count = vectorstore.count()
        self.stdout.write(f"Vector store now contains {count} documents")

    def _process_pdf_streaming(
        self, pdf_path, vectorstore, tokenizer, chunk_size, chunk_overlap
    ):
        """
        Process a PDF page-by-page, writing each page's chunks to the
        vector store immediately to minimize memory usage.
        """
        doc_id = pdf_path.name
        added = 0

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            self.stdout.write(f"  Pages: {total_pages}")

            for page_num in range(total_pages):
                # Load one page at a time
                page = pdf.pages[page_num]
                text = page.extract_text()

                if not text or not text.strip():
                    continue

                text = self._clean_text(text)

                page_chunks = self._chunk_text(
                    text, tokenizer, chunk_size, chunk_overlap
                )

                if not page_chunks:
                    continue

                # Build batch for this page only
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

                # Write immediately, then free memory
                vectorstore.add_documents(
                    documents=chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                added += len(chunks)

                self.stdout.write(
                    f"  Page {page_num + 1}/{total_pages}: "
                    f"{len(chunks)} chunks stored"
                )

                # Free page data
                del chunks, metadatas, ids, page_chunks, text

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
        """
        Split text into overlapping chunks based on token count.
        """
        tokens = tokenizer.encode(text)
        chunks = []

        if len(tokens) <= chunk_size:
            return [text]

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
