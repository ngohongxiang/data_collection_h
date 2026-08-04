# Data Collection Pipeline (Hospitality)

A production-ready online data collection pipeline that collects, decodes, and exports hotel listings at scale. Built to handle obfuscated data, anti-bot protections, and performance bottlenecks — not just the happy-path.

> **TL;DR:** Fetches 367+ pages of hotel listings, parses structured data, decodes ROT-style obfuscated contact details, and exports clean CSV. Includes benchmarking for parser optimization (BeautifulSoup vs. Selectolax) and parallelization.

---

### Why This Project Matters

Most tutorials stop at `requests.get()` + `BeautifulSoup`. This pipeline solves real-world problems:

1.  **Obfuscated Data:** Contact details are encoded with a custom token (`data-mailto-token`) requiring reverse-engineered decoding logic
2.  **Anti-Bot Measures:** Implements proxy support, randomized delays, and human-like headers
3.  **Performance at Scale:** Benchmarked two parsers and parallel execution — 130x speedup on 4400+ records with `selectolax` (BeautifulSoup alternative) + `ThreadPoolExecutor` against baseline parser

### Architecture

```
data_collection_pipeline.py (Orchestrator)
    │
    ├── fetcher/data_fetcher.py     → Handles HTTP, proxies, rate-limiting
    ├── extractor/
    │   ├── data_extractor.py       → Baseline parser (BeautifulSoup / lxml)
    │   └── data_extractor_fast.py  → Optimized parser (selectolax / lexbor) + single-item API
    └── common/common_tools.py      → perf_test harness
```

**Pipeline Flow:**
1.  `get_listings(pages)` - Fetch paginated hotel listing HTML with Gaussian-distributed sleep (2-4s) as a polite rate-limiting measure 
2.  `extract_listings()` - Parse hotel name, star rating, detail page link
3.  `get_emails(links)` - Fetch detail pages for encoded contacts
4.  `extract_emails()` - Decode `data-mailto-token` via custom Caesar-cipher-like decoder
5.  Export to `hotel_details.csv` (UTF-8-SIG)

### Key Engineering Decisions

**1. Dual Extractor Strategy**
- `DataExtractor` (BeautifulSoup): Readable, robust, great for debugging selectors
- `DataExtractorFast` (Selectolax + Lexbor): C-based, ~130x faster. Used for production. Chose Lexbor over html5lib for speed while keeping CSS selector support.

**2. Custom Decoder**
```python
def _decoder(self, string, offset=1):
    # Reverse-engineered obfuscation: handles edge cases for 'a', '@', '_' 
    # bytearray + latin1 for performance over string concatenation
```
Instead of regex replace, operates on bytearray for O(n) decoding with minimal allocations.

**3. Resilience**
- Proxy support via `requests` proxies dict
- `DEBUG_MODE` loads `sample_responses.json` from env — allows offline development & CI without hitting live site
- Config via `.env` (`BASE_URL`, `FILTER_URL`, `DEBUG_MODE`) — no hardcoded sensitive information

**4. Performance Testing Built-In**
- `run_extractor_perf_test()` compares baseline vs fast vs parallelized
- `common_tools.perf_test()` runs 30 rounds with `perf_counter()` for stable avg
- `ThreadPoolExecutor` map for I/O-bound decoding — shows when parallelism helps (large samples >200)

### Tech Stack

- **Python 3**, **requests**, **BeautifulSoup4 / lxml**, **Selectolax (Lexbor)**
- **Concurrency:** `concurrent.futures.ThreadPoolExecutor`
- **Tooling:** `python-dotenv`, `pandas` (export), `pytest`-ready structure

### Results

| Parser | Avg Time (4404 contacts) | Notes |
| :--- | :--- | :--- |
| BeautifulSoup | ~18.93s | Baseline, most readable |
| Selectolax | ~0.29s | ~64.5x faster |
| Selectolax + ThreadPool | ~0.145s | ~130x+ faster |

> Numbers vary by machine; run `run_extractor_perf_test()` to reproduce.

Output: `hotel_details.csv` with columns `hotel`, `rating`, `link`, `email`

### Quick Start

```bash
git clone https://github.com/ngohongxiang/data_collection_h.git
cd data_collection_h
pip install -r requirements.txt

# .env.example
# BASE_URL=https://www.example.com/
# FILTER_URL=?filter=stars
# DEBUG_MODE=True # uses sample_responses.json, no live requests

python data_collection_pipeline.py
```

For live fetch:
```bash
# Set DEBUG_MODE=False in .env and add real BASE_URL
python -c "from data_collection_pipeline import DataCollectionPipeline; DataCollectionPipeline().run()"
```

### What I'd Do Next (Scale to Production)

- Implement full `rotate_identity()` with `fake-useragent` + rotating proxy pool
- Add retries with exponential backoff, dead-letter queue for failed pages
- Schema validation with `pydantic`, logging with `structlog`

---

**Built by [Ngo Hong Xiang]** — Backend / Data Engineer focused on reliable data pipelines and performance optimization. Open to roles in Data Engineering, Platform, and Online Data Collection Infrastructure.