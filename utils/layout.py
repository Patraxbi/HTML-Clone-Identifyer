
from bs4 import BeautifulSoup, Tag
from difflib import SequenceMatcher

def get_dom_tree_structure(soup, max_depth=5):
    def traverse(node, depth):
        if not isinstance(node, Tag) or depth > max_depth:
            return []
        structure = [f"{'  ' * depth}<{node.name}>"]
        for child in getattr(node, 'children', []):
            structure.extend(traverse(child, depth + 1))
        return structure

    root = soup.body if soup.body else soup
    return traverse(root, 0)

def compare_layout(html_file1, html_file2):
    with open(html_file1, 'r', encoding='utf-8') as f1, open(html_file2, 'r', encoding='utf-8') as f2:
        soup1 = BeautifulSoup(f1, 'html.parser')
        soup2 = BeautifulSoup(f2, 'html.parser')

    s1 = "\n".join(get_dom_tree_structure(soup1))
    s2 = "\n".join(get_dom_tree_structure(soup2))
    return SequenceMatcher(None, s1, s2).ratio() * 100
