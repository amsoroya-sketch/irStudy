# Task 08: RAG Integration (Multimodal)

**Duration:** 4 hours
**Priority:** P2 (Optional Enhancement)
**Dependencies:** Task 07 (Database Image Indexing)
**Output:** RAG system returns images with text responses

---

## Objective

Integrate medical images into the existing Qdrant RAG system, enabling multimodal responses where relevant images are returned alongside text chunks for medical queries.

---

## Scope

### In Scope
- Generate image embeddings using CLIP model
- Store image embeddings in Qdrant
- Update RAG query logic to return images + text
- Implement image relevance scoring
- Create multimodal response formatter
- Test RAG with image-heavy queries (e.g., "Show ECG for STEMI")

### Out of Scope
- Image content analysis (OCR, object detection)
- Video embeddings (future)
- Real-time image generation (future)
- Custom CLIP fine-tuning (future enhancement)

---

## Prerequisites

### Completed Tasks
- ✅ Task 07: Images indexed in PostgreSQL

### Existing Systems
- Qdrant vector database running
- RAG query service (`src/services/rag_query_service.py`)
- Text embeddings using sentence-transformers

### New Requirements
- CLIP model (OpenAI's CLIP or similar)
- Image embedding pipeline
- Multimodal Qdrant collection

---

## Implementation Steps

### Step 1: CLIP Model Setup (30 min)

**File:** `src/models/clip_client.py`

```python
#!/usr/bin/env python3
"""
CLIP model for generating image embeddings.

Uses OpenAI's CLIP model to create embeddings for:
- Medical images (visual features)
- Text descriptions (for cross-modal search)
"""

from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
from pathlib import Path
from typing import List, Union
import numpy as np


class CLIPEmbedder:
    """Generate embeddings using CLIP"""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        """
        Initialize CLIP model.

        Args:
            model_name: HuggingFace model name
        """
        print(f"Loading CLIP model: {model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.embedding_dim = 512  # CLIP base dimension

    def embed_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Generate embedding for single image.

        Args:
            image_path: Path to image file

        Returns:
            Embedding vector (512-dim)
        """
        image = Image.open(image_path).convert('RGB')

        # Process image
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        # Generate embedding
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)

        # Normalize
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()[0]

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text query.

        Args:
            text: Text query

        Returns:
            Embedding vector (512-dim)
        """
        # Process text
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)

        # Generate embedding
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)

        # Normalize
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        return text_features.cpu().numpy()[0]

    def embed_images_batch(self, image_paths: List[Path], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple images in batches.

        Args:
            image_paths: List of image paths
            batch_size: Batch size for processing

        Returns:
            Array of embeddings (N × 512)
        """
        embeddings = []

        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_images = [Image.open(p).convert('RGB') for p in batch_paths]

            # Process batch
            inputs = self.processor(images=batch_images, return_tensors="pt", padding=True).to(self.device)

            # Generate embeddings
            with torch.no_grad():
                batch_features = self.model.get_image_features(**inputs)

            # Normalize
            batch_features = batch_features / batch_features.norm(dim=-1, keepdim=True)

            embeddings.append(batch_features.cpu().numpy())

        return np.vstack(embeddings)
```

---

### Step 2: Generate Image Embeddings (1 hour)

**File:** `scripts/generate_image_embeddings.py`

```python
#!/usr/bin/env python3
"""
Generate CLIP embeddings for all medical images.

Usage:
    python3 scripts/generate_image_embeddings.py \\
        --metadata data/processed_metadata/heal_metadata_cited.json \\
        --output data/embeddings/image_embeddings.pkl \\
        --batch-size 32
"""

import argparse
import json
import pickle
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.clip_client import CLIPEmbedder
from tqdm import tqdm


def generate_embeddings(
    metadata_file: Path,
    output_file: Path,
    batch_size: int = 32
) -> Dict:
    """Generate CLIP embeddings for all images"""

    # Load metadata
    with open(metadata_file, 'r') as f:
        data = json.load(f)

    images = data['images']

    print(f"\n{'='*70}")
    print(f"Image Embedding Generation")
    print(f"{'='*70}")
    print(f"Total images: {len(images)}")
    print(f"Batch size: {batch_size}")
    print()

    # Initialize CLIP
    embedder = CLIPEmbedder()

    # Prepare image paths
    image_paths = []
    image_ids = []

    for img in images:
        # Use local file if exists, otherwise download from CDN
        file_path = Path(img.get('file_path', ''))

        if not file_path.exists():
            print(f"⚠ Skipping {img['image_id']} (file not found)")
            continue

        image_paths.append(file_path)
        image_ids.append(img['image_id'])

    print(f"Processing {len(image_paths)} images...")

    # Generate embeddings in batches
    all_embeddings = []

    for i in tqdm(range(0, len(image_paths), batch_size), desc="Generating embeddings"):
        batch_paths = image_paths[i:i + batch_size]
        batch_embeddings = embedder.embed_images_batch(batch_paths, batch_size=batch_size)
        all_embeddings.append(batch_embeddings)

    # Combine all embeddings
    embeddings = np.vstack(all_embeddings)

    # Create embeddings dict
    embeddings_dict = {
        'image_ids': image_ids,
        'embeddings': embeddings,
        'embedding_dim': embedder.embedding_dim,
        'model': 'openai/clip-vit-base-patch32',
        'generated_at': datetime.now().isoformat()
    }

    # Save embeddings
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'wb') as f:
        pickle.dump(embeddings_dict, f)

    print(f"\n{'='*70}")
    print(f"Embeddings Generated!")
    print(f"{'='*70}")
    print(f"Total embeddings: {len(image_ids)}")
    print(f"Embedding dimension: {embedder.embedding_dim}")
    print(f"Output: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")

    return embeddings_dict


if __name__ == "__main__":
    import numpy as np
    from datetime import datetime

    parser = argparse.ArgumentParser(description='Generate image embeddings with CLIP')

    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--batch-size', type=int, default=32)

    args = parser.parse_args()

    generate_embeddings(args.metadata, args.output, args.batch_size)
```

---

### Step 3: Index Images in Qdrant (45 min)

**File:** `scripts/index_images_qdrant.py`

```python
#!/usr/bin/env python3
"""
Index medical images in Qdrant for multimodal RAG.

Usage:
    python3 scripts/index_images_qdrant.py \\
        --metadata data/processed_metadata/heal_metadata_cited.json \\
        --embeddings data/embeddings/image_embeddings.pkl \\
        --collection medical_images
"""

import argparse
import json
import pickle
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm


def index_images_qdrant(
    metadata_file: Path,
    embeddings_file: Path,
    collection_name: str,
    qdrant_url: str = "http://localhost:6333"
) -> Dict:
    """Index images in Qdrant"""

    # Load metadata
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    images = {img['image_id']: img for img in metadata['images']}

    # Load embeddings
    with open(embeddings_file, 'rb') as f:
        embeddings_data = pickle.load(f)

    image_ids = embeddings_data['image_ids']
    embeddings = embeddings_data['embeddings']
    embedding_dim = embeddings_data['embedding_dim']

    print(f"\n{'='*70}")
    print(f"Qdrant Image Indexing")
    print(f"{'='*70}")
    print(f"Collection: {collection_name}")
    print(f"Images: {len(image_ids)}")
    print(f"Embedding dim: {embedding_dim}")
    print()

    # Connect to Qdrant
    client = QdrantClient(url=qdrant_url)

    # Create collection if not exists
    try:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=embedding_dim,
                distance=Distance.COSINE
            )
        )
        print(f"✓ Created collection: {collection_name}")
    except Exception:
        print(f"✓ Collection already exists: {collection_name}")

    # Prepare points
    points = []

    for idx, image_id in enumerate(tqdm(image_ids, desc="Preparing points")):
        img = images.get(image_id)

        if not img:
            print(f"⚠ Image not found in metadata: {image_id}")
            continue

        point = PointStruct(
            id=idx,
            vector=embeddings[idx].tolist(),
            payload={
                'image_id': image_id,
                'source': img['source'],
                'specialty': img['specialty'],
                'topic': img['topic'],
                'clinical_finding': img.get('clinical_finding', ''),
                'modality': img.get('modality', ''),
                'cdn_url': img['cdn_url'],
                'citation': img['citation'],
                'license': img['license'],
                'type': 'image'  # Distinguish from text chunks
            }
        )

        points.append(point)

    # Upload points in batches
    batch_size = 100

    for i in tqdm(range(0, len(points), batch_size), desc="Uploading to Qdrant"):
        batch = points[i:i + batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )

    print(f"\n{'='*70}")
    print(f"Indexing Complete!")
    print(f"{'='*70}")
    print(f"Indexed: {len(points)} images")

    return {
        'total_indexed': len(points),
        'collection': collection_name
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Index images in Qdrant')

    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--embeddings', type=Path, required=True)
    parser.add_argument('--collection', default='medical_images')
    parser.add_argument('--qdrant-url', default='http://localhost:6333')

    args = parser.parse_args()

    index_images_qdrant(
        metadata_file=args.metadata,
        embeddings_file=args.embeddings,
        collection_name=args.collection,
        qdrant_url=args.qdrant_url
    )
```

---

### Step 4: Multimodal RAG Query Service (1.5 hours)

**File:** `src/services/multimodal_rag_service.py`

```python
#!/usr/bin/env python3
"""
Multimodal RAG service that returns both text and images.
"""

from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from src.models.clip_client import CLIPEmbedder
from src.services.rag_query_service import RAGQueryService


class MultimodalRAGService:
    """RAG service with image support"""

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        text_collection: str = "medical_knowledge",
        image_collection: str = "medical_images"
    ):
        self.client = QdrantClient(url=qdrant_url)
        self.text_collection = text_collection
        self.image_collection = image_collection

        # Text RAG service
        self.text_rag = RAGQueryService(qdrant_url=qdrant_url)

        # CLIP for image search
        self.clip = CLIPEmbedder()

    def query(
        self,
        query_text: str,
        top_k_text: int = 5,
        top_k_images: int = 3,
        include_images: bool = True
    ) -> Dict:
        """
        Query RAG system for both text and images.

        Args:
            query_text: User query
            top_k_text: Number of text chunks to return
            top_k_images: Number of images to return
            include_images: Whether to search images

        Returns:
            {
                'text_results': [...],
                'image_results': [...],
                'combined_response': str
            }
        """

        # Search text chunks (existing RAG)
        text_results = self.text_rag.query(
            query=query_text,
            top_k=top_k_text
        )

        image_results = []

        if include_images:
            # Generate query embedding
            query_embedding = self.clip.embed_text(query_text)

            # Search images
            search_results = self.client.search(
                collection_name=self.image_collection,
                query_vector=query_embedding.tolist(),
                limit=top_k_images,
                with_payload=True
            )

            # Format image results
            for result in search_results:
                image_results.append({
                    'image_id': result.payload['image_id'],
                    'cdn_url': result.payload['cdn_url'],
                    'topic': result.payload['topic'],
                    'clinical_finding': result.payload['clinical_finding'],
                    'modality': result.payload['modality'],
                    'citation': result.payload['citation'],
                    'relevance_score': result.score
                })

        # Combine results into response
        combined_response = self._format_multimodal_response(
            query=query_text,
            text_results=text_results,
            image_results=image_results
        )

        return {
            'text_results': text_results,
            'image_results': image_results,
            'combined_response': combined_response
        }

    def _format_multimodal_response(
        self,
        query: str,
        text_results: List[Dict],
        image_results: List[Dict]
    ) -> str:
        """Format combined text + image response"""

        response_parts = []

        # Add text summary
        if text_results:
            response_parts.append("**Text Sources:**\n")
            for idx, result in enumerate(text_results[:3], 1):
                response_parts.append(
                    f"{idx}. {result.get('text', '')[:200]}... "
                    f"[{result.get('source', 'Unknown')}]"
                )

        # Add image references
        if image_results:
            response_parts.append("\n**Relevant Images:**\n")
            for idx, img in enumerate(image_results, 1):
                response_parts.append(
                    f"{idx}. [{img['topic']}]({img['cdn_url']}) - "
                    f"{img['clinical_finding']} ({img['modality']}) "
                    f"[Relevance: {img['relevance_score']:.2f}]"
                )

        return "\n".join(response_parts)
```

---

### Step 5: API Integration (30 min)

**File:** `backend/src/api/v1/rag.py` (update existing)

```python
from fastapi import APIRouter, Query
from src.services.multimodal_rag_service import MultimodalRAGService

router = APIRouter(prefix="/rag", tags=["RAG"])

rag_service = MultimodalRAGService()


@router.get("/query")
async def query_rag(
    query: str = Query(..., description="Search query"),
    top_k_text: int = Query(5, description="Number of text results"),
    top_k_images: int = Query(3, description="Number of image results"),
    include_images: bool = Query(True, description="Include images in response")
):
    """
    Query RAG system with multimodal support.

    Returns text chunks and relevant medical images.
    """
    results = rag_service.query(
        query_text=query,
        top_k_text=top_k_text,
        top_k_images=top_k_images,
        include_images=include_images
    )

    return results
```

---

## Testing

### Integration Test

```bash
# Step 1: Generate embeddings
python3 scripts/generate_image_embeddings.py \
    --metadata data/processed_metadata/heal_metadata_cited.json \
    --output data/embeddings/image_embeddings.pkl \
    --batch-size 32

# Step 2: Index in Qdrant
python3 scripts/index_images_qdrant.py \
    --metadata data/processed_metadata/heal_metadata_cited.json \
    --embeddings data/embeddings/image_embeddings.pkl \
    --collection medical_images

# Step 3: Test query
curl -s "http://localhost:8000/api/v1/rag/query?query=Show%20ECG%20for%20atrial%20fibrillation&include_images=true" | jq

# Expected response:
{
  "text_results": [...],
  "image_results": [
    {
      "image_id": "heal_abc123",
      "cdn_url": "https://pub-xyz.r2.dev/medical_images/heal/cardiology/atrial_fibrillation_ecg/heal_889123.jpg",
      "topic": "Atrial Fibrillation ECG",
      "clinical_finding": "Atrial Fibrillation (ECG)",
      "modality": "ECG",
      "relevance_score": 0.92
    }
  ],
  "combined_response": "..."
}
```

---

## Success Criteria

- ✅ CLIP embeddings generated for all images
- ✅ Images indexed in Qdrant (1,137 images)
- ✅ Multimodal RAG query returns text + images
- ✅ Image relevance scores >0.8 for specific queries
- ✅ API endpoint returns multimodal responses
- ✅ Query time <500ms for text + images
- ✅ Images ranked correctly by relevance

---

## Next Task

After completion, proceed to **Task 09: Image Content Linking**

File: `09_image_content_linking.md`
