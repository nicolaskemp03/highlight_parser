# MoonReader+ & Zotero Highlight Parser & Formatter

A suite of Python scripts to parse and format book highlights exported from different applications into a unified format.

## Features

1. **Unified Schema**: All parsers output a consistent JSON format (`id`, `text`, `title`, `date`, `page`, `note`, `metadata`).
2. **`moon_reader_parser.py`**: Parses MoonReader+ `.mrexpt` files.
3. **`zotero_parser.py`**: Parses Zotero Markdown annotation exports. It automatically maps user notes to the "relevance" field.
4. **`markdown_formatter.py`**: Transforms the unified JSON into Obsidian-compatible Markdown files with custom callouts.

## Quick Start

### 1. Parse your export to JSON
For MoonReader:
```bash
python3 moon_reader_parser.py "MyBook.mrexpt"
```
For Zotero:
```bash
python3 zotero_parser.py "Annotations.md"
```

### 2. Format JSON to Markdown (Interactive)
```bash
python3 markdown_formatter.py "Annotations.json"
```
Follow the terminal prompts for **Author**, **Year**, and **Short Title**. User notes from the source will appear in the `[relevance:: ...]` field.

## Metadata Formatting

The Markdown file uses the following format for each highlight:

> [!quote] Quote Title: Quote 71
> "Quote text goes here."
> 
> [source:: [[Author_Year_ShortTitle]]] [page:: 3223] [topic:: #tag1 #tag2] [relevance:: relevant]
> 
> ^71

## Developer Usage

Both scripts are designed using **OOP (Object-Oriented Programming)** and can be imported as modules:

```python
from moon_reader_parser import MoonReaderParser
from markdown_formatter import MarkdownFormatter

# Parse
parser = MoonReaderParser("file.mrexpt")
data = parser.parse()

# Format
formatter = MarkdownFormatter(data=data)
formatter.set_source_info("Smith", 2023, "BookTitle")
formatter.generate_markdown()
```

## Repository Structure

- `moon_reader_parser.py`: Core parser class and CLI utility.
- `markdown_formatter.py`: Markdown generation class and TUI utility.
- `.gitignore`: Excludes generated `.json` and highlight `.md` files to keep the repo clean.
