#!/usr/bin/env python3
"""
Index parsed OSCE video scenarios to Qdrant RAG system.

Purpose: Enhance persona generation with dual citations (eTG + video scenarios).
Output: ~13,000 chunks in Qdrant collection 'osce_video_scenarios'.

Phase 0 of 8-phase AMC Clinical Exam platform implementation.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Configuration
VIDEO_OUTPUT_DIR = "/home/dev/Development/irStudy/osce-pipeline/output"
COLLECTION_NAME = "osce_video_scenarios"
CHUNK_SIZE = 250  # tokens (same as eTG)
OVERLAP = 50  # tokens
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

def load_video_metadata(video_dir: Path) -> Dict:
    """Load analysis.json metadata."""
    analysis_path = video_dir / "analysis.json"
    if not analysis_path.exists():
        return {}
    with open(analysis_path) as f:
        return json.load(f)

def load_clinical_notes(video_dir: Path) -> str:
    """Load clinical_notes.md content."""
    notes_path = video_dir / "clinical_notes.md"
    if not notes_path.exists():
        return ""
    with open(notes_path, 'r', encoding='utf-8') as f:
        return f.read()

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Chunk text into segments of ~250 tokens with 50-token overlap.
    Simple word-based chunking (1 word ≈ 1.3 tokens for English medical text).
    """
    words = text.split()
    word_chunk_size = int(chunk_size / 1.3)
    word_overlap = int(overlap / 1.3)

    chunks = []
    for i in range(0, len(words), word_chunk_size - word_overlap):
        chunk_words = words[i:i + word_chunk_size]
        if len(chunk_words) < 50:  # Skip very small chunks
            continue
        chunks.append(' '.join(chunk_words))

    return chunks

def create_qdrant_collection(client: QdrantClient, embedding_size: int):
    """Create Qdrant collection if it doesn't exist."""
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' already exists")
    except:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=embedding_size,
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Created collection '{COLLECTION_NAME}'")

def index_videos():
    """Main indexing function."""
    print("=== Phase 0: Video Scenario Indexing ===\n")

    # Initialize embedding model
    print("1. Loading embedding model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embedding_size = model.get_sentence_embedding_dimension()
    print(f"   Embedding size: {embedding_size}")

    # Connect to Qdrant
    print(f"2. Connecting to Qdrant ({QDRANT_HOST}:{QDRANT_PORT})...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Create collection
    print("3. Creating/verifying collection...")
    create_qdrant_collection(client, embedding_size)

    # Find all video directories
    video_base = Path(VIDEO_OUTPUT_DIR)
    video_dirs = [d for d in video_base.iterdir() if d.is_dir()]
    print(f"4. Found {len(video_dirs)} video directories")

    # Process each video
    total_chunks = 0
    points = []
    successful_videos = 0
    failed_videos = []

    for idx, video_dir in enumerate(video_dirs, 1):
        print(f"\n   [{idx}/{len(video_dirs)}] Processing: {video_dir.name}")

        try:
            # Load metadata
            metadata = load_video_metadata(video_dir)
            if not metadata:
                print(f"       ⚠️ No analysis.json found, skipping")
                failed_videos.append(video_dir.name)
                continue

            slug = metadata.get('slug', video_dir.name)

            # Load clinical notes
            clinical_notes = load_clinical_notes(video_dir)
            if not clinical_notes:
                print(f"       ⚠️ No clinical_notes.md found, skipping")
                failed_videos.append(video_dir.name)
                continue

            # Chunk notes
            chunks = chunk_text(clinical_notes, CHUNK_SIZE, OVERLAP)
            print(f"       Created {len(chunks)} chunks")

            # Create embeddings and points
            for chunk_idx, chunk_content in enumerate(chunks):
                # Generate unique point ID
                point_id_str = f"{slug}_chunk_{chunk_idx}"
                point_id_hash = hashlib.md5(point_id_str.encode()).hexdigest()

                # Embed chunk
                embedding = model.encode(chunk_content).tolist()

                # Create point
                point = models.PointStruct(
                    id=point_id_hash,
                    vector=embedding,
                    payload={
                        "source_type": "osce_video",
                        "video_slug": slug,
                        "chunk_index": chunk_idx,
                        "content": chunk_content,
                        "presenting_complaint": metadata.get('presenting_complaint', ''),
                        "ddx_mentioned": metadata.get('ddx_mentioned', []),
                        "investigations_mentioned": metadata.get('investigations_mentioned', []),
                        "station_type": metadata.get('station_type', 'history_taking'),
                    }
                )
                points.append(point)
                total_chunks += 1

            # Batch upload every 100 points
            if len(points) >= 100:
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                print(f"       ✅ Uploaded {len(points)} points")
                points = []

            successful_videos += 1

        except Exception as e:
            print(f"       ❌ Error processing {video_dir.name}: {e}")
            failed_videos.append(video_dir.name)
            continue

    # Upload remaining points
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"\n✅ Uploaded final {len(points)} points")

    print(f"\n=== Indexing Complete ===")
    print(f"Total videos processed: {successful_videos}/{len(video_dirs)}")
    print(f"Total chunks indexed: {total_chunks}")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")

    if failed_videos:
        print(f"\n⚠️ Failed videos ({len(failed_videos)}):")
        for video in failed_videos:
            print(f"   - {video}")

    # Verify collection
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        print(f"\n✅ Verification: {collection_info.points_count} points in collection")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")

if __name__ == "__main__":
    index_videos()
