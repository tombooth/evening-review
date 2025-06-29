# evening-review

A python app that scrapes:
  - theguardian.com
  - ft.com

Where there are paywalled articles we can use archive.ph to grab a copy

It then bundles these pages up into an epub e-book and sends it to
my kindle over email.

The HTML scraped from both sites can be converted to plain text using
the ``Scraped.text()`` method which relies on
[Trafilatura](https://github.com/adbar/trafilatura).

## Development

Run `uv sync` to install dependencies

Run `uv run pytest` to run tests
