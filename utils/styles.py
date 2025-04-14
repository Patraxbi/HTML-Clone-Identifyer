import os
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

_css_cache = {}

def fetch_css(href):
    if href in _css_cache:
        return _css_cache[href]
    try:
        response = requests.get(href, timeout=5)
        if response.status_code == 200:
            _css_cache[href] = response.text
            return response.text
    except Exception as e:
        print(f"Failed to fetch CSS: {href} — {e}")
    return ""


def extract_all_styles(soup, base_path=None):
    styles = []

    # Inline styles within <style> tags
    for style in soup.find_all("style"):
        styles.append(style.string or "")


    # Takes too much time to fetch all stylesheets
    # Some even don't exist anymore or I can't access them



    # External stylesheets <link rel="stylesheet">
   # for link in soup.find_all("link", rel="stylesheet"):
    #    href = link.get("href")
     #   if not href:
      #      continue

       # if href.startswith("http"):
        #    styles.append(fetch_css(href))
       # elif base_path:
        #    try:
         #       with open(os.path.join(base_path, href), 'r', encoding='utf-8') as f:
         #           styles.append(f.read())
         #   except Exception as e:
          #      print(f"Could not read local stylesheet {href}: {e}")
    
    return "\n".join(styles)


def extract_text_styles(soup):
    styled_texts = []

    for tag in soup.find_all(string=True):
        parent = tag.parent
        if not parent or not tag.strip():
            continue

        # Check if the parent has inline styles
        style_dict = {}
        inline_style = parent.get("style", "")
        for part in inline_style.split(";"):
            if ':' in part:
                key, value = part.split(':', 1)
                style_dict[key.strip().lower()] = value.strip().lower()

        if style_dict:  # Only append if there are inline styles
            styled_texts.append(style_dict)

    return styled_texts


def compare_text_styles(html_file1, html_file2):
    with open(html_file1, 'r', encoding='utf-8') as f1, open(html_file2, 'r', encoding='utf-8') as f2:
        soup1 = BeautifulSoup(f1, 'html.parser')
        soup2 = BeautifulSoup(f2, 'html.parser')

    # Extract the raw CSS styles
    styles1 = extract_all_styles(soup1)
    styles2 = extract_all_styles(soup2)

    # Extract the inline styles from the text (element-based)
    text_styles1 = extract_text_styles(soup1)
    text_styles2 = extract_text_styles(soup2)

    total = max(len(text_styles1), len(text_styles2))
    matches = 0

    # Compare inline styles on text elements
    for s1, s2 in zip(text_styles1, text_styles2):
        overlap = set(s1.keys()) & set(s2.keys())
        if not overlap:
            continue
        similarity = sum(1 for k in overlap if s1[k] == s2[k]) / len(overlap)
        if similarity >= 0.8:
            matches += 1

    # Compare raw styles (CSS) — you could tweak this to match only important parts of the CSS
    style_similarity = 0
    if styles1 and styles2:
        style_similarity = SequenceMatcher(None, styles1, styles2).ratio() # Rough check, or refine it further

    final_similarity = (matches / total) * 100 if total > 0 else 100
    final_style_similarity = style_similarity * 100

    # You can adjust weights between inline and external CSS similarity
    final_score = int(0.8 * final_similarity + 0.2 * final_style_similarity)

    return final_score
