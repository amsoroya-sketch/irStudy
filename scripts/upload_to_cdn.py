#!/usr/bin/env python3
"""
Upload medical images to Cloudflare R2 (S3-compatible CDN)

Usage:
    # Set environment variables
    export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
    export R2_ACCESS_KEY_ID="<your-access-key>"
    export R2_SECRET_ACCESS_KEY="<your-secret-key>"

    # Upload images
    python3 scripts/upload_to_cdn.py \
        --source data/medical_images \
        --bucket irstudy-medical-images \
        --metadata data/image_metadata.json

Requirements:
    pip3 install boto3 tqdm Pillow
"""

import boto3
from pathlib import Path
from tqdm import tqdm
import json
import os
import argparse
from PIL import Image
import io

class R2Uploader:
    """Upload images to Cloudflare R2 with thumbnail generation"""

    def __init__(self, endpoint_url, access_key_id, secret_access_key, bucket_name):
        self.bucket_name = bucket_name

        # Configure R2 client (S3-compatible)
        self.s3 = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name='auto'
        )

        # Verify bucket exists
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            print(f"✓ Connected to bucket: {bucket_name}")
        except Exception as e:
            print(f"✗ Bucket access error: {e}")
            raise

    def generate_thumbnail(self, image_path, max_size=(300, 300)):
        """Generate thumbnail and return as bytes"""
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                # Generate thumbnail
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save to bytes
                thumb_bytes = io.BytesIO()
                img.save(thumb_bytes, format='JPEG', quality=85, optimize=True)
                thumb_bytes.seek(0)

                return thumb_bytes

        except Exception as e:
            print(f"  Thumbnail generation error: {e}")
            return None

    def upload_image(self, local_path, s3_key, metadata=None):
        """Upload single image to R2"""
        try:
            extra_args = {
                'ContentType': self._get_content_type(local_path),
                'CacheControl': 'public, max-age=31536000',  # 1 year cache
            }

            # Add custom metadata
            if metadata:
                extra_args['Metadata'] = {
                    k: str(v) for k, v in metadata.items()
                    if v is not None and k in [
                        'source', 'external_id', 'diagnosis',
                        'modality', 'specialty', 'license'
                    ]
                }

            # Upload original image
            self.s3.upload_file(
                str(local_path),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Generate and upload thumbnail
            thumb_key = s3_key.replace('images/', 'thumbnails/')
            thumb_data = self.generate_thumbnail(local_path)

            if thumb_data:
                self.s3.upload_fileobj(
                    thumb_data,
                    self.bucket_name,
                    thumb_key,
                    ExtraArgs={
                        'ContentType': 'image/jpeg',
                        'CacheControl': 'public, max-age=31536000'
                    }
                )

            return True

        except Exception as e:
            print(f"  Upload error: {e}")
            return False

    def _get_content_type(self, file_path):
        """Determine content type from file extension"""
        ext = Path(file_path).suffix.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff'
        }
        return content_types.get(ext, 'application/octet-stream')

def upload_to_r2(source_dir, bucket_name, metadata_json, cdn_base_url, dry_run=False):
    """Upload images to Cloudflare R2"""

    # Load metadata
    with open(metadata_json) as f:
        images = json.load(f)

    print(f"Found {len(images)} images in metadata")

    # Initialize uploader
    endpoint_url = os.getenv('R2_ENDPOINT_URL')
    access_key_id = os.getenv('R2_ACCESS_KEY_ID')
    secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')

    if not all([endpoint_url, access_key_id, secret_access_key]):
        print("✗ Missing R2 credentials in environment variables:")
        print("  - R2_ENDPOINT_URL")
        print("  - R2_ACCESS_KEY_ID")
        print("  - R2_SECRET_ACCESS_KEY")
        return

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be uploaded\n")
    else:
        uploader = R2Uploader(endpoint_url, access_key_id, secret_access_key, bucket_name)

    # Upload each image
    uploaded_count = 0
    failed_count = 0

    for img_meta in tqdm(images, desc="Uploading images"):
        local_path = Path(source_dir) / img_meta['file_path']

        if not local_path.exists():
            print(f"✗ File not found: {local_path}")
            failed_count += 1
            continue

        # Generate S3 key
        s3_key = f"images/{img_meta['file_path']}"

        if dry_run:
            print(f"Would upload: {local_path} → s3://{bucket_name}/{s3_key}")
            uploaded_count += 1
        else:
            # Upload to R2
            success = uploader.upload_image(
                local_path,
                s3_key,
                metadata=img_meta
            )

            if success:
                # Update CDN URLs in metadata
                img_meta['cdn_url'] = f"{cdn_base_url}/{s3_key}"
                img_meta['thumbnail_url'] = f"{cdn_base_url}/thumbnails/{img_meta['file_path']}"
                uploaded_count += 1
            else:
                failed_count += 1

    if not dry_run:
        # Save updated metadata with CDN URLs
        with open(metadata_json, 'w') as f:
            json.dump(images, f, indent=2)

    print(f"\n{'='*50}")
    print("Upload Summary")
    print(f"{'='*50}")
    print(f"Total images: {len(images)}")
    print(f"Uploaded: {uploaded_count}")
    print(f"Failed: {failed_count}")

    if not dry_run:
        print(f"\nMetadata updated with CDN URLs: {metadata_json}")
        print(f"\nNext step: python3 scripts/index_images.py")

def main():
    parser = argparse.ArgumentParser(
        description='Upload medical images to Cloudflare R2 CDN',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Environment Variables (required):
  R2_ENDPOINT_URL         Cloudflare R2 endpoint URL
  R2_ACCESS_KEY_ID        R2 access key ID
  R2_SECRET_ACCESS_KEY    R2 secret access key

Examples:
  # Setup credentials
  export R2_ENDPOINT_URL="https://abc123.r2.cloudflarestorage.com"
  export R2_ACCESS_KEY_ID="your-key-id"
  export R2_SECRET_ACCESS_KEY="your-secret"

  # Upload images
  python3 scripts/upload_to_cdn.py \\
      --source data/medical_images \\
      --bucket irstudy-medical-images \\
      --metadata data/image_metadata.json \\
      --cdn-url https://cdn.irstudy.com

  # Dry run (test without uploading)
  python3 scripts/upload_to_cdn.py \\
      --source data/medical_images \\
      --bucket irstudy-medical-images \\
      --metadata data/image_metadata.json \\
      --dry-run
        '''
    )

    parser.add_argument(
        '--source',
        required=True,
        help='Source directory containing medical images'
    )
    parser.add_argument(
        '--bucket',
        required=True,
        help='R2 bucket name'
    )
    parser.add_argument(
        '--metadata',
        required=True,
        help='Metadata JSON file'
    )
    parser.add_argument(
        '--cdn-url',
        default='https://cdn.irstudy.com',
        help='CDN base URL (default: https://cdn.irstudy.com)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test run without uploading'
    )

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.source).exists():
        print(f"✗ Source directory not found: {args.source}")
        return 1

    if not Path(args.metadata).exists():
        print(f"✗ Metadata file not found: {args.metadata}")
        return 1

    # Upload images
    upload_to_r2(
        args.source,
        args.bucket,
        args.metadata,
        args.cdn_url,
        dry_run=args.dry_run
    )

    return 0

if __name__ == '__main__':
    exit(main())
