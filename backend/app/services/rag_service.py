import os
import pickle
from typing import List, Dict, Optional
from pathlib import Path
import faiss
import numpy as np
from datetime import datetime
from app.utils.file_processor import extract_text_from_file, chunk_text
from app.services.mistral_service import mistral_service


class RAGSystem:
    def __init__(self, data_dir: str = None, index_dir: str = None):
        # Use absolute paths based on this file's location
        base_dir = Path(__file__).parent.parent.parent  # Go up to backend/

        if data_dir is None:
            data_dir = base_dir / "data"
        else:
            data_dir = Path(data_dir)

        if index_dir is None:
            index_dir = base_dir / "vector_store"
        else:
            index_dir = Path(index_dir)

        self.data_dir = data_dir
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Mistral embed-2312 outputs 1024-dimensional vectors
        self.dimension = 1024

        # Initialize or load FAISS index
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict] = []
        self.index_path = self.index_dir / "faiss.index"
        self.metadata_path = self.index_dir / "metadata.pkl"

    async def initialize(self):
        """Initialize RAG system - load existing index or create new one."""
        # Check if existing index has the correct dimension
        if self.index_path.exists() and self.metadata_path.exists():
            print("Loading existing FAISS index...")
            if not self._load_index():
                # Index had wrong dimension — start fresh
                print("Index dimension mismatch detected, rebuilding from scratch...")
                self.index = faiss.IndexFlatL2(self.dimension)
                self.documents = []
                # Delete stale index files
                self.index_path.unlink(missing_ok=True)
                self.metadata_path.unlink(missing_ok=True)
        else:
            print("No existing index found, creating new one")
            self.index = faiss.IndexFlatL2(self.dimension)

        # Check for history.txt updates specifically
        history_file = self.data_dir / "history.txt"
        await self._check_and_reindex_history(history_file)

        # Check for other new files
        new_files = await self._scan_for_new_files()

        if new_files:
            print(f"Found {len(new_files)} new files to index")
            await self._add_documents(new_files)

        print(f"RAG system initialized with {len(self.documents)} documents")

    async def _check_and_reindex_history(self, history_file: Path):
        """Check if history.txt has been updated and reindex only that file."""
        if not history_file.exists():
            print("No history.txt file found, skipping history reindexing")
            return

        # Get current modification time using Path for consistency
        current_mtime = history_file.stat().st_mtime

        # Check if history.txt is in the index
        history_docs = [doc for doc in self.documents if doc['filepath'] == str(history_file)]

        if history_docs:
            # Get the timestamp of the indexed version
            indexed_timestamp = history_docs[0].get('file_mtime', 0)

            if current_mtime > indexed_timestamp:
                print(f"history.txt has been updated, reindexing...")
                # Remove old history.txt chunks from index
                await self._remove_document_from_index(str(history_file))
                # Add updated version
                await self._add_documents([history_file], file_mtime=current_mtime)
            else:
                print("history.txt is up to date in the index")
        else:
            # History file not in index, add it
            print("Adding history.txt to index for the first time")
            await self._add_documents([history_file], file_mtime=current_mtime)

    async def _remove_document_from_index(self, filepath: str):
        """
        Remove all chunks of a document from the index.

        Performance Note: FAISS IndexFlatL2 doesn't support removing individual vectors,
        so we must rebuild the entire index. For large indexes (>10k chunks), this could
        take several seconds. This is acceptable for history.txt updates but may need
        optimization for bulk operations (e.g., use IndexIDMap for deletion support).
        """
        # Find indices of chunks to remove
        indices_to_keep = []
        docs_to_keep = []

        for i, doc in enumerate(self.documents):
            if doc['filepath'] != filepath:
                indices_to_keep.append(i)
                docs_to_keep.append(doc)

        if len(indices_to_keep) == len(self.documents):
            print(f"No chunks found for {filepath}")
            return

        # Rebuild index with remaining documents
        if self.index and self.index.ntotal > 0:
            # Extract embeddings for documents to keep
            if indices_to_keep:
                print(f"Removing {len(self.documents) - len(indices_to_keep)} chunks from index")
                # Optimisation: Rather than calling the external Mistral API to re-embed
                # the existing chunks (which is slow, costly, and error-prone), we can
                # reconstruct the vectors directly from the local FAISS index.
                if self.index.ntotal == len(self.documents):
                    all_vectors = self.index.reconstruct_n(0, self.index.ntotal)
                    embeddings = all_vectors[indices_to_keep]
                else:
                    # Fallback in case of mismatch (highly unlikely)
                    print("Warning: FAISS index size does not match metadata length. Re-embedding via Mistral API...")
                    chunks_to_keep = [doc['chunk'] for doc in docs_to_keep]
                    embeddings = await mistral_service.get_embeddings(chunks_to_keep)
                
                self.index = faiss.IndexFlatL2(self.dimension)
                self.index.add(embeddings)
            else:
                # No documents to keep, reset index
                self.index = faiss.IndexFlatL2(self.dimension)

        self.documents = docs_to_keep
        self._save_index()

    async def _scan_for_new_files(self) -> List[Path]:
        """Scan data directory for new files."""
        supported_extensions = {'.pdf', '.txt', '.md', '.markdown', '.docx'}
        all_files = []

        for ext in supported_extensions:
            all_files.extend(self.data_dir.glob(f"*{ext}"))

        # Filter out already indexed files and history.txt (handled separately)
        indexed_files = {doc['filepath'] for doc in self.documents}
        history_file = str(self.data_dir / "history.txt")
        new_files = [f for f in all_files if str(f) not in indexed_files and str(f) != history_file]

        return new_files

    async def _add_documents(self, files: List[Path], file_mtime: float = None):
        """Process and add documents to FAISS index."""
        for file_path in files:
            try:
                print(f"Processing: {file_path.name}")
                text = await extract_text_from_file(str(file_path))

                if not text:
                    print(f"No text extracted from {file_path.name}")
                    continue

                # Chunk the text
                chunks = chunk_text(text, chunk_size=800, overlap=100)

                if not chunks:
                    continue

                # Generate embeddings via Mistral API
                embeddings = await mistral_service.get_embeddings(chunks)

                # Add to FAISS index
                if self.index is None:
                    self.index = faiss.IndexFlatL2(self.dimension)

                self.index.add(embeddings)

                # Get file modification time if not provided (using Path for consistency)
                if file_mtime is None:
                    file_mtime = file_path.stat().st_mtime if file_path.exists() else 0

                # Store metadata
                for i, chunk in enumerate(chunks):
                    self.documents.append({
                        'filepath': str(file_path),
                        'filename': file_path.name,
                        'chunk': chunk,
                        'chunk_index': i,
                        'timestamp': datetime.utcnow().isoformat(),
                        'file_mtime': file_mtime
                    })

                print(f"Added {len(chunks)} chunks from {file_path.name}")

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

        # Save index after adding documents
        self._save_index()

    async def add_note_to_index(self, title: str, content: str, note_id: str):
        """Add a single note to the index."""
        try:
            # Save note as text file
            clean_title = title.replace(' ', '_').replace('/', '_')
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{clean_title}_{timestamp}.txt"
            filepath = self.data_dir / filename

            # Save content to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            # Add to index
            await self._add_documents([filepath])

            print(f"Note '{title}' added to RAG index")

        except Exception as e:
            print(f"Error adding note to index: {e}")

    async def search(self, query: str, k: int = 3) -> List[Dict]:
        """Search for relevant documents."""
        if self.index is None or self.index.ntotal == 0:
            return []

        try:
            # Encode query via Mistral API
            query_embedding = await mistral_service.get_embeddings([query])

            # Search
            distances, indices = self.index.search(
                query_embedding,
                min(k, self.index.ntotal)
            )

            # Format results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx].copy()
                    doc['similarity'] = float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                    results.append(doc)

            return results

        except Exception as e:
            print(f"Error searching index: {e}")
            return []

    def _save_index(self):
        """Save FAISS index and metadata to disk."""
        try:
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))

            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)

            print("Index saved successfully")

        except Exception as e:
            print(f"Error saving index: {e}")

    def _load_index(self) -> bool:
        """Load FAISS index and metadata from disk.

        Returns:
            True if loaded successfully with correct dimension, False otherwise.
        """
        try:
            loaded_index = faiss.read_index(str(self.index_path))

            # Validate dimension matches expected Mistral embedding size
            if loaded_index.d != self.dimension:
                print(f"Index dimension mismatch: found {loaded_index.d}, expected {self.dimension}")
                return False

            self.index = loaded_index

            with open(self.metadata_path, 'rb') as f:
                self.documents = pickle.load(f)

            print("Index loaded successfully")
            return True

        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            return False


# Global RAG system instance
rag_system: Optional[RAGSystem] = None


async def get_rag_system() -> RAGSystem:
    """Get or create RAG system instance."""
    global rag_system
    if rag_system is None:
        rag_system = RAGSystem()
        await rag_system.initialize()
    return rag_system
