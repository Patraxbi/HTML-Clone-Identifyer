import os
from utils.text import compare_text
from utils.layout import compare_layout
from utils.functionality import compare_functionality
from utils.styles import compare_text_styles

coef_functionality = 0.4
coef_layout = 0.2
coef_css = 0.4
#coef_text = 0.0

base_path = os.path.join(os.getcwd(), 'clones')
tire_dirs = ['tier1', 'tier2', 'tier3', 'tier4']
tire_files = {
    tire: [f for f in os.listdir(os.path.join(base_path, tire)) if f.endswith('.html')]
    for tire in tire_dirs
}
tire_groups = {tire: [] for tire in tire_dirs}

for tire in tire_dirs:
    for file in tire_files[tire]:
        full_path = os.path.join(base_path, tire, file)
        added = False
        to_add = False
        best_group = None
        biggest = 0;
        #print(f"Processing file: {file} in {tire}, number of groups: {len(tire_groups[tire])}")
        for group in tire_groups[tire]:
            rep = group[0]
            rep_path = os.path.join(base_path, tire, rep)

            text_similarity = -1
            #text_similarity = compare_text(full_path, rep_path)
            layout_similarity = compare_layout(full_path, rep_path)
            functionality_similarity = compare_functionality(full_path, rep_path)
            css_similarity = compare_text_styles(full_path, rep_path)
            total = sum([
                #coef_text * text_similarity,
                coef_layout * layout_similarity,
                coef_functionality * functionality_similarity,
                coef_css * css_similarity
            ])
            #print(f"Comparing with {rep}: {total:.2f}% similarity, {text_similarity:.2f}% text, {layout_similarity:.2f}% layout, {functionality_similarity:.2f}% functionality, {css_similarity:.2f}% css")
            # sure the same file
            if total >= 90:
                group.append(file)
                added = True
                to_add = False
                break

            # there may be better match
            if total >= 75 and total >= biggest:
                biggest = total
                to_add = True
                best_group = group

        if to_add:
            best_group.append(file)
        elif not added:
            tire_groups[tire].append([file])
            #print(f"Creating new group with {file}")
        #print()

with open("groups.txt", 'w', encoding='utf-8') as f:
    for tire, groups in tire_groups.items():
        f.write(f"{tire}\n")
        for group in groups:
            f.write(f"{group}\n")
        f.write("\n")

