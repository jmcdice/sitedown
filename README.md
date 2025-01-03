# sitedown: Site to Markdown

A Python tool that converts entire websites into a single Markdown file by crawling internal pages and converting their HTML content.

## Features

- Recursively crawls all internal pages from a starting URL
- Converts HTML to Markdown while preserving content structure
- Combines all pages into a single organized Markdown file
- Handles only internal links to maintain scope
- Gracefully manages errors from inaccessible URLs

## Installation

Requires Python 3.6+

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4 html2text
```

## Usage

Basic usage:
```bash
python sitedown.py <URL> [options]
```

Options:
```
-o, --output FILENAME    Output file path (default: output.md)
```

Example:
```bash
python sitedown.py https://example.com -o example_site.md
```

## How It Works

1. Accepts a starting URL and crawls the webpage
2. Extracts and queues all internal links (same domain)
3. Converts HTML content to Markdown using html2text
4. Combines all pages into one file, separated by headers and horizontal rules

## Output Format

The generated Markdown file structures content as:

```markdown
## Page: [URL1]
---
[Page 1 Content]

## Page: [URL2]
---
[Page 2 Content]
```

## Dependencies

- [Requests](https://docs.python-requests.org): HTTP requests
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/): HTML parsing
- [html2text](https://pypi.org/project/html2text/): HTML to Markdown conversion

## Limitations

- Works best with static sites; limited support for JavaScript-heavy content
- No depth or page count limits; may be slow on large sites
- No caching system; refetches pages on each run

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Submit a pull request

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
