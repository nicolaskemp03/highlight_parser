import json
import os
import re

class MarkdownFormatter:
    """
    A class to format parsed MoonReader highlights into a structured Markdown file.
    """

    def __init__(self, json_path=None, data=None):
        self.data = data
        if json_path:
            self.load_json(json_path)
        
        self.author = "UnknownAuthor"
        self.year = "0000"
        self.short_title = "ShortTitle"
        self.tags = []

    def load_json(self, json_path):
        """Loads highlight data from a JSON file."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file {json_path} not found.")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def set_source_info(self, author, year, short_title):
        """Sets the metadata required for the Source Note Name."""
        self.author = author.replace(" ", "")
        self.year = str(year)
        self.short_title = short_title.replace(" ", "")

    @property
    def source_note_name(self):
        """Returns the formatted Source Note Name (Author_Year_ShortTitle)."""
        return f"{self.author}_{self.year}_{self.short_title}"

    def suggest_metadata(self):
        """
        Attempts to guess metadata from the first highlight's path and title.
        Returns a tuple of (suggested_author, suggested_year, suggested_title).
        """
        if not self.data:
            return None, None, None

        first = self.data[0]
        path = first.get("metadata", {}).get("path", "")
        full_title = first.get("title", "")

        # Try to find a 4-digit year in the path
        year_match = re.search(r'\b(19|20)\d{2}\b', path)
        s_year = year_match.group(0) if year_match else "YYYY"

        # Try to find author in path (usually after -- or before ;)
        # This is a heuristic for the specific path format seen in your file
        author_match = re.search(r'--\s*([^,-]+)', path)
        s_author = author_match.group(1).strip() if author_match else "Author"

        # Simplified title (first 2-3 words)
        s_title = "".join([w.capitalize() for w in full_title.split()[:3]])

        return s_author, s_year, s_title

    def format_quote(self, item):
        """Formats a single highlight into the requested Markdown block."""
        quote_id = item.get("id", "0")
        text = item.get("text", "")
        # Indent multi-line quotes for the Obsidian callout
        indented_text = text.replace("\n", "\n> ")
        
        pos = item.get("metadata", {}).get("position", "0")
        
        tag_str = " ".join([f"#{t}" if not t.startswith("#") else t for t in self.tags])
        
        # Structure:
        # > [!quote] Quote Title: Quote {id}
        # > "Quote text"
        # 
        # [source:: [[Source Note Name]]] [page:: position] [topic:: tags] [relevance:: filler]
        # 
        # ^id
        
        block = [
            f"> [!quote] Quote Title: Quote {quote_id}",
            f"> {indented_text}",
            "",
            f"[source:: [[{self.source_note_name}]]] [page:: {pos}] [topic:: {tag_str}] [relevance:: relevant]",
            "",
            f"^{quote_id}"
        ]
        return "\n".join(block)

    def generate_markdown(self, output_dir="."):
        """Generates the .md file."""
        if not self.data:
            raise ValueError("No data to format. Load JSON first.")

        filename = f"{self.source_note_name}.md"
        filepath = os.path.join(output_dir, filename)
        
        content = []
        content.append(f"# {self.source_note_name}\n")
        content.append(f"Source: [[{self.data[0].get('title', 'Unknown')}]]\n")
        content.append("---\n")

        for item in self.data:
            content.append(self.format_quote(item))
            content.append("\n---\n")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        
        return filepath

def run_tui(formatter):
    """Simple terminal interface for metadata gathering."""
    s_author, s_year, s_title = formatter.suggest_metadata()
    
    print("\n--- Markdown Formatter Setup ---")
    print("I've attempted to guess the metadata from your file.")
    
    author = input(f"Author [{s_author}]: ").strip() or s_author
    year = input(f"Year [{s_year}]: ").strip() or s_year
    title = input(f"Short Title [{s_title}]: ").strip() or s_title
    
    formatter.set_source_info(author, year, title)
    
    tags_raw = input("Enter tags for all quotes (comma separated, e.g. psychology, media): ").strip()
    if tags_raw:
        formatter.tags = [t.strip() for t in tags_raw.split(',')]
    
    print(f"\nTarget file: {formatter.source_note_name}.md")
    confirm = input("Proceed? (y/n): ").lower()
    if confirm != 'y':
        print("Cancelled.")
        return False
    return True

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Convert MoonReader JSON highlights to Markdown.")
    parser.add_argument("input_json", help="Path to the JSON file generated by moon_reader_parser.py")
    parser.add_argument("--author", help="Author last name")
    parser.add_argument("--year", help="Publication year")
    parser.add_argument("--title", help="Short title for the note name")
    parser.add_argument("--tags", help="Comma-separated tags (e.g. 'tag1,tag2')")
    parser.add_argument("--non-interactive", action="store_true", help="Run without TUI (requires metadata via args)")

    args = parser.parse_args()

    formatter = MarkdownFormatter(args.input_json)
    
    if args.non_interactive:
        # Validation for module-like usage: metadata is required if non-interactive
        if not (args.author and args.year and args.title):
            print("Error: Author, year, and title are required in non-interactive mode.")
            sys.exit(1)
        formatter.set_source_info(args.author, args.year, args.title)
        if args.tags:
            formatter.tags = [t.strip() for t in args.tags.split(',')]
        
        out = formatter.generate_markdown()
        print(f"File generated: {out}")
    else:
        # Interactive mode
        if run_tui(formatter):
            out = formatter.generate_markdown()
            print(f"Successfully generated: {out}")
