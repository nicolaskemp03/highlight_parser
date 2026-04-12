# MoonReader+ Highlight Parser & Formatter

A suite of Python scripts to parse and format book highlights exported from MoonReader+ on Android (`.mrexpt` files).

## Features

1. **`moon_reader_parser.py`**: A robust parser that converts the complex `.mrexpt` format into a clean, structured JSON file.
2. **`markdown_formatter.py`**: A formatter that transforms the JSON data into Obsidian-compatible Markdown files with custom callouts and Zettelkasten-style metadata.

## Quick Start

### 1. Parse your export to JSON
```bash
python3 moon_reader_parser.py "MyBookHighlights.mrexpt"
```
This generates `MyBookHighlights.json`.

### 2. Format JSON to Markdown (Interactive)
```bash
python3 markdown_formatter.py "MyBookHighlights.json"
```
Follow the terminal prompts to provide the **Author**, **Year**, and **Short Title**. This creates a file named `Author_Year_ShortTitle.md`.

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
