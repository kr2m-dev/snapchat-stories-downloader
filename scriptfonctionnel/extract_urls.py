import json
import sys

def extract_video_urls(har_file):
    with open(har_file, "r", encoding="utf-8") as f:
        har = json.load(f)

    urls = []
    for entry in har["log"]["entries"]:
        url = entry["request"]["url"]
        mime = entry["response"]["content"].get("mimeType", "")
        # Filtrer uniquement les vidéos mp4 depuis sc-cdn.net
        if "sc-cdn.net" in url and ("mp4" in mime or "video" in mime):
            urls.append(url)

    # Dédoublonner tout en gardant l'ordre
    seen = set()
    unique_urls = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    # Sauvegarder dans un fichier texte
    output_file = "video_urls.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        for url in unique_urls:
            f.write(url + "\n")

    print(f"✅ {len(unique_urls)} URLs extraites → {output_file}")

if __name__ == "__main__":
    har_file = sys.argv[1] if len(sys.argv) > 1 else "snapchat.har"
    extract_video_urls(har_file)
