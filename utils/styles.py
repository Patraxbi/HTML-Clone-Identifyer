import os
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import cssutils
import logging

cssutils.log.setLevel(logging.CRITICAL)

_css_cache = {}
_style_cache = {}

VISUAL_PROPERTIES = set()  # Will be populated dynamically

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

def extract_all_properties_from_css(css_texts):
    found_properties = set()
    for css_text in css_texts:
        try:
            stylesheet = cssutils.parseString(css_text)
            for rule in stylesheet:
                if rule.type == rule.STYLE_RULE:
                    for prop in rule.style:
                        found_properties.add(prop.name.lower())
        except Exception:
            continue
    return found_properties

def extract_css_rules(css_text, used_selectors):
    key = (css_text, tuple(sorted(used_selectors)))
    if key in _style_cache:
        return _style_cache[key]

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

    _style_cache[key] = matched_rules
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
                if key in VISUAL_PROPERTIES and "var(" not in value and "calc(" not in value:
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
    style_dicts1 = [r for _, r in rules1] if rules1 and isinstance(rules1[0], tuple) else rules1
    style_dicts2 = [r for _, r in rules2] if rules2 and isinstance(rules2[0], tuple) else rules2

    total = max(len(style_dicts1), len(style_dicts2))
    if total == 0:
        return 100

    if min(len(style_dicts1), len(style_dicts2)) == 0:
        return 0
    
    matched_ratios = []
    for s1 in style_dicts1:
        best = 0
        for s2 in style_dicts2:
            overlap = set(s1.keys()) & set(s2.keys())
            if not overlap:
                continue
            similarity = sum(1 for k in overlap if SequenceMatcher(None, s1[k], s2[k]).ratio() > 0.8) / len(overlap)
            best = max(best, similarity)
        matched_ratios.append(best)
    
    if matched_ratios :
        average_similarity = sum(matched_ratios) / len(matched_ratios)

    return int(average_similarity * 100)

def compare_text_styles(html_file1, html_file2):
    global VISUAL_PROPERTIES

    with open(html_file1, 'r', encoding='utf-8') as f1, open(html_file2, 'r', encoding='utf-8') as f2:
        soup1 = BeautifulSoup(f1, 'html.parser')
        soup2 = BeautifulSoup(f2, 'html.parser')

    all_css_texts = []
    for style in soup1.find_all("style"):
        if style.string:
            all_css_texts.append(style.string)
    for style in soup2.find_all("style"):
        if style.string:
            all_css_texts.append(style.string)
    for soup in [soup1, soup2]:
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href")
            if href and href.startswith("http"):
                css_text = fetch_css(href)
                if css_text:
                    all_css_texts.append(css_text)

    VISUAL_PROPERTIES = extract_all_properties_from_css(all_css_texts)

    inline1, style1, sheet1 = extract_styles(soup1)
    inline2, style2, sheet2 = extract_styles(soup2)


    available = {
        "inline": len(inline1) > 0 or len(inline2) > 0,
        "style": len(style1) > 0 or len(style2) > 0,
        "sheet": len(sheet1) > 0 or len(sheet2) > 0
    }

    inline_score = compare_style_blocks(inline1, inline2) if available["inline"] else 0
    style_tag_score = compare_style_blocks(style1, style2) if available["style"] else 0
    stylesheet_score = compare_style_blocks(sheet1, sheet2) if available["sheet"] else 0
    
    scores = {
        "inline": inline_score ,
        "style": style_tag_score,
        "sheet": stylesheet_score 
    }

    # Original weights
    base_weights = {
        "inline": 0.33,
        "style": 0.33,
        "sheet": 0.34
    }

    # Total active weight
    total_weight = sum(base_weights[k] for k in available if available[k])

    # Redistribute weights
    final_score = 0
    for k in scores:
        if available[k]:
            weight = base_weights[k] / total_weight
            final_score += scores[k] * weight


    print(f"      -Inline Style Similarity: {scores["inline"]:.2f}, <style> Similarity: {scores["style"]:.2f}, Stylesheet Similarity: {scores["sheet"]:.2f}")
    print(f"      -Avalability: <inline> {available["inline"]}, <style> {available["style"]}, Stylesheet {available["sheet"]}")
    return final_score
