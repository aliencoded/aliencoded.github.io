import os
import re

# --- CONFIG ---
script_dir = os.path.dirname(os.path.abspath(__file__))

folders = {
    "articles": os.path.join(script_dir, "..", "_articles"),
    "videos": os.path.join(script_dir, "..", "_videos")
}

# --- FUNCTIONS ---
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def rename_files(folder):
    folder = os.path.abspath(folder)
    print(f"\nProcessing folder: {folder}\n{'-'*40}")

    for filename in os.listdir(folder):
        if not filename.endswith(".md"):
            continue

        path = os.path.join(folder, filename)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract date and title
        date_match = re.search(r"^date:\s*(.+)$", content, re.MULTILINE)
        title_match = re.search(r"^title:\s*\"?(.+?)\"?$", content, re.MULTILINE)

        if not date_match or not title_match:
            print("Skipping (missing date/title):", filename)
            continue

        date = date_match.group(1).split()[0]  # Only YYYY-MM-DD
        title_slug = slugify(title_match.group(1))

        new_name = f"{date}-{title_slug}.md"
        new_path = os.path.join(folder, new_name)

        if new_name != filename:
            print(f"{filename} → {new_name}")
            os.rename(path, new_path)
        else:
            print(f"Already correct: {filename}")


# --- RUN ---
for key, folder_path in folders.items():
    rename_files(folder_path)

print("\n✅ All done!")