import os
from pathlib import Path
from dotenv import load_dotenv
from edgar import Company, set_identity

TICKERS = ["AAPL", "JPM", "WMT"]
RAW_DIR = Path("data/raw")


def download_10k(ticker: str) -> None:
    company = Company(ticker)
    filing = company.get_filings(form="10-K").latest()
    fiscal_year = filing.period_of_report[:4]
    filepath = RAW_DIR / f"{ticker}_{fiscal_year}_10K.html"

    if filepath.exists():
        size_kb = filepath.stat().st_size / 1024
        print(f"{ticker}: Filing date {filing.filing_date} | Skipped (Already exists: {size_kb:.1f} KB)")
        return

    html_content = filing.html()
    filepath.write_text(html_content, encoding="utf-8")
    size_kb = filepath.stat().st_size / 1024
    print(f"{ticker}: Filing date {filing.filing_date} | Downloaded ({size_kb:.1f} KB)")


def main() -> None:
    load_dotenv()
    identity = os.getenv("EDGAR_IDENTITY") or f"{os.getenv('SEC_NAME', '')} {os.getenv('SEC_EMAIL', '')}".strip()
    if not identity:
        raise ValueError("Please set SEC_NAME and SEC_EMAIL in your .env file.")

    set_identity(identity)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in TICKERS:
        download_10k(ticker)


if __name__ == "__main__":
    main()
