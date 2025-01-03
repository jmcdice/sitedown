#!/usr/bin/env python3

import requests
import argparse
import html2text
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def get_domain(url):
    """Return the domain portion of a URL."""
    return urlparse(url).netloc

def is_internal_link(link, domain):
    """Check if a link belongs to the same domain."""
    return urlparse(link).netloc == "" or urlparse(link).netloc == domain

def crawl_website(start_url):
    """
    Crawl the website starting at start_url, collecting the text content of each page.
    Returns a dict of {url: text_content}.
    """
    domain = get_domain(start_url)
    to_visit = [start_url]
    visited = set()
    pages_content = {}
    converter = html2text.HTML2Text()
    converter.ignore_links = True  # You can adjust if you want links in the final markdown

    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        visited.add(current_url)

        # Fetch HTML
        print(f"Crawling: {current_url}")
        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to retrieve {current_url}: {e}")
            continue

        # Convert HTML → Markdown
        raw_html = response.text
        markdown_text = converter.handle(raw_html)
        pages_content[current_url] = markdown_text

        # Extract links
        soup = BeautifulSoup(raw_html, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            link_url = urljoin(current_url, link_tag["href"])
            if is_internal_link(link_url, domain) and link_url not in visited:
                to_visit.append(link_url)

    return pages_content

def write_markdown_file(pages_content, output_filename):
    """Write all the crawled pages into a single markdown file."""
    with open(output_filename, "w", encoding="utf-8") as f:
        for page_url, content in pages_content.items():
            f.write(f"## Page: {page_url}\n\n")
            f.write(content)
            f.write("\n\n---\n\n")

def main():
    parser = argparse.ArgumentParser(description="Crawl a website and save content to a markdown file.")
    parser.add_argument("url", help="The starting URL to crawl")
    parser.add_argument("-o", "--output", default="output.md", help="Output markdown file (default: output.md)")
    args = parser.parse_args()

    pages_content = crawl_website(args.url)
    write_markdown_file(pages_content, args.output)
    print(f"All content saved to {args.output}")

if __name__ == "__main__":
    main()

