import httpx
from bs4 import BeautifulSoup
from graph.state import ResearchState

MAX_URLS = 18
MAX_CHARS_PER_PAGE = 5000
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MarketResearchBot/1.0)"}


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button"]):
        tag.decompose()
    # Prefer article/main content blocks
    main = soup.find("article") or soup.find("main") or soup
    text = main.get_text(separator=" ", strip=True)
    lines = [l.strip() for l in text.splitlines() if l.strip() and len(l.strip()) > 20]
    return " ".join(lines)[:MAX_CHARS_PER_PAGE]


def scraper_node(state: ResearchState) -> dict:
    """Fetches and cleans HTML from unique URLs found in search results."""
    all_urls: set[str] = set()
    for results in state["search_results"].values():
        for r in results:
            url = r.get("url", "")
            if url and url.startswith("http"):
                all_urls.add(url)

    scraped_data: dict[str, str] = {}

    # First, use raw_content from Tavily where available (avoids scrape failures)
    for results in state["search_results"].values():
        for r in results:
            url = r.get("url", "")
            raw = r.get("raw_content", "")
            if url and raw:
                scraped_data[url] = raw[:MAX_CHARS_PER_PAGE]

    # Scrape remaining URLs that didn't have raw content
    urls_to_scrape = [u for u in list(all_urls)[:MAX_URLS] if u not in scraped_data]
    with httpx.Client(timeout=12.0, follow_redirects=True) as client:
        for url in urls_to_scrape:
            try:
                resp = client.get(url, headers=HEADERS)
                if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                    scraped_data[url] = clean_html(resp.text)
            except Exception as e:
                print(f"[Scraper] Skipped {url}: {e}")

    return {
        "scraped_data": scraped_data,
        "status": "✅ Verifier Agent: Cross-checking facts...",
    }
