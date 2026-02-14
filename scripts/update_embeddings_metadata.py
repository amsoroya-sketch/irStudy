#!/usr/bin/env python3
"""
Update Embeddings Metadata
Merges existing embeddings with fixed metadata from chunks.json

This is faster than re-embedding (which requires torch and takes 20+ minutes)
We keep the embeddings but update the metadata from the fixed chunks.json

USAGE:
    python scripts/update_embeddings_metadata.py
"""

import json
import pickle
from pathlib import Path
import sys


def update_embeddings_metadata(
    embeddings_file: str = "data/embeddings/medical_embeddings.pkl",
    chunks_file: str = "data/chunks.json",
    output_file: str = "data/embeddings/medical_embeddings_fixed.pkl"
):
    """
    Update embeddings with fixed metadata from chunks.json

    Args:
        embeddings_file: Existing embeddings file
        chunks_file: Fixed chunks file with complete metadata
        output_file: Output file for updated embeddings
    """
    print(f"🔄 Updating embeddings metadata")
    print("="*60)

    # Load existing embeddings
    print(f"Loading embeddings from: {embeddings_file}")
    with open(embeddings_file, 'rb') as f:
        embedded_chunks = pickle.load(f)

    print(f"Loaded {len(embedded_chunks):,} embedded chunks")

    # Load fixed chunks
    print(f"Loading fixed metadata from: {chunks_file}")
    with open(chunks_file, 'r', encoding='utf-8') as f:
        fixed_chunks = json.load(f)

    print(f"Loaded {len(fixed_chunks):,} fixed chunks")

    # Verify counts match
    if len(embedded_chunks) != len(fixed_chunks):
        print(f"⚠️  Warning: Count mismatch!")
        print(f"   Embeddings: {len(embedded_chunks):,}")
        print(f"   Chunks: {len(fixed_chunks):,}")
        print("   Using minimum count...")
        min_count = min(len(embedded_chunks), len(fixed_chunks))
    else:
        min_count = len(embedded_chunks)
        print(f"✅ Counts match: {min_count:,}")

    # Update metadata
    print(f"\nUpdating metadata for {min_count:,} chunks...")
    updated_chunks = []

    stats = {
        'updated_title': 0,
        'updated_author': 0,
        'updated_year': 0,
        'updated_edition': 0,
    }

    for i in range(min_count):
        embedded = embedded_chunks[i]
        fixed = fixed_chunks[i]

        # Keep embedding, update metadata
        updated = {
            'text': embedded['text'],
            'embedding': embedded['embedding'],
            'metadata': fixed['metadata']  # Use fixed metadata
        }

        # Track what was updated
        old_meta = embedded.get('metadata', {})
        new_meta = fixed['metadata']

        if old_meta.get('title') != new_meta.get('title'):
            stats['updated_title'] += 1
        if old_meta.get('author') != new_meta.get('author'):
            stats['updated_author'] += 1
        if old_meta.get('year') != new_meta.get('year'):
            stats['updated_year'] += 1
        if old_meta.get('edition') != new_meta.get('edition'):
            stats['updated_edition'] += 1

        updated_chunks.append(updated)

    # Save updated embeddings
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving updated embeddings to: {output_file}")
    with open(output_path, 'wb') as f:
        pickle.dump(updated_chunks, f)

    # Show statistics
    print("\n" + "="*60)
    print("UPDATE STATISTICS:")
    print("="*60)
    print(f"Total chunks updated: {len(updated_chunks):,}")
    print(f"\nMetadata fields updated:")
    print(f"  • Title: {stats['updated_title']:,} chunks")
    print(f"  • Author: {stats['updated_author']:,} chunks")
    print(f"  • Year: {stats['updated_year']:,} chunks")
    print(f"  • Edition: {stats['updated_edition']:,} chunks")

    # Sample check
    print("\n" + "="*60)
    print("SAMPLE METADATA (first chunk):")
    print("="*60)

    sample = updated_chunks[0]
    meta = sample['metadata']
    print(f"Title: {meta.get('title', 'N/A')}")
    print(f"Author: {meta.get('author', 'N/A')}")
    print(f"Year: {meta.get('year', 'N/A')}")
    print(f"Edition: {meta.get('edition', 'N/A')}")
    print(f"Source: {meta.get('source', 'N/A')}")
    print(f"Page: {meta.get('page', 'N/A')}")

    print("\n✅ Metadata update complete!")
    print(f"Updated embeddings saved to: {output_file}")

    return len(updated_chunks)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update embeddings with fixed metadata from chunks.json"
    )
    parser.add_argument(
        '--embeddings',
        default="data/embeddings/medical_embeddings.pkl",
        help="Existing embeddings file"
    )
    parser.add_argument(
        '--chunks',
        default="data/chunks.json",
        help="Fixed chunks file with metadata"
    )
    parser.add_argument(
        '--output',
        default="data/embeddings/medical_embeddings_fixed.pkl",
        help="Output file for updated embeddings"
    )

    args = parser.parse_args()

    try:
        count = update_embeddings_metadata(
            args.embeddings,
            args.chunks,
            args.output
        )

        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Re-index Qdrant with updated embeddings:")
        print(f"   python scripts/index_qdrant.py --embeddings {args.output}")
        print("2. Validate RAG database metadata:")
        print("   python scripts/validate_rag_database_metadata.py")
        print("3. Test RAG citation quality:")
        print("   python scripts/test_rag_citation_quality.py --queries 20")
        print("="*60)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
