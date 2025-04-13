import os
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

def compare_text(html_file1, html_file2):
    # Load and parse the HTML files
    with open(html_file1, 'r', encoding='utf-8') as file:
        soup1 = BeautifulSoup(file, 'html.parser')
    
    with open(html_file2, 'r', encoding='utf-8') as file:
        soup2 = BeautifulSoup(file, 'html.parser')
    
    # Extract text content
    text1 = soup1.get_text(strip=True)
    text2 = soup2.get_text(strip=True)
    
    # Calculate similarity ratio
    similarity_ratio = SequenceMatcher(None, text1, text2).ratio()
    similarity_score = int(similarity_ratio * 100)  # Convert to a percentage

    return similarity_score

def compare_layout(html_file1, html_file2):
    # Load and parse the HTML files
    with open(html_file1, 'r', encoding='utf-8') as file:
        soup1 = BeautifulSoup(file, 'html.parser')
    
    with open(html_file2, 'r', encoding='utf-8') as file:
        soup2 = BeautifulSoup(file, 'html.parser')
    
    # Extract the layout structure (i.e., the HTML tag names)
    layout1 = [tag.name for tag in soup1.find_all(True)]
    layout2 = [tag.name for tag in soup2.find_all(True)]
    
    # Get unique tags and common tags
    unique_tags1 = set(layout1)
    unique_tags2 = set(layout2)
    common_tags = unique_tags1.intersection(unique_tags2)
    
    # Calculate the layout similarity score
    total_unique_tags = len(unique_tags1.union(unique_tags2))
    if total_unique_tags == 0:  # Avoid division by zero
        return 100  # Both files have no tags, consider them identical
    
    layout_similarity_score = int((len(common_tags) / total_unique_tags) * 100)

    return layout_similarity_score


coef_text = 0.4
coef_layout = 0.6


# Base path to the directory containing the tire folders
base_path = os.path.join(os.getcwd(), 'clones')

# List of tire directories
tire_dirs = ['tier1', 'tier2', 'tier3', 'tier4']

# Filter only .html files
tire_files = {tire: [file for file in os.listdir(os.path.join(base_path, tire)) 
                     if os.path.isfile(os.path.join(base_path, tire, file)) and file.endswith('.html')] 
                         for tire in tire_dirs}


# Create a dictionary to hold groups for each tire
tire_groups = {tire: [] for tire in tire_dirs}

# Group files based on similarity
for tire in tire_dirs:
    for file in tire_files[tire]:
        added_to_group = False
        print(f"Processing file: {file} in {tire}, nr of groups: {len(tire_groups[tire])}")
        # Compare with existing groups
        for group in tire_groups[tire]:
            representative = group[0]
            text_similarity = compare_text(
                                os.path.join(base_path, tire, file),
                                os.path.join(base_path, tire, representative)
                            )
            layout_similarity = compare_layout(
                                os.path.join(base_path, tire, file),
                                os.path.join(base_path, tire, representative)
                            )
            # Define thresholds for similarity
            # text similarity >= 60% (it's considered close match in documentation) 
            # layout similarity >= 80% ( personal it's a good match)

            added_to_group = coef_text * text_similarity + coef_layout * layout_similarity >= 70 
            # exceptional cases ( text is not the same but the layout is perfect)
            if layout_similarity >= 90: # takes in accound small color differences
                added_to_group = True

            if text_similarity >= 80: # in documentation everything above 60 is close match
                added_to_group = True

            if added_to_group:
                group.append(file)
                break

        if not added_to_group:
            # If there is no group at all, create a group
            # and add the file to it
            tire_groups[tire].append([file])
            added_to_group = True


# Write the grouped files to groups.txt
output_file = os.path.join(os.getcwd(), 'groups.txt')

with open(output_file, 'w', encoding='utf-8') as f:
    for tire, groups in tire_groups.items():
        f.write(f"{tire}\n")
        for group in groups:
            f.write(f"{group}\n")
        f.write("\n")

print(f"Grouped files have been written to {output_file}")