#!/usr/bin/env python3
"""
Fix Polish Bundle button text from "Zabezpiecz Bundle" to "Zamów Teraz"
"""

from pathlib import Path

def fix_polish_button(content):
    """Replace old Polish button text with new one"""
    # Replace "Zabezpiecz Bundle" with "Zamów Teraz"
    content = content.replace('Zabezpiecz Bundle', 'Zamów Teraz')
    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no old text found
        if 'Zabezpiecz Bundle' not in original:
            return False

        new_content = fix_polish_button(original)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix Polish Bundle button on all PL pages"""
    base_dir = Path('.')
    modified_count = 0

    pl_dir = base_dir / 'pl'

    if not pl_dir.exists():
        print("Polish directory not found!")
        return

    html_files = list(pl_dir.glob('*.html'))

    for html_file in html_files:
        if process_file(html_file):
            print(f"[OK] Fixed: {html_file}")
            modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Changed 'Zabezpiecz Bundle' -> 'Zamów Teraz'")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
