from __future__ import annotations

import chromadb
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Any

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model

# Ephemeral client: Lives in memory and goes away when the server restarts
chroma_client = chromadb.EphemeralClient()

def get_or_create_collection(collection_name: str):
    return chroma_client.get_or_create_collection(name=collection_name)

def delete_collection(collection_name: str):
    try:
        chroma_client.delete_collection(name=collection_name)
    except Exception:
        # Ignore if collection doesn't exist or other deletion errors
        pass

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Splits text into chunks of `chunk_size` characters with `overlap` characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += (chunk_size - overlap)
    return chunks

def embed_and_store(collection_name: str, text: str) -> None:
    """Chunks the text, creates embeddings, and stores them in ChromaDB."""
    delete_collection(collection_name) # Ensure fresh collection for the document
    collection = get_or_create_collection(collection_name)
    
    chunks = chunk_text(text)
    if not chunks:
        return
        
    embeddings = get_embedding_model().encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]
    
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

def query_vector_store(collection_name: str, query: str, n_results: int = 3) -> List[str]:
    """Queries the collection using the embedded query string and returns top K documents."""
    collection = get_or_create_collection(collection_name)
    
    # Check if the collection is empty
    if collection.count() == 0:
        return []
        
    query_embedding = get_embedding_model().encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count())
    )
    
    documents = results.get("documents", [[]])[0]
    return documents
