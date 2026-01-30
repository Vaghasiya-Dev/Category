import re
import json
from collections import OrderedDict
from html.parser import HTMLParser

class CategoryHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.categories = []
        self.current_text = ""
        self.in_span = False
        
    def handle_starttag(self, tag, attrs):
        if tag == "span":
            self.in_span = True
            
    def handle_endtag(self, tag):
        if tag == "span" and self.in_span:
            if self.current_text.strip():
                self.categories.append(self.current_text.strip())
            self.current_text = ""
            self.in_span = False
            
    def handle_data(self, data):
        if self.in_span:
            self.current_text += data

def extract_indent_level(style_attr):
    """Extract indent level from CSS left property"""
    match = re.search(r'left:(\d+)pt', style_attr)
    if match:
        return int(match.group(1))
    return 0

def parse_html_to_hierarchy(html_content):
    """Parse HTML and build hierarchy based on indentation"""
    # Extract all div elements with their left positions and text
    div_pattern = r'<div class="awdiv"[^>]*style="[^"]*left:(\d+)pt[^"]*"><span[^>]*>(.*?)</span>'
    matches = re.findall(div_pattern, html_content, re.DOTALL)
    
    items = []
    for left_pos, text in matches:
        text = text.strip()
        if text and text != '&amp;':
            items.append({
                'indent': int(left_pos),
                'text': text
            })
    
    return items

def build_hierarchy_tree(items):
    """Build nested hierarchy from flat list with indentation levels"""
    if not items:
        return OrderedDict()
    
    root = OrderedDict()
    stack = [(0, root)]  # (indent_level, node_dict)
    
    for item in items:
        indent = item['indent']
        text = item['text']
        
        # Pop stack until we find the correct parent level
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        
        # Create new node
        new_node = OrderedDict()
        parent_indent, parent_node = stack[-1]
        parent_node[text] = new_node
        
        # Push to stack
        stack.append((indent, new_node))
    
    return root

def html_to_json(html_content):
    """Convert HTML to JSON with correct hierarchy"""
    items = parse_html_to_hierarchy(html_content)
    hierarchy = build_hierarchy_tree(items)
    return hierarchy

if __name__ == "__main__":
    # Read HTML file
    with open("Main-Product-Category-2.html", encoding="utf-8") as f:
        html_content = f.read()
    
    # Convert to JSON
    hierarchy = html_to_json(html_content)
    
    # Save to JSON file
    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)
    
    print("✅ HTML converted to categories.json")

def iter_tree(d):
    """Helper function to count nodes"""
    for k, v in d.items():
        yield k
        if isinstance(v, dict):
            yield from iter_tree(v)

    print(f"✅ Total nodes: {sum(1 for _ in iter_tree(hierarchy))}")