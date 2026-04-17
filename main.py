#!/usr/bin/env python3
"""
Snapchat Stories Downloader - Application Complète
Télécharge et fusionne les stories Snapchat
"""

import sys
import argparse
from pathlib import Path
from snapchat_downloader import SnapchatDownloader
from video_merger import VideoMerger, check_ffmpeg_installed, install_ffmpeg_instructions


def main():
    """Point d'entrée principal avec interface en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Téléchargeur de Stories Snapchat avec fusion vidéo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s "https://snapchat.com/t/i9nYZgjr"
  %(prog)s "https://www.snapchat.com/add/citizennasri" --merge --output ./mes_stories
  %(prog)s "https://snapchat.com/t/abc123" --merge --with-transitions --no-keep-individual

Note: Nécessite FFmpeg installé pour la fusion des vidéos.
        """
    )
    
    parser.add_argument(
        "url",
        help="URL du profil Snapchat ou de la story"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="downloads",
        help="Dossier de sortie (défaut: downloads)"
    )
    
    parser.add_argument(
        "-c", "--concurrent",
        type=int,
        default=3,
        choices=range(1, 6),
        metavar="1-5",
        help="Nombre de téléchargements simultanés (défaut: 3)"
    )
    
    parser.add_argument(
        "-m", "--merge",
        action="store_true",
        help="Fusionner toutes les vidéos en une seule"
    )
    
    parser.add_argument(
        "-t", "--with-transitions",
        action="store_true",
        help="Ajouter des transitions entre les vidéos (nécessite --merge)"
    )
    
    parser.add_argument(
        "--no-keep-individual",
        action="store_true",
        help="Supprimer les fichiers individuels après fusion"
    )
    
    parser.add_argument(
        "--ffmpeg-path",
        default="ffmpeg",
        help="Chemin vers l'exécutable FFmpeg (défaut: ffmpeg)"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Lancer l'interface graphique"
    )
    
    args = parser.parse_args()
    
    # Lancer l'interface graphique si demandé
    if args.gui:
        from gui import run_gui
        run_gui()
        return
    
    # Vérifier FFmpeg si fusion demandée
    if args.merge:
        if not check_ffmpeg_installed():
            install_ffmpeg_instructions()
            print("\n❌ Veuillez installer FFmpeg pour utiliser la fonction de fusion.")
            sys.exit(1)
    
    # Télécharger les stories
    print("=" * 70)
    print("🚀 Snapchat Stories Downloader - Téléchargement")
    print("=" * 70)
    
    downloader = SnapchatDownloader(args.output)
    success = downloader.download_sync(args.url, args.concurrent)
    
    if not success:
        print("\n❌ Le téléchargement a échoué.")
        sys.exit(1)
    
    # Fusionner les vidéos si demandé
    if args.merge:
        print("\n" + "=" * 70)
        print("🎬 Fusion des vidéos")
        print("=" * 70)
        
        # Trouver le dernier dossier créé
        output_path = Path(args.output)
        username = downloader.extract_username_from_url(args.url)
        if username:
            user_dir = output_path / username
        else:
            user_dir = output_path
        
        if user_dir.exists():
            merger = VideoMerger(args.ffmpeg_path)
            result = merger.create_montage(
                user_dir,
                output_filename=f"{username}_montage.mp4" if username else "story_montage.mp4",
                keep_individual=not args.no_keep_individual,
                use_transitions=args.with_transitions
            )
            
            if result:
                print(f"\n✨ Montage final créé: {result}")
            else:
                print("\n⚠️  La fusion a échoué, mais les fichiers individuels sont conservés.")
    
    print("\n🎉 Terminé!")


if __name__ == "__main__":
    main()