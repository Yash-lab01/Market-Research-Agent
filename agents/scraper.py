import httpx
from bs4 import BeautifulSoup
from graph.state import ResearchState

MAX_URLS = 12
MAX_CHARS_PER_PAGE = 2500
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MarketResearchBot/1.0)"}


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return " ".join(lines)[:MAX_CHARS_PER_PAGE]


def scraper_node(state: ResearchState) -> dict:
    """Fetches and cleans HTML from unique URLs found in search results."""
    all_urls: set[str] = set()
    for results in state["search_results"].values():
        for r in results:
            url = r.get("url", "")
            if url:
                all_urls.add(url)

    scraped_data: dict[str, str] = {}
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        for url in list(all_urls)[:MAX_URLS]:
            try:
                resp = client.get(url, headers=HEADERS)
                if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                    scraped_data[url] = clean_html(resp.text)
            except Exception as e:
                print(f"[Scraper] Skipped {url}: {e}")
                scraped_data[url] = ""

    return {
        "scraped_data": scraped_data,
        "status": "✅ Verifier Agent: Cross-checking facts...",
    }
