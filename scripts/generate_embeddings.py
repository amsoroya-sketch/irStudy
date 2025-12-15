#!/usr/bin/env python3
"""
PubMedBERT Embedding Generation Pipeline
Generates medical-optimized embeddings for all text chunks
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalEmbeddingGenerator:
    def __init__(self, model_name: str = "pritamdeka/S-PubMedBert-MS-MARCO", device: str = None):
        """
        Initialize embedding generator with PubMedBERT

        Args:
            model_name: HuggingFace model name (medical-optimized)
            device: 'cuda' or 'cpu' (auto-detected if None)
        """
        # Auto-detect device
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self.device = device
        logger.info(f"Using device: {self.device}")

        # Load model
        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model.to(self.device)

        # Get embedding dimension
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        embedding = self.model.encode(
            text,
            device=self.device,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embedding

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for batch of texts"""
        embeddings = self.model.encode(
            texts,
            device=self.device,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings

    def process_chunks(self, chunks_file: str = "data/chunks.json", output_file: str = "data/embeddings/medical_embeddings.pkl", batch_size: int = 32):
        """Process all chunks and generate embeddings"""
        chunks_path = Path(chunks_file)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Load chunks
        logger.info(f"Loading chunks from {chunks_file}")
        with open(chunks_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)

        logger.info(f"Loaded {len(chunks):,} chunks")

        # Extract texts
        texts = [chunk['text'] for chunk in chunks]

        # Generate embeddings
        logger.info(f"Generating embeddings (batch_size={batch_size})...")
        embeddings = self.generate_embeddings_batch(texts, batch_size=batch_size)

        # Combine chunks with embeddings
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append({
                'text': chunk['text'],
                'embedding': embedding.tolist(),  # Convert to list for JSON serialization
                'metadata': chunk['metadata']
            })

        # Save
        logger.info(f"Saving embeddings to {output_file}")
        with open(output_path, 'wb') as f:
            pickle.dump(embedded_chunks, f)

        # Statistics
        logger.info(f"✓ Embedding generation complete!")
        logger.info(f"  Total embeddings: {len(embedded_chunks):,}")
        logger.info(f"  Embedding dimension: {self.embedding_dim}")
        logger.info(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

        # Also save a sample as JSON for inspection
        sample_file = output_path.parent / "embeddings_sample.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(embedded_chunks[:10], f, indent=2, ensure_ascii=False)
        logger.info(f"  Sample saved to: {sample_file}")

        return embedded_chunks


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate PubMedBERT embeddings for medical texts")
    parser.add_argument("--input", default="data/chunks.json", help="Input chunks JSON file")
    parser.add_argument("--output", default="data/embeddings/medical_embeddings.pkl", help="Output embeddings file")
    parser.add_argument("--model", default="pritamdeka/S-PubMedBert-MS-MARCO", help="Embedding model name")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for embedding generation")
    parser.add_argument("--device", choices=['cuda', 'cpu'], default=None, help="Device to use (auto-detect if not specified)")

    args = parser.parse_args()

    generator = MedicalEmbeddingGenerator(model_name=args.model, device=args.device)
    generator.process_chunks(chunks_file=args.input, output_file=args.output, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
