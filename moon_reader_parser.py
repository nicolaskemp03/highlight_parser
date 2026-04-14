import json
import os
import datetime

class MoonReaderParser:
    """
    A class to parse MoonReader+ (.mrexpt) highlight files.
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.highlights = []

    def parse(self):
        """
        Parses the .mrexpt file and returns a list of highlight dictionaries.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File {self.file_path} not found.")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # The file starts with some header info and uses '#' as an entry separator.
        # Entries are typically separated by '\n#\n'.
        blocks = content.split('\n#\n')
        
        # Reset highlights list in case parse is called multiple times
        self.highlights = []

        # blocks[0] is the file header (e.g., version info)
        for block in blocks[1:]:
            lines = block.strip('\n').split('\n')
            
            # A valid entry should have at least 13 lines:
            # 10 metadata, 2 empty, at least 1 text line, 3 trailing '0's.
            if len(lines) < 13:
                continue
            
            try:
                # Metadata fields (standard MoonReader format)
                entry_id = lines[0]
                title = lines[1]
                path = lines[2]
                chapter_index = lines[4]
                # Start position in the file
                pos = lines[6]
                # Length of the highlight
                length = lines[7]
                # Color code (can be negative for ARGB)
                color = lines[8]
                # Timestamp in milliseconds
                ts_ms = int(lines[9])
                
                # Convert timestamp to human-readable format
                date_str = datetime.datetime.fromtimestamp(ts_ms / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

                # Highlight text starts at line 12 (0-indexed)
                # The last 3 lines of each block are consistently '0'
                # We also skip the two empty lines (10 and 11)
                text_lines = lines[12:-3]
                highlight_text = '\n'.join(text_lines).strip()
                
                # Remove common MoonReader artifacts if they exist (optional)
                highlight_text = highlight_text.replace('<BR>', '\n')

                self.highlights.append({
                    "id": entry_id,
                    "text": highlight_text,
                    "title": title,
                    "date": date_str,
                    "timestamp": ts_ms,
                    "page": pos,
                    "note": "", # MoonReader doesn't have a separate note field per highlight usually
                    "metadata": {
                        "path": path,
                        "chapter_index": chapter_index,
                        "length": length,
                        "color": color
                    }
                })
            except (ValueError, IndexError):
                # Skip malformed blocks
                continue
        
        return self.highlights

    def save_to_json(self, output_path=None):
        """
        Saves the parsed highlights to a JSON file.
        If output_path is None, it uses the input filename with .json extension.
        """
        if not self.highlights:
            self.parse()
            
        if output_path is None:
            output_path = os.path.splitext(self.file_path)[0] + '.json'
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.highlights, f, indent=4, ensure_ascii=False)
        
        return output_path

if __name__ == "__main__":
    import sys
    
    # Check for command line argument or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Looking for any .mrexpt file in the current directory if none provided
        mrexpt_files = [f for f in os.listdir('.') if f.endswith('.mrexpt')]
        if mrexpt_files:
            input_file = mrexpt_files[0]
            print(f"No input file provided. Using: {input_file}")
        else:
            print("Usage: python moon_reader_parser.py <file.mrexpt>")
            sys.exit(1)
            
    try:
        parser = MoonReaderParser(input_file)
        results = parser.parse()
        out = parser.save_to_json()
        print(f"Successfully parsed {len(results)} highlights.")
        print(f"Output saved to: {out}")
    except Exception as e:
        print(f"Error: {e}")
