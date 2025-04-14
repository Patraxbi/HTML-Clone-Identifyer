# script to check similarity between two HTML files in a more explicit manner

import os
from utils.text import compare_text
from utils.layout import compare_layout
from utils.functionality import compare_functionality
from utils.styles import compare_text_styles


coef_text = 0.0
coef_layout = 0.2
coef_functionality = 0.4
coef_css = 0.4

html_file1 = 'clones/tier3/susuetawalinkuid.site.html'  # Replace with your first HTML file path
html_file2 = 'clones/tier3/dvnbysarah.com.html'  # Replace with your second HTML file path


# in both ways because SequenceMatcher is not symmetric

text_similarity = compare_text(html_file1, html_file2)
layout_similarity = compare_layout(html_file1, html_file2)
functionality_similarity = compare_functionality(html_file1, html_file2)
css_similarity = compare_text_styles(html_file1, html_file2)
similarity = (coef_text * text_similarity + coef_layout * layout_similarity + coef_functionality * functionality_similarity+ coef_css * css_similarity)

print(f"Text Similarity Score: {text_similarity}/100")
print(f"Layout Similarity Score: {layout_similarity}/100")
print(f"Functionality Similarity Score: {functionality_similarity}/100")
print(f"CSS Similarity Score: {css_similarity}/100")
print(f"Overall Similarity Score: {similarity}/100")
print();

text_similarity = compare_text(html_file2, html_file1)
layout_similarity = compare_layout(html_file2, html_file1)
functionality_similarity = compare_functionality(html_file2, html_file1)
css_similarity = compare_text_styles(html_file2, html_file1)
similarity = (coef_text * text_similarity + coef_layout * layout_similarity + coef_functionality * functionality_similarity+ coef_css * css_similarity)

print(f"Text Similarity Score: {text_similarity}/100")
print(f"Layout Similarity Score: {layout_similarity}/100")
print(f"Functionality Similarity Score: {functionality_similarity}/100")
print(f"CSS Similarity Score: {css_similarity}/100")
print(f"Overall Similarity Score: {similarity}/100")
