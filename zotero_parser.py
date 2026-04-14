import json
import os
import re
import datetime

class ZoteroParser:
    """
    A class to parse Zotero Markdown highlight exports.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.highlights = []

    def parse(self):
        """
        Parses the Zotero .md file and returns a list of highlight dictionaries.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} not found.")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.highlights = []
        
        # Default metadata if not found in header
        title = "Zotero Annotations"
        date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Try to parse header for title and date
        if lines and lines[0].startswith('# '):
            title = lines[0].strip('# \n')
        
        if len(lines) > 1 and '(' in lines[1]:
            # Extract date from something like (4/13/2026, 4:00:33 PM)
            date_match = re.search(r'\((.*?)\)', lines[1])
            if date_match:
                date_str = date_match.group(1)

        # Regex for Zotero annotation lines:
        # “Quote” ([Citation](zotero_link)) ([pdf](pdf_link)) User Note
        # pdf_link contains page=X and annotation=ID
        pattern = re.compile(
            r'“(?P<text>.*?)”\s*'                     # Quote text
            r'\(\[(?P<citation>.*?)\]\((?P<z_link>.*?)\)\)\s*' # Citation & Zotero link
            r'\(\[pdf\]\((?P<pdf_link>.*?)\)\)'      # PDF link
            r'(?P<note>.*)'                            # Optional user note (relevance)
        )

        for line in lines:
            line = line.strip()
            if not line.startswith('“'):
                continue

            match = pattern.search(line)
            if match:
                text = match.group('text')
                citation = match.group('citation')
                pdf_link = match.group('pdf_link')
                note = match.group('note').strip()

                # Extract page and annotation ID from PDF link
                # Example: zotero://open-pdf/library/items/UC644P8X?page=1&annotation=Y7ZMTA75
                page = "1"
                page_match = re.search(r'page=(\d+)', pdf_link)
                if page_match:
                    page = page_match.group(1)

                ann_id = "unknown"
                id_match = re.search(r'annotation=([A-Z0-9]+)', pdf_link)
                if id_match:
                    ann_id = id_match.group(1)
                
                self.highlights.append({
                    "id": ann_id,
                    "text": text,
                    "title": title,
                    "date": date_str,
                    "timestamp": 0, # Zotero export date is for the whole file
                    "page": page,
                    "note": note,
                    "metadata": {
                        "citation": citation,
                        "zotero_link": match.group('z_link'),
                        "pdf_link": pdf_link
                    }
                })
        
        return self.highlights

    def save_to_json(self, output_path=None):
        """Saves the highlights to a JSON file."""
        if not self.highlights:
            self.parse()
            
        if output_path is None:
            output_path = os.path.splitext(self.file_path)[0] + '.json'
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.highlights, f, indent=4, ensure_ascii=False)
        
        return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        print("Usage: python zotero_parser.py <Annotations.md>")
        sys.exit(1)
            
    try:
        parser = ZoteroParser(input_file)
        results = parser.parse()
        out = parser.save_to_json()
        print(f"Successfully parsed {len(results)} Zotero highlights.")
        print(f"Output saved to: {out}")
    except Exception as e:
        print(f"Error: {e}")
