import os

def fix_html_indentation(directory="."):
    """Removes leading spaces from HTML lines inside Python files to fix Streamlit rendering."""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "fix_ui_v2.py":
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.read().split('\n')
                
                new_lines = []
                changed = False
                for line in lines:
                    stripped = line.lstrip()
                    # If the line is an indented HTML tag, strip its indentation
                    if line.startswith(' ') and stripped.startswith('<') and '>' in stripped:
                        new_lines.append(stripped)
                        changed = True
                    else:
                        new_lines.append(line)
                
                if changed:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write('\n'.join(new_lines))
                    print(f"Fixed HTML indentation in {filepath}")
                    count += 1
                    
    print(f"\nDone! Successfully fixed HTML indentation in {count} Python files.")

if __name__ == "__main__":
    fix_html_indentation()
