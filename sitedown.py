#!/usr/bin/env python3

import requests
import argparse
import html2text
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def get_domain(url):
    """Return the domain portion of a URL."""
    return urlparse(url).netloc

def get_path(url):
    """Return the path portion of a URL."""
    return urlparse(url).path

def is_internal_link(link, domain):
    """Check if a link belongs to the same domain."""
    parsed_link = urlparse(link)
    return parsed_link.netloc == "" or parsed_link.netloc == domain

def is_in_subpath(link, start_path):
    """
    Check if the link's path begins with the start path.
    e.g. start_path = '/quickstart' => only match /quickstart... 
    """
    parsed_link_path = get_path(link)
    # If the start_path is '/', it essentially means no restriction.
    # Otherwise, require the link path to start with start_path.
    if start_path == '/':
        return True
    return parsed_link_path.startswith(start_path)

def is_excluded(link, exclude_paths):
    """
    Check if the link's path contains any of the excluded paths (case-insensitive).
    """
    parsed_link_path = get_path(link).lower()
    for exclude in exclude_paths:
        if exclude.lower() in parsed_link_path:
            return True
    return False

def list_paths(start_url):
    """
    Crawl the website starting at start_url and collect all full URLs found.
    Returns a list of full URLs (with possible duplicates), excluding any fragment-only links.
    """
    domain = get_domain(start_url)
    start_path = get_path(start_url)

    to_visit = [start_url]
    visited = set()
    urls_found = []

    while to_visit:
        current_url = to_visit.pop()
        # Normalize current_url by stripping fragments
        parsed_current = urlparse(current_url)
        normalized_current_url = parsed_current._replace(fragment='').geturl()

        if normalized_current_url in visited:
            continue
        visited.add(normalized_current_url)

        # Fetch HTML
        print(f"Crawling: {normalized_current_url}")
        try:
            response = requests.get(normalized_current_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to retrieve {normalized_current_url}: {e}")
            continue

        # Collect the normalized URL
        urls_found.append(normalized_current_url)

        # Parse HTML and extract links
        soup = BeautifulSoup(response.text, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            href = link_tag["href"]
            # Skip links that are only fragments
            if href.startswith('#'):
                continue

            link_url = urljoin(normalized_current_url, href)
            parsed_link = urlparse(link_url)

            # Skip URLs with fragments
            if parsed_link.fragment:
                continue

            # Collect full URL without fragment
            full_url = parsed_link._replace(fragment='').geturl()
            urls_found.append(full_url)

            if (is_internal_link(full_url, domain) and 
                    full_url not in visited and 
                    is_in_subpath(full_url, start_path)):
                to_visit.append(full_url)

    return urls_found

def crawl_website(start_url, exclude_paths):
    """
    Crawl the website starting at start_url, restricted to the same domain/path.
    Excludes any URLs containing paths in exclude_paths.
    Returns a dict of {url: text_content}.
    """
    domain = get_domain(start_url)
    start_path = get_path(start_url)

    to_visit = [start_url]
    visited = set()
    pages_content = {}
    converter = html2text.HTML2Text()
    converter.ignore_links = True  # You can tweak if you want inline links

    while to_visit:
        current_url = to_visit.pop()
        # Normalize current_url by stripping fragments
        parsed_current = urlparse(current_url)
        normalized_current_url = parsed_current._replace(fragment='').geturl()

        if normalized_current_url in visited:
            continue
        visited.add(normalized_current_url)

        # Fetch HTML
        print(f"Crawling: {normalized_current_url}")
        try:
            response = requests.get(normalized_current_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to retrieve {normalized_current_url}: {e}")
            continue

        # Convert HTML → Markdown
        raw_html = response.text
        markdown_text = converter.handle(raw_html)
        pages_content[normalized_current_url] = markdown_text

        # Extract links
        soup = BeautifulSoup(raw_html, "html.parser")
        for link_tag in soup.find_all("a", href=True):
            href = link_tag["href"]
            # Skip links that are only fragments
            if href.startswith('#'):
                continue

            link_url = urljoin(normalized_current_url, href)
            parsed_link = urlparse(link_url)

            # Skip URLs with fragments
            if parsed_link.fragment:
                continue

            # Collect full URL without fragment
            full_url = parsed_link._replace(fragment='').geturl()

            if (is_internal_link(full_url, domain) and 
                    full_url not in visited and 
                    is_in_subpath(full_url, start_path) and
                    not is_excluded(full_url, exclude_paths)):
                to_visit.append(full_url)

    return pages_content

def write_markdown_file(pages_content, output_filename):
    """Write all the crawled pages into a single markdown file."""
    with open(output_filename, "w", encoding="utf-8") as f:
        for page_url, content in pages_content.items():
            f.write(f"## Page: {page_url}\n\n")
            f.write(content)
            f.write("\n\n---\n\n")

def main():
    parser = argparse.ArgumentParser(description="Crawl a website (restricted to a specific path) and save content to a markdown file.")
    parser.add_argument("url", help="The starting URL to crawl (e.g. https://example.com/quickstart)")
    parser.add_argument("-o", "--output", default="output.md", help="Output markdown file (default: output.md)")
    parser.add_argument(
        "-e", "--exclude",
        nargs='*',
        default=[],
        help="Path(s) to exclude from crawling (e.g., /release-notes/ /admin/)"
    )
    parser.add_argument(
        "-l", "--list-paths",
        action='store_true',
        help="List all paths found on the website without downloading."
    )
    args = parser.parse_args()

    if args.list_paths:
        urls = list_paths(args.url)
        for url in urls:
            print(f"Crawling: {url}")
    else:
        pages_content = crawl_website(args.url, args.exclude)
        write_markdown_file(pages_content, args.output)
        print(f"All content saved to {args.output}")

if __name__ == "__main__":
    main()

