#!/usr/bin/env python3
"""
Téléchargeur de vidéos Snapchat → AWS S3 ou stockage local EC2
Usage :
  python3 download_videos.py --mode s3   --bucket mon-bucket --prefix snapchat/
  python3 download_videos.py --mode local --output /home/ubuntu/videos/
"""

import argparse
import os
import time
import requests

# ── Optionnel : upload S3 ──────────────────────────────────────────────────────
try:
    import boto3
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

# ── Arguments ─────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Télécharge les vidéos Snapchat")
parser.add_argument("--urls",   default="video_urls.txt", help="Fichier contenant les URLs")
parser.add_argument("--mode",   choices=["s3", "local"], default="local")
parser.add_argument("--bucket", default="", help="Nom du bucket S3 (si mode=s3)")
parser.add_argument("--prefix", default="snapchat/", help="Préfixe S3 (dossier dans le bucket)")
parser.add_argument("--output", default="./videos/", help="Dossier local (si mode=local)")
parser.add_argument("--delay",  type=float, default=1.0, help="Délai entre chaque téléchargement (secondes)")
args = parser.parse_args()

# ── Préparation ───────────────────────────────────────────────────────────────
if args.mode == "local":
    os.makedirs(args.output, exist_ok=True)

if args.mode == "s3":
    if not S3_AVAILABLE:
        print("❌ boto3 non installé. Exécute : pip3 install boto3")
        exit(1)
    s3 = boto3.client("s3")

# ── Lecture des URLs ──────────────────────────────────────────────────────────
with open(args.urls, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"📋 {len(urls)} vidéos à télécharger (mode: {args.mode})\n")

# ── Téléchargement ────────────────────────────────────────────────────────────
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
    "Referer": "https://megastory.org/",
    "Accept": "video/webm,video/ogg,video/*;q=0.9,*/*;q=0.5",
}

failed = []

for i, url in enumerate(urls, start=1):
    filename = f"video_{i:04d}.mp4"  # ex: video_0001.mp4, video_0002.mp4 ...
    print(f"[{i}/{len(urls)}] Téléchargement de {filename}...", end=" ", flush=True)

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()

        if args.mode == "local":
            filepath = os.path.join(args.output, filename)
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                    f.write(chunk)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✅ sauvegardé ({size_mb:.2f} MB) → {filepath}")

        elif args.mode == "s3":
            s3_key = args.prefix + filename
            # Upload direct en streaming vers S3
            s3.upload_fileobj(
                response.raw,
                args.bucket,
                s3_key,
                ExtraArgs={"ContentType": "video/mp4"}
            )
            print(f"✅ uploadé vers s3://{args.bucket}/{s3_key}")

    except Exception as e:
        print(f"❌ ERREUR : {e}")
        failed.append((i, url, str(e)))

    time.sleep(args.delay)  # pause polie entre requêtes

# ── Résumé ────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"✅ Terminé : {len(urls) - len(failed)}/{len(urls)} vidéos téléchargées")
if failed:
    print(f"❌ {len(failed)} échec(s) :")
    for idx, url, err in failed:
        print(f"   - video_{idx:04d} : {err}")
