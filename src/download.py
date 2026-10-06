import os
from pathlib import Path
from dotenv import load_dotenv
from edgar import Company, set_identity

TICKERS = ["AAPL", "JPM", "WMT"]
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def download_10k(ticker: str) -> str:
    company = Company(ticker)
    filings = company.get_filings(form="10-K")
    filing = filings.latest() if filings else None
    if not filing or not getattr(filing, "period_of_report", None):
        raise ValueError(f"[{ticker}] Latest 10-K filing or period_of_report is unavailable.")

    fiscal_year = filing.period_of_report[:4]
    filepath = RAW_DIR / f"{ticker}_{fiscal_year}_10K.html"

    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"{ticker}: Filing date {filing.filing_date} | Skipped (Already exists: {size_kb:.1f} KB)")
        return "skipped"

    html_content = filing.html()
    if not html_content:
        raise ValueError(f"[{ticker}] HTML content for 10-K filing is empty or None.")

    tmp_filepath = RAW_DIR / f"{ticker}_{fiscal_year}_10K.tmp"
    tmp_filepath.write_text(html_content, encoding="utf-8")
    tmp_filepath.replace(filepath)

    size_kb = filepath.stat().st_size / 1024
    print(f"{ticker}: Filing date {filing.filing_date} | Downloaded ({size_kb:.1f} KB)")
    return "downloaded"


def main() -> None:
    load_dotenv()
    identity = os.getenv("EDGAR_IDENTITY", "")
    if not identity or "@" not in identity:
        raise ValueError("EDGAR_IDENTITY environment variable missing or invalid (must contain email with '@').")

    set_identity(identity)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    summary = {"downloaded": 0, "skipped": 0, "failed": 0}
    for ticker in TICKERS:
        try:
            status = download_10k(ticker)
            summary[status] += 1
        except Exception as err:
            print(f"{ticker}: Failed - {err}")
            summary["failed"] += 1

    print(f"\nSummary: {summary['downloaded']} downloaded / {summary['skipped']} skipped / {summary['failed']} failed")


if __name__ == "__main__":
    main()
