# Brazos County Foreclosure Search

A lightweight tool to extract, search, and analyze Brazos County monthly foreclosure notices. Built to support multifamily and single-family real estate deal sourcing in Bryan/College Station, TX.

---

## What it does

- **Extracts** structured data from Brazos County foreclosure PDFs (messy OCR-scanned documents)
- **Displays** all notices in a searchable, filterable card interface
- **Filters** by city, notice type (substitute trustee, trustee, sheriff's sale), and loan amount range
- **Expands** each card to show full debtor, lender, deed date, property description, and notes

---

## Repo structure

```
foreclosure-search/
├── app/
│   ├── index.html      # Search engine UI (standalone, no build step needed)
│   └── data.js         # Current month's notice data (update monthly)
├── data/
│   └── notices.json    # Raw extracted JSON (output of extract.py)
├── scripts/
│   └── extract.py      # PDF → JSON extractor
└── README.md
```

---

## How to update monthly

1. Download the new foreclosure PDF from [Brazos County Clerk](https://www.brazoscountytx.gov/481/Foreclosure-Notices)
2. Run the extractor:
   ```bash
   python scripts/extract.py <new_file.pdf> data/notices.json
   ```
3. Review `data/notices.json` — the OCR parser handles most notices automatically, but verify addresses and amounts
4. Copy the array contents into `app/data.js` replacing the existing `DATA` array
5. Open `app/index.html` in a browser — no server needed

---

## Running locally

Just open `app/index.html` in any browser. No build step, no server, no dependencies.

---

## Extractor requirements

```bash
# Install poppler (for pdftotext)
# macOS:
brew install poppler

# Ubuntu/Debian:
sudo apt install poppler-utils

# Python fallback (if no poppler):
pip install pymupdf
```

---

## Investment criteria this tool helps screen for

The search and filter system is built around spotting:

- **Sheriff's sales** — judgment liens, often the deepest discounts
- **Private lender deals** — easier to negotiate than national servicers
- **Local credit union loans** — relationship-based, more flexible
- **High-value properties** — filter by loan amount to find multifamily or commercial
- **College Station properties** — A&M student rental demand drives year-round occupancy

---

## License

MIT — use freely.
