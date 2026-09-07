"""
Brazos County Foreclosure Notice Extractor
-------------------------------------------
Extracts structured data from Brazos County monthly foreclosure PDFs.

Usage:
    python extract.py input.pdf output.json

Requirements:
    pip install pdfminer.six pymupdf
"""

import sys
import re
import json
from pathlib import Path


def extract_text(pdf_path: str) -> str:
    """Extract raw text from PDF using pdftotext (poppler) or pymupdf fallback."""
    import subprocess
    result = subprocess.run(
        ["pdftotext", pdf_path, "-"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout
    # Fallback: pymupdf
    try:
        import fitz
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text() for page in doc)
    except ImportError:
        raise RuntimeError("Neither pdftotext nor pymupdf available. Install poppler-utils or pip install pymupdf.")


def parse_notices(text: str) -> list[dict]:
    """
    Parse raw PDF text into structured notice records.
    Handles OCR artifacts common in scanned Brazos County documents.
    """
    notices = []
    pages = text.split("\f")

    current_address = None
    current_city = None
    current_text = ""

    for page in pages:
        lines = [l.strip() for l in page.strip().split("\n") if l.strip()]
        if not lines:
            continue

        first_line = lines[0]
        # Address pattern: 3-5 digits + street name
        addr_match = re.match(r"^\d{3,5}\s+[A-Z]", first_line)

        if addr_match and len(lines) > 1:
            if current_address and current_text:
                notice = parse_notice_block(current_address, current_city, current_text)
                if notice:
                    notices.append(notice)
            current_address = first_line
            current_city = lines[1] if len(lines) > 1 else ""
            current_text = "\n".join(lines)
        else:
            current_text += "\n" + "\n".join(lines)

    # Last notice
    if current_address and current_text:
        notice = parse_notice_block(current_address, current_city, current_text)
        if notice:
            notices.append(notice)

    return notices


def parse_notice_block(address: str, city_line: str, raw_text: str) -> dict | None:
    """Extract structured fields from a single notice block."""
    # Dollar amounts
    amounts = re.findall(r"\$([1-9][0-9]{2,3},[0-9]{3}(?:\.[0-9]{2})?)", raw_text)
    if not amounts:
        return None

    # Clean amount (first occurrence = original principal)
    amount_str = amounts[0].replace(",", "")
    try:
        amount = float(amount_str)
    except ValueError:
        return None

    # Debtor name
    debtor_match = re.search(
        r"executed by\s+([\w\s,\.]+?)(?:,?\s*(?:securing|provides|husband|wife))",
        raw_text, re.IGNORECASE
    )
    debtor = debtor_match.group(1).strip() if debtor_match else "Unknown"

    # Notice type
    if "SHERIFF" in raw_text.upper():
        notice_type = "Sheriff"
    elif "SUBSTITUTE" in raw_text.upper():
        notice_type = "Substitute trustee"
    else:
        notice_type = "Trustee"

    # Lender / mortgagee
    lender_match = re.search(
        r"(?:current mortgagee|mortgagee of the note)[^.]*?\.\s*([\w\s&,\.]+?(?:LLC|Inc|Corp|Bank|Trust|Capital|Mortgage|Investment)[^.]*?)\.",
        raw_text, re.IGNORECASE
    )
    lender = lender_match.group(1).strip() if lender_match else "Unknown"

    # Deed date
    deed_match = re.search(
        r"Deed of Trust[^d]*dated\s+([\w\s,]+?\d{4})",
        raw_text, re.IGNORECASE
    )
    deed_date = deed_match.group(1).strip() if deed_match else "Unknown"

    # Parse city/state/zip from city_line
    city_parts = re.match(r"(.+?),\s*TX\s*(\d{5})?", city_line)
    city = city_parts.group(1).strip() if city_parts else city_line
    zipcode = city_parts.group(2) if city_parts and city_parts.group(2) else ""

    return {
        "address": address.title(),
        "city": city,
        "state": "TX",
        "zip": zipcode,
        "debtor": debtor,
        "lender": lender,
        "amount": amount,
        "deedDate": deed_date,
        "type": notice_type,
        "raw_snippet": raw_text[:500]
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract.py input.pdf output.json")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Extracting text from {pdf_path}...")
    text = extract_text(pdf_path)

    print("Parsing notices...")
    notices = parse_notices(text)

    print(f"Found {len(notices)} notices.")
    with open(output_path, "w") as f:
        json.dump(notices, f, indent=2)

    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
