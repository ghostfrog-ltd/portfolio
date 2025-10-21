from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BASE_URL = "https://www.civilservicejobs.service.gov.uk"

def scrape_jobs(role="developer"):
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set to True when stable
        page = browser.new_page()

        try:
            print("[DEBUG] Navigating to Civil Service jobs site...")
            page.goto(f"{BASE_URL}/csr/index.cgi", timeout=60000)
            page.wait_for_timeout(3000)

            if page.title() == "Quick Check Needed":
                print("[DEBUG] Bot check triggered — bypassing...")
                try:
                    page.check("input[type='checkbox']")
                    page.click("button[type='submit']")
                    page.wait_for_timeout(5000)
                except Exception as e:
                    print("[DEBUG] Bypass failed:", e)

            # Fill search field
            print("[DEBUG] Filling search with:", role)
            page.fill("input[name='what']", role)

            # Click Search
            print("[DEBUG] Clicking search...")
            page.click("input#submitSearch")

            # Wait for search results
            page.wait_for_timeout(5000)

            html = page.content()
            print("[DEBUG] Page title after search:", page.title())
            print("[DEBUG] Scraping job titles...")

            soup = BeautifulSoup(html, "html.parser")

            for h3 in soup.select("h3.search-results-job-box-title"):
                a = h3.find("a", href=True)
                if a:
                    jobs.append({
                        "title": a.get_text(strip=True),
                        "link": a["href"],
                        "summary": "Description not scraped yet"
                    })

            print(f"[DEBUG] Found {len(jobs)} '{role}' jobs.")

        finally:
            browser.close()

    return jobs
