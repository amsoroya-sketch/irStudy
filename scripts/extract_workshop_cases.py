#!/usr/bin/env python3
"""
Extract text + images from the 25-august-docs workshop case files (DOCX + PDF).

Reads 25-august-docs/INVENTORY.json (built by build_25aug_inventory.py) and
writes one JSON record per case to 25-august-docs/staging/<specialty>/,
with images saved under an assets/ subdir next to each record.

DOCX: mammoth (semantic HTML + image extraction) with python-docx text fallback.
PDF:  PyMuPDF text extraction; pytesseract OCR fallback for image-only pages
      (same approach as scripts/extract_pdfs.py MedicalPDFExtractor).

USAGE:
    source venv/bin/activate
    python3 scripts/extract_workshop_cases.py [--only <bundle-substring>] [--limit N]
"""

import argparse
import base64
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF
import mammoth

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "25-august-docs" / "INVENTORY.json"
STAGING = ROOT / "25-august-docs" / "staging"

MIN_TEXT_PER_PAGE = 40  # chars; below this a PDF page is considered image-only
MAX_IMAGE_BYTES = 400_000  # skip giant embedded images (full-slide screenshots kept)


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[\s_-]+", "_", name)[:80]


def ocr_page(page) -> str:
    try:
        import pytesseract
        from PIL import Image
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img)
    except Exception as e:  # OCR is best-effort
        print(f"      OCR failed: {e}", file=sys.stderr)
        return ""


def extract_pdf(path: Path, assets_dir: Path, case_slug: str):
    doc = fitz.open(path)
    pages, images, ocr_pages = [], [], 0
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if len(text) < MIN_TEXT_PER_PAGE:
            ocr_text = ocr_page(page).strip()
            if len(ocr_text) > len(text):
                text = ocr_text
                ocr_pages += 1
        pages.append(text)
        # keep at most 2 representative images per page to bound size
        for j, info in enumerate(page.get_images(full=True)[:2]):
            try:
                pix = fitz.Pixmap(doc, info[0])
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                data = pix.tobytes("png")
                if len(data) > MAX_IMAGE_BYTES or pix.width < 120 or pix.height < 120:
                    continue
                img_name = f"{case_slug}_p{i+1}_{j}.png"
                (assets_dir / img_name).write_bytes(data)
                images.append(img_name)
            except Exception:
                continue
    doc.close()
    return "\n\n".join(p for p in pages if p), images, {"pages": len(pages), "ocr_pages": ocr_pages}


def extract_docx(path: Path, assets_dir: Path, case_slug: str):
    images = []
    counter = {"n": 0}

    def save_image(image):
        counter["n"] += 1
        ext = (image.content_type or "image/png").split("/")[-1].split("+")[0]
        img_name = f"{case_slug}_img{counter['n']}.{ext}"
        with image.open() as f:
            data = f.read()
        if len(data) <= MAX_IMAGE_BYTES:
            (assets_dir / img_name).write_bytes(data)
            images.append(img_name)
            return {"src": f"assets/{img_name}"}
        return {"src": ""}

    with open(path, "rb") as f:
        result = mammoth.convert_to_html(f, convert_image=mammoth.images.img_element(save_image))
    html = result.value
    # plain text for the assessment stage
    with open(path, "rb") as f:
        text = mammoth.extract_raw_text(f).value
    return text.strip(), html, images


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="substring filter on bundle name")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    inv = json.loads(INVENTORY.read_text())
    files = inv["files"]
    if args.only:
        files = [f for f in files if args.only.lower() in f["bundle"].lower()]
    if args.limit:
        files = files[: args.limit]

    ok, failed = 0, []
    for item in files:
        src = ROOT / item["source"]
        specialty_dir = STAGING / item["target_dir"]
        assets_dir = specialty_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        case_slug = slugify(f"{item['bundle']}_{item['case_name']}")
        out_path = specialty_dir / f"{case_slug}.json"
        if out_path.exists():
            ok += 1
            continue

        print(f"  [{item['format']}] {item['bundle']} / {item['case_name']}")
        try:
            record = {
                "case_id": case_slug,
                "title": item["case_name"],
                "bundle": item["bundle"],
                "class": item["class"],
                "specialty": item["specialty"],
                "target_dir": item["target_dir"],
                "source_file": item["source"],
                "format": item["format"],
            }
            if item["format"] == "docx":
                text, html, images = extract_docx(src, assets_dir, case_slug)
                record.update(raw_text=text, html_fragment=html, images=images)
            else:
                text, images, stats = extract_pdf(src, assets_dir, case_slug)
                record.update(raw_text=text, html_fragment=None, images=images, pdf_stats=stats)

            if len(record["raw_text"]) < 200:
                raise ValueError(f"extracted only {len(record['raw_text'])} chars")

            out_path.write_text(json.dumps(record, ensure_ascii=False))
            ok += 1
        except Exception as e:
            failed.append({"source": item["source"], "error": str(e)})
            print(f"    ✗ FAILED: {e}", file=sys.stderr)

    summary = {"extracted": ok, "failed": failed}
    (STAGING / "extraction_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nDone: {ok} extracted, {len(failed)} failed → {STAGING}")
    if failed:
        for f in failed[:10]:
            print(f"  FAILED {f['source']}: {f['error']}")


if __name__ == "__main__":
    main()
