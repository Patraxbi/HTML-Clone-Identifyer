
from bs4 import BeautifulSoup

def compare_functionality(html_file1, html_file2):
    def extract_features(soup):
        tags = ['input', 'select', 'textarea', 'button', 'form', 'a', 'label', 'details', 'summary']
        events = ['onclick', 'onchange', 'onsubmit', 'oninput', 'onmouseover', 'onkeydown', 'onkeyup', 'onload', 'onfocus', 'onblur']
        return {
            'elements': sum(len(soup.find_all(tag)) for tag in tags),
            'events': sum(1 for tag in soup.find_all(True) for e in events if tag.has_attr(e)),
            'scripts': len(soup.find_all("script"))
        }

    with open(html_file1, 'r', encoding='utf-8') as f1, open(html_file2, 'r', encoding='utf-8') as f2:
        s1 = BeautifulSoup(f1, 'html.parser')
        s2 = BeautifulSoup(f2, 'html.parser')

    f1, f2 = extract_features(s1), extract_features(s2)
    total = sum(max(f1[k], f2[k]) for k in f1)
    diff = sum(abs(f1[k] - f2[k]) for k in f1)
    return 100 - (diff / total) * 100 if total > 0 else 100
