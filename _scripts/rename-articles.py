import os
import re


script_dir = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(script_dir, "..", "_articles")
folder = os.path.abspath(folder)


def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

for filename in os.listdir(folder):
    if not filename.endswith(".md"):
        continue

    path = os.path.join(folder, filename)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    date_match = re.search(r"date:\s*([0-9\-]+)", content)
    title_match = re.search(r"title:\s*(.+)", content)

    if not date_match or not title_match:
        print("Skipping:", filename)
        continue

    date = date_match.group(1)
    title = slugify(title_match.group(1))

    new_name = f"{date}-{title}.md"
    new_path = os.path.join(folder, new_name)

    if new_name != filename:
        print(f"{filename} → {new_name}")
        os.rename(path, new_path)
    else:
        print(f"Already correct: {filename}")
