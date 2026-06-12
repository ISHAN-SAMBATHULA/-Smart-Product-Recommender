import os
import re
import textwrap

def fix_streamlit_markdown(directory="."):
    """Removes leading spaces from st.markdown HTML strings to fix rendering."""
    pattern = re.compile(r'(st\.markdown\(\s*(f?["\']{3}))([\s\S]*?)\2(\s*,\s*unsafe_allow_html=True\s*\))')
    
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Replace function
                def replacer(match):
                    prefix = match.group(1)
                    html_content = match.group(3)
                    suffix = match.group(4)
                    
                    # Split lines, strip leading whitespace, re-join
                    lines = html_content.split('\n')
                    stripped_lines = [line.lstrip() for line in lines]
                    fixed_html = '\n'.join(stripped_lines)
                    
                    return f"{prefix}{fixed_html}{match.group(2)}{suffix}"

                new_content, num_subs = pattern.subn(replacer, content)
                
                if num_subs > 0:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"Fixed {num_subs} markdown blocks in {filepath}")
                    count += 1
                    
    print(f"\nDone! Fixed HTML indentation in {count} Python files.")

if __name__ == "__main__":
    fix_streamlit_markdown()
    fix_streamlit_markdown("pages")
