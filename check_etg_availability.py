#!/usr/bin/env python3
"""
Check eTG (Therapeutic Guidelines) availability in Qdrant medical_knowledge collection
"""

from qdrant_client import QdrantClient
from typing import List, Dict, Any
import json


def check_etg_in_qdrant():
    """Check if eTG content is available in Qdrant"""

    print("🔍 Checking eTG availability in Qdrant medical_knowledge collection...")
    print("=" * 80)

    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)

    # Get collection info
    try:
        collection_info = client.get_collection("medical_knowledge")
        print(f"\n✅ Collection 'medical_knowledge' found")
        print(f"   Total points: {collection_info.points_count}")
        print(f"   Vector size: {collection_info.config.params.vectors.size}")
        print()
    except Exception as e:
        print(f"❌ Error accessing collection: {e}")
        return

    # Search for eTG-related content
    etg_search_terms = [
        "Therapeutic Guidelines",
        "eTG",
        "antibiotic guideline",
        "paediatric guideline",
        "cardiovascular guideline",
        "surgery guideline",
    ]

    print("\n🔎 Searching for eTG content in collection...")
    print("-" * 80)

    etg_points_found = {}

    for term in etg_search_terms:
        try:
            # Use scroll to search through payloads
            points, _ = client.scroll(
                collection_name="medical_knowledge",
                limit=100,
                with_payload=True,
                with_vectors=False,
            )

            # Check each point for eTG references
            for point in points:
                payload = point.payload

                # Check if source contains eTG references
                source = payload.get("source", "").lower()
                text = payload.get("text", "").lower()
                book = payload.get("book", "").lower()

                if any(
                    etg_term.lower() in field
                    for field in [source, text, book]
                    for etg_term in ["therapeutic guidelines", "etg"]
                ):
                    # Extract section info if available
                    section = payload.get("section", "N/A")
                    page = payload.get("page", "N/A")
                    chunk_id = payload.get("chunk_id", str(point.id))

                    if chunk_id not in etg_points_found:
                        etg_points_found[chunk_id] = {
                            "source": payload.get("source", "Unknown"),
                            "book": payload.get("book", "Unknown"),
                            "section": section,
                            "page": page,
                            "text_preview": payload.get("text", "")[:150],
                        }

            if etg_points_found:
                break

        except Exception as e:
            print(f"   ⚠️  Error searching for '{term}': {e}")
            continue

    # Report findings
    print(f"\n📊 eTG Content Analysis:")
    print("-" * 80)

    if etg_points_found:
        print(f"✅ Found {len(etg_points_found)} eTG-related chunks")
        print()

        # Show sample entries
        print("📄 Sample eTG entries:")
        for i, (chunk_id, data) in enumerate(list(etg_points_found.items())[:5]):
            print(f"\n   {i+1}. Chunk ID: {chunk_id}")
            print(f"      Source: {data['source']}")
            print(f"      Book: {data['book']}")
            print(f"      Section: {data['section']}")
            print(f"      Page: {data['page']}")
            print(f"      Preview: {data['text_preview']}...")

        # Check for section number patterns
        sections_available = sum(
            1 for d in etg_points_found.values() if d["section"] not in ["N/A", None, "", "Unknown"]
        )

        print(f"\n📋 Section Number Availability:")
        print(f"   Chunks with section numbers: {sections_available}/{len(etg_points_found)}")

        if sections_available > 0:
            print(f"   ✅ Section numbers ARE extractable from eTG chunks!")
        else:
            print(f"   ⚠️  Section numbers NOT found in payload metadata")
            print(f"   💡 Will need to extract from text content")

    else:
        print("❌ No eTG content found in collection")
        print()
        print("📋 Available books in collection:")

        # Try to find what books ARE available
        try:
            points, _ = client.scroll(
                collection_name="medical_knowledge", limit=50, with_payload=True, with_vectors=False
            )

            books = set()
            for point in points:
                book = point.payload.get("book", point.payload.get("source", "Unknown"))
                if book and book != "Unknown":
                    books.add(book)

            for book in sorted(books):
                print(f"   - {book}")

        except Exception as e:
            print(f"   ⚠️  Error retrieving book list: {e}")

    print("\n" + "=" * 80)

    # Return summary
    return {
        "etg_found": len(etg_points_found) > 0,
        "total_etg_chunks": len(etg_points_found),
        "sections_available": sections_available if etg_points_found else 0,
        "sample_entries": list(etg_points_found.values())[:5],
    }


if __name__ == "__main__":
    result = check_etg_in_qdrant()

    # Save result to JSON
    with open("etg_availability_report.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n📝 Report saved to: etg_availability_report.json")
