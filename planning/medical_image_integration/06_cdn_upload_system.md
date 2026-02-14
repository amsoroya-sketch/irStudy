# Task 06: CDN Upload System

**Duration:** 4 hours
**Priority:** P1
**Dependencies:** Task 05 (Citation Enrichment)
**Output:** Images uploaded to Cloudflare R2, CDN URLs in metadata

---

## Objective

Upload all medical images to Cloudflare R2 (S3-compatible storage) for fast, global CDN delivery with optimized images, caching, and cost-effective bandwidth.

---

## Scope

### In Scope
- Configure Cloudflare R2 bucket
- Optimize images (resize, compress, progressive JPEG)
- Upload images to R2 with correct metadata
- Generate CDN URLs for all images
- Update metadata JSON with CDN URLs
- Implement retry logic for failed uploads
- Calculate and monitor storage costs
- Test CDN delivery performance (<2s load time)

### Out of Scope
- Image watermarking
- Video uploads (future)
- 3D model uploads (future)
- Image transformation API (Cloudflare Images - future enhancement)

---

## Prerequisites

### Completed Tasks
- ✅ Task 04: Metadata processing complete
- ✅ Task 05: Citations added

### Cloudflare R2 Setup
- Cloudflare account created
- R2 enabled (free tier: 10GB storage)
- API credentials generated

### Tools Needed
- Python 3.12+
- Libraries: boto3 (S3 SDK), Pillow (image optimization)
- Cloudflare R2 credentials

---

## Implementation Steps

### Step 1: Cloudflare R2 Configuration (30 min)

**Manual setup in Cloudflare Dashboard:**

1. **Create R2 Bucket:**
   ```
   Dashboard > R2 > Create Bucket
   Name: irstudy-medical-images
   Region: Automatic (closest to users)
   ```

2. **Configure Public Access:**
   ```
   Bucket Settings > Public Access
   ☑ Allow public read access
   Custom domain: images.irstudy.com (optional)
   ```

3. **Generate API Token:**
   ```
   R2 > Manage R2 API Tokens > Create API Token
   Permissions: Edit
   Token Name: irstudy-image-uploader
   ```

   Save credentials:
   ```
   Account ID: <account-id>
   Access Key ID: <access-key>
   Secret Access Key: <secret-key>
   Endpoint: https://<account-id>.r2.cloudflarestorage.com
   ```

4. **Set Environment Variables:**
   ```bash
   # .env
   R2_ACCOUNT_ID=<account-id>
   R2_ACCESS_KEY_ID=<access-key>
   R2_SECRET_ACCESS_KEY=<secret-key>
   R2_BUCKET_NAME=irstudy-medical-images
   R2_PUBLIC_URL=https://pub-<hash>.r2.dev  # From R2 dashboard
   ```

---

### Step 2: Image Optimization Script (1 hour)

**File:** `scripts/optimize_images.py`

```python
#!/usr/bin/env python3
"""
Optimize medical images for web delivery.

Features:
- Resize large images (max 1920px)
- Convert to progressive JPEG
- Compress with quality 85
- Preserve EXIF metadata (if medical data)
"""

from PIL import Image
from pathlib import Path
import os


class ImageOptimizer:
    """Optimize images for CDN delivery"""

    def __init__(
        self,
        max_width: int = 1920,
        max_height: int = 1920,
        quality: int = 85,
        progressive: bool = True
    ):
        self.max_width = max_width
        self.max_height = max_height
        self.quality = quality
        self.progressive = progressive

    def optimize(self, input_path: Path, output_path: Path) -> Dict:
        """
        Optimize single image.

        Returns:
            {
                'original_size': int,
                'optimized_size': int,
                'reduction_percent': float,
                'original_dimensions': tuple,
                'optimized_dimensions': tuple
            }
        """
        try:
            # Open image
            with Image.open(input_path) as img:
                # Record original stats
                original_size = os.path.getsize(input_path)
                original_dimensions = img.size

                # Convert to RGB if needed (removes alpha channel)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Resize if too large
                if img.width > self.max_width or img.height > self.max_height:
                    img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)

                # Save optimized version
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(
                    output_path,
                    'JPEG',
                    quality=self.quality,
                    progressive=self.progressive,
                    optimize=True
                )

                # Record optimized stats
                optimized_size = os.path.getsize(output_path)
                optimized_dimensions = img.size

                reduction_percent = ((original_size - optimized_size) / original_size) * 100

                return {
                    'success': True,
                    'original_size': original_size,
                    'optimized_size': optimized_size,
                    'reduction_percent': reduction_percent,
                    'original_dimensions': original_dimensions,
                    'optimized_dimensions': optimized_dimensions
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def optimize_all_images(
    source_dir: Path,
    output_dir: Path,
    metadata_file: Path
) -> Dict:
    """Optimize all images referenced in metadata"""

    import json

    # Load metadata
    with open(metadata_file, 'r') as f:
        data = json.load(f)

    images = data['images']
    optimizer = ImageOptimizer()

    stats = {
        'total_images': len(images),
        'optimized': 0,
        'failed': 0,
        'total_original_size': 0,
        'total_optimized_size': 0,
        'errors': []
    }

    print(f"\n{'='*70}")
    print(f"Image Optimization")
    print(f"{'='*70}")
    print(f"Images: {len(images)}")
    print()

    for idx, img in enumerate(images, 1):
        if idx % 100 == 0:
            print(f"Processing: {idx}/{len(images)}")

        input_path = Path(img['file_path'])
        output_path = output_dir / input_path.relative_to('data')

        result = optimizer.optimize(input_path, output_path)

        if result['success']:
            stats['optimized'] += 1
            stats['total_original_size'] += result['original_size']
            stats['total_optimized_size'] += result['optimized_size']

            # Update metadata with optimized path
            img['optimized_path'] = str(output_path)
            img['optimized_size'] = result['optimized_size']
            img['optimized_dimensions'] = result['optimized_dimensions']

        else:
            stats['failed'] += 1
            stats['errors'].append({
                'image_id': img['image_id'],
                'error': result['error']
            })

    # Save updated metadata
    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=2)

    reduction_mb = (stats['total_original_size'] - stats['total_optimized_size']) / 1024 / 1024
    reduction_percent = ((stats['total_original_size'] - stats['total_optimized_size']) / stats['total_original_size']) * 100

    print(f"\n{'='*70}")
    print(f"Optimization Complete!")
    print(f"{'='*70}")
    print(f"Optimized: {stats['optimized']}/{stats['total_images']}")
    print(f"Failed: {stats['failed']}")
    print(f"Original size: {stats['total_original_size'] / 1024 / 1024:.2f} MB")
    print(f"Optimized size: {stats['total_optimized_size'] / 1024 / 1024:.2f} MB")
    print(f"Saved: {reduction_mb:.2f} MB ({reduction_percent:.1f}%)")

    return stats
```

---

### Step 3: Cloudflare R2 Upload Script (1.5 hours)

**File:** `scripts/upload_to_cdn.py`

```python
#!/usr/bin/env python3
"""
Upload optimized images to Cloudflare R2.

Usage:
    python3 scripts/upload_to_cdn.py \\
        --metadata data/processed_metadata/heal_metadata_cited.json \\
        --source data/optimized_images \\
        --bucket irstudy-medical-images
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError
from tqdm import tqdm
import time


class R2Uploader:
    """Upload images to Cloudflare R2"""

    def __init__(
        self,
        account_id: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        public_url: str
    ):
        self.bucket_name = bucket_name
        self.public_url = public_url

        # Create S3 client for R2
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto'
        )

    def upload_file(
        self,
        file_path: Path,
        object_key: str,
        metadata: Dict = None,
        retry_count: int = 3
    ) -> Dict:
        """
        Upload single file to R2.

        Args:
            file_path: Local file path
            object_key: R2 object key (path in bucket)
            metadata: Optional metadata dict
            retry_count: Number of retries on failure

        Returns:
            {
                'success': bool,
                'url': str,
                'error': str (if failed)
            }
        """
        for attempt in range(retry_count):
            try:
                # Prepare extra args
                extra_args = {
                    'ContentType': 'image/jpeg',
                    'CacheControl': 'public, max-age=31536000',  # 1 year
                }

                if metadata:
                    extra_args['Metadata'] = {
                        k: str(v) for k, v in metadata.items()
                    }

                # Upload file
                self.s3.upload_file(
                    str(file_path),
                    self.bucket_name,
                    object_key,
                    ExtraArgs=extra_args
                )

                # Generate public URL
                url = f"{self.public_url}/{object_key}"

                return {
                    'success': True,
                    'url': url
                }

            except ClientError as e:
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return {
                        'success': False,
                        'error': str(e)
                    }

        return {
            'success': False,
            'error': 'Max retries exceeded'
        }

    def upload_batch(
        self,
        images: List[Dict],
        source_dir: Path
    ) -> Dict:
        """Upload batch of images"""

        stats = {
            'total_images': len(images),
            'uploaded': 0,
            'failed': 0,
            'skipped': 0,
            'total_bytes': 0,
            'errors': []
        }

        print(f"\n{'='*70}")
        print(f"Uploading to Cloudflare R2")
        print(f"{'='*70}")
        print(f"Bucket: {self.bucket_name}")
        print(f"Images: {len(images)}")
        print()

        for img in tqdm(images, desc="Uploading"):
            # Skip if already uploaded
            if img.get('cdn_url'):
                stats['skipped'] += 1
                continue

            # Get file path
            file_path = Path(img.get('optimized_path', img['file_path']))

            if not file_path.exists():
                stats['failed'] += 1
                stats['errors'].append({
                    'image_id': img['image_id'],
                    'error': f'File not found: {file_path}'
                })
                continue

            # Generate object key
            # Example: medical_images/heal/hematology/acute_myeloid_leukemia/heal_889318.jpg
            object_key = f"medical_images/{img['source']}/{img['specialty']}/{img['topic'].lower().replace(' ', '_')}/{file_path.name}"

            # Prepare metadata
            metadata = {
                'image-id': img['image_id'],
                'specialty': img['specialty'],
                'topic': img['topic'],
                'source': img['source'],
                'license': img.get('license', ''),
            }

            # Upload
            result = self.upload_file(
                file_path=file_path,
                object_key=object_key,
                metadata=metadata
            )

            if result['success']:
                img['cdn_url'] = result['url']
                img['object_key'] = object_key
                stats['uploaded'] += 1
                stats['total_bytes'] += file_path.stat().st_size
            else:
                stats['failed'] += 1
                stats['errors'].append({
                    'image_id': img['image_id'],
                    'error': result['error']
                })

        return stats


def upload_images_to_cdn(
    metadata_file: Path,
    source_dir: Path,
    bucket_name: str,
    account_id: str,
    access_key: str,
    secret_key: str,
    public_url: str
) -> Dict:
    """Main upload function"""

    # Load metadata
    with open(metadata_file, 'r') as f:
        data = json.load(f)

    images = data['images']

    # Create uploader
    uploader = R2Uploader(
        account_id=account_id,
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
        public_url=public_url
    )

    # Upload batch
    stats = uploader.upload_batch(images, source_dir)

    # Update metadata file
    data['images'] = images
    data['cdn_metadata'] = {
        'bucket': bucket_name,
        'public_url': public_url,
        'uploaded_at': datetime.now().isoformat(),
        'statistics': stats
    }

    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Upload Complete!")
    print(f"{'='*70}")
    print(f"Uploaded: {stats['uploaded']}/{stats['total_images']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Total size: {stats['total_bytes'] / 1024 / 1024:.2f} MB")

    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for err in stats['errors'][:5]:
            print(f"  - {err['image_id']}: {err['error']}")

    return stats
```

---

### Step 4: CLI Interface (20 min)

```python
def main():
    parser = argparse.ArgumentParser(
        description='Upload images to Cloudflare R2 CDN',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--metadata',
        type=Path,
        required=True,
        help='Metadata JSON file'
    )

    parser.add_argument(
        '--source',
        type=Path,
        required=True,
        help='Source directory with optimized images'
    )

    parser.add_argument(
        '--bucket',
        default='irstudy-medical-images',
        help='R2 bucket name'
    )

    parser.add_argument(
        '--account-id',
        default=os.getenv('R2_ACCOUNT_ID'),
        help='Cloudflare R2 account ID'
    )

    parser.add_argument(
        '--access-key',
        default=os.getenv('R2_ACCESS_KEY_ID'),
        help='R2 access key ID'
    )

    parser.add_argument(
        '--secret-key',
        default=os.getenv('R2_SECRET_ACCESS_KEY'),
        help='R2 secret access key'
    )

    parser.add_argument(
        '--public-url',
        default=os.getenv('R2_PUBLIC_URL'),
        help='R2 public URL'
    )

    args = parser.parse_args()

    # Validate credentials
    if not all([args.account_id, args.access_key, args.secret_key, args.public_url]):
        print("❌ Missing R2 credentials. Set environment variables:")
        print("  R2_ACCOUNT_ID")
        print("  R2_ACCESS_KEY_ID")
        print("  R2_SECRET_ACCESS_KEY")
        print("  R2_PUBLIC_URL")
        return 1

    # Upload images
    stats = upload_images_to_cdn(
        metadata_file=args.metadata,
        source_dir=args.source,
        bucket_name=args.bucket,
        account_id=args.account_id,
        access_key=args.access_key,
        secret_key=args.secret_key,
        public_url=args.public_url
    )

    print("\n✓ Upload complete!")
    return 0


if __name__ == "__main__":
    from datetime import datetime
    exit(main())
```

---

### Step 5: CDN Performance Testing (30 min)

**File:** `scripts/test_cdn_performance.py`

```python
#!/usr/bin/env python3
"""Test CDN delivery performance"""

import requests
import time
import json
from pathlib import Path
from statistics import mean, median


def test_cdn_performance(metadata_file: Path, sample_size: int = 20) -> Dict:
    """Test CDN image load times"""

    # Load metadata
    with open(metadata_file, 'r') as f:
        data = json.load(f)

    images = [img for img in data['images'] if img.get('cdn_url')]

    if not images:
        print("❌ No CDN URLs found in metadata")
        return {}

    # Sample random images
    import random
    sample = random.sample(images, min(sample_size, len(images)))

    print(f"\n{'='*70}")
    print(f"CDN Performance Test")
    print(f"{'='*70}")
    print(f"Testing {len(sample)} random images...")
    print()

    load_times = []
    failed = []

    for idx, img in enumerate(sample, 1):
        url = img['cdn_url']

        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            duration = time.time() - start

            if response.status_code == 200:
                load_times.append(duration)
                size_kb = len(response.content) / 1024
                print(f"{idx:2}. ✓ {duration*1000:6.0f}ms | {size_kb:6.1f}KB | {img['image_id']}")
            else:
                failed.append({
                    'image_id': img['image_id'],
                    'url': url,
                    'status_code': response.status_code
                })
                print(f"{idx:2}. ✗ HTTP {response.status_code} | {img['image_id']}")

        except Exception as e:
            failed.append({
                'image_id': img['image_id'],
                'url': url,
                'error': str(e)
            })
            print(f"{idx:2}. ✗ ERROR | {img['image_id']}")

    # Calculate statistics
    if load_times:
        stats = {
            'total_tested': len(sample),
            'successful': len(load_times),
            'failed': len(failed),
            'mean_load_time_ms': mean(load_times) * 1000,
            'median_load_time_ms': median(load_times) * 1000,
            'min_load_time_ms': min(load_times) * 1000,
            'max_load_time_ms': max(load_times) * 1000,
            'under_2s': sum(1 for t in load_times if t < 2),
            'pass': all(t < 2 for t in load_times)
        }

        print(f"\n{'='*70}")
        print(f"Performance Results")
        print(f"{'='*70}")
        print(f"Tested: {stats['total_tested']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"\nLoad Times:")
        print(f"  Mean: {stats['mean_load_time_ms']:.0f}ms")
        print(f"  Median: {stats['median_load_time_ms']:.0f}ms")
        print(f"  Min: {stats['min_load_time_ms']:.0f}ms")
        print(f"  Max: {stats['max_load_time_ms']:.0f}ms")
        print(f"  Under 2s: {stats['under_2s']}/{stats['total_tested']}")
        print(f"\n{'✓' if stats['pass'] else '✗'} Performance test {'PASSED' if stats['pass'] else 'FAILED'}")

        return stats

    return {}


if __name__ == "__main__":
    import sys
    metadata_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('data/processed_metadata/heal_metadata_cited.json')
    test_cdn_performance(metadata_file)
```

---

## Testing

### Full Workflow Test

```bash
# Step 1: Optimize images
python3 scripts/optimize_images.py \
    --source data/medical_images/heal \
    --output data/optimized_images \
    --metadata data/processed_metadata/heal_metadata_cited.json

# Step 2: Upload to R2
export R2_ACCOUNT_ID="<your-account-id>"
export R2_ACCESS_KEY_ID="<your-access-key>"
export R2_SECRET_ACCESS_KEY="<your-secret-key>"
export R2_PUBLIC_URL="https://pub-<hash>.r2.dev"

python3 scripts/upload_to_cdn.py \
    --metadata data/processed_metadata/heal_metadata_cited.json \
    --source data/optimized_images \
    --bucket irstudy-medical-images

# Step 3: Test CDN performance
python3 scripts/test_cdn_performance.py \
    data/processed_metadata/heal_metadata_cited.json
```

---

## Success Criteria

- ✅ All images optimized (30-50% size reduction)
- ✅ All images uploaded to R2 (1,137/1,137)
- ✅ CDN URLs generated for all images
- ✅ Metadata updated with CDN URLs
- ✅ Load time <2s for all images (95%+)
- ✅ Public access works (no 403 errors)
- ✅ Correct caching headers set (1 year)
- ✅ Storage cost <$5/month (estimated)

---

## Next Task

After completion, proceed to **Task 07: Database Image Indexing**

File: `07_database_image_indexing.md`
