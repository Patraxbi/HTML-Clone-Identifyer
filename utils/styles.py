import os
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import cssutils
import logging
cssutils.log.setLevel(logging.CRITICAL)
_css_cache = {}

VISUAL_PROPERTIES = {
    "color", "background", "background-color", "font-size", "font-family",
    "font-weight", "font-style", "text-align", "text-decoration",
    "line-height", "letter-spacing", "word-spacing", "opacity",
    "visibility", "display", "position", "z-index", "border", "margin",
    "padding", "box-shadow", "text-shadow", "overflow", "white-space",
    "text-transform", "animation", "transition"
}

def fetch_css(href):
    if href in _css_cache:
        return _css_cache[href]
    try:
        response = requests.get(href, timeout=10)
        if response.status_code == 200:
            _css_cache[href] = response.text
            return response.text
    except Exception:
        return ""

def extract_used_classes_and_tags(soup):
    used = set()
    for tag in soup.find_all(True):
        used.add(tag.name)
        classes = tag.get("class", [])
        for cls in classes:
            used.add(f".{cls}")
    return used

def extract_css_rules(css_text, used_selectors):
    matched_rules = []
    try:
        stylesheet = cssutils.parseString(css_text)
        for rule in stylesheet:
            if rule.type != rule.STYLE_RULE:
                continue
            selector_matches = any(sel in rule.selectorText for sel in used_selectors)
            if not selector_matches:
                continue
            props = {}
            for prop in rule.style:
                value = prop.value.lower()
                if "var(" in value or "calc(" in value:
                    continue
                if prop.name.lower() in VISUAL_PROPERTIES:
                    props[prop.name.lower()] = value
            if props:
                matched_rules.append((rule.selectorText, props))
    except Exception:
        pass
    return matched_rules

def extract_styles(soup, base_path=None):
    used_selectors = extract_used_classes_and_tags(soup)
    inline_styles = []
    style_tag_rules = []
    stylesheet_rules = []

    for tag in soup.find_all(string=True):
        parent = tag.parent
        if not parent or not tag.strip():
            continue
        style_dict = {}
        inline_style = parent.get("style", "")
        for part in inline_style.split(";"):
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().lower()
                value = value.strip().lower()
                if key in VISUAL_PROPERTIES:
                    style_dict[key] = value
        if style_dict:
            inline_styles.append(style_dict)

    for style in soup.find_all("style"):
        if not style.string:
            continue
        style_tag_rules.extend(extract_css_rules(style.string, used_selectors))

    for link in soup.find_all("link", rel="stylesheet"):
        href = link.get("href")
        if not href or len(href) < 5:
            continue
        if href.startswith("http"):
            css_text = fetch_css(href)
            stylesheet_rules.extend(extract_css_rules(css_text, used_selectors))

    return inline_styles, style_tag_rules, stylesheet_rules

def compare_style_blocks(rules1, rules2):
    total = max(len(rules1), len(rules2))
    matches = 0
    for r1, r2 in zip(rules1, rules2):
        overlap = set(r1.keys()) & set(r2.keys())
        if not overlap:
            continue
        similarity = sum(1 for k in overlap if r1[k] == r2[k]) / len(overlap)
        if similarity >= 0.8:
            matches += 1
    return (matches / total) * 100 if total > 0 else 100

def compare_text_styles(html_file1, html_file2):
    with open(html_file1, 'r', encoding='utf-8') as f1, open(html_file2, 'r', encoding='utf-8') as f2:
        soup1 = BeautifulSoup(f1, 'html.parser')
        soup2 = BeautifulSoup(f2, 'html.parser')

    inline1, style1, sheet1 = extract_styles(soup1)
    inline2, style2, sheet2 = extract_styles(soup2)

    inline_score = compare_style_blocks(inline1, inline2)
    style_tag_score = compare_style_blocks([r for _, r in style1], [r for _, r in style2])
    stylesheet_score = compare_style_blocks([r for _, r in sheet1], [r for _, r in sheet2])

    print(f"      -Inline Style Similarity: {inline_score:.2f}, <style> Similarity: {style_tag_score:.2f}, Stylesheet Similarity: {stylesheet_score:.2f}")

    final_score = int(0.4 * inline_score + 0.3 * style_tag_score + 0.3 * stylesheet_score)
    return final_score
