"""Script to fetch CVE data from NVD API."""

import httpx
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_recent_cves(
    days_back: int = 30,
    results_per_page: int = 50,
    output_dir: Path = Path("data/raw"),
) -> list[dict]:
    """Fetch recent CVEs from NVD API."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days_back)

    params = {
        "pubStartDate": start_date.strftime("%Y-%m-%dT00:00:00.000"),
        "pubEndDate": end_date.strftime("%Y-%m-%dT23:59:59.999"),
        "resultsPerPage": results_per_page,
    }

    logger.info(f"Fetching CVEs from {start_date} to {end_date}")

    # TODO: Implement pagination and rate limiting
    response = httpx.get(NVD_API_BASE, params=params, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    cves = data.get("vulnerabilities", [])

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"cves_{start_date.date()}_{end_date.date()}.json"
    with open(output_path, "w") as f:
        json.dump(cves, f, indent=2)

    logger.info(f"Fetched {len(cves)} CVEs, saved to {output_path}")
    return cves


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fetch_recent_cves()
