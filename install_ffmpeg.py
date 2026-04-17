#!/usr/bin/env python3
"""
Script d'installation automatique de FFmpeg pour Windows
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path


def is_admin():
    """Vérifie si le script s'exécute en administrateur"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def download_file(url: str, dest: str) -> bool:
    """Télécharge un fichier avec barre de progression"""
    try:
        print(f"⬇️  Téléchargement depuis: {url}")
        print("   Cela peut prendre quelques minutes...")
        
        def report_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            size_mb = total_size / (1024 * 1024)
            sys.stdout.write(f"\r   Progression: {percent:.1f}% ({downloaded/(1024*1024):.1f}/{size_mb:.1f} MB)")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, dest, reporthook=report_hook)
        print("\n✅ Téléchargement terminé!")
        return True
    except Exception as e:
        print(f"\n❌ Erreur de téléchargement: {e}")
        return False


def install_ffmpeg_windows():
    """Installe FFmpeg sur Windows"""
    print("=" * 70)
    print("🎬 Installation de FFmpeg pour Windows")
    print("=" * 70)
    
    # Vérifier si FFmpeg est déjà installé
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"✅ FFmpeg est déjà installé: {ffmpeg_path}")
        return True
    
    # URLs des versions FFmpeg
    ffmpeg_urls = [
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    ]
    
    # Créer un dossier temporaire
    temp_dir = Path(os.environ.get('TEMP', 'C:\\temp')) / "ffmpeg_install"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = temp_dir / "ffmpeg.zip"
    extract_path = temp_dir / "extracted"
    
    # Télécharger
    downloaded = False
    for url in ffmpeg_urls:
        if download_file(url, str(zip_path)):
            downloaded = True
            break
    
    if not downloaded:
        print("❌ Impossible de télécharger FFmpeg")
        print("💡 Veuillez l'installer manuellement depuis:")
        print("   https://ffmpeg.org/download.html#build-windows")
        return False
    
    # Extraire
    print("\n📦 Extraction des fichiers...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print("✅ Extraction terminée!")
    except Exception as e:
        print(f"❌ Erreur d'extraction: {e}")
        return False
    
    # Trouver le dossier bin
    bin_path = None
    for root, dirs, files in os.walk(extract_path):
        if "bin" in dirs:
            potential_bin = Path(root) / "bin"
            if (potential_bin / "ffmpeg.exe").exists():
                bin_path = potential_bin
                break
    
    if not bin_path:
        print("❌ Impossible de trouver les exécutables FFmpeg")
        return False
    
    print(f"📁 Dossier FFmpeg trouvé: {bin_path}")
    
    # Copier vers un emplacement permanent
    install_dir = Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / "FFmpeg"
    install_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📂 Installation dans: {install_dir}")
    
    # Copier les fichiers
    try:
        for file in bin_path.glob("*"):
            dest = install_dir / file.name
            if file.is_file():
                shutil.copy2(file, dest)
        print("✅ Fichiers copiés!")
    except Exception as e:
        print(f"⚠️  Erreur lors de la copie: {e}")
        print("   Tentative en mode utilisateur...")
        install_dir = Path.home() / "FFmpeg"
        install_dir.mkdir(exist_ok=True)
        for file in bin_path.glob("*"):
            dest = install_dir / file.name
            if file.is_file():
                shutil.copy2(file, dest)
    
    # Ajouter au PATH
    print("\n📝 Configuration du PATH...")
    try:
        import winreg
        
        # Ouvrir la clé PATH
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # Lire le PATH actuel
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except:
            current_path = ""
        
        # Vérifier si FFmpeg n'est pas déjà dans le PATH
        if str(install_dir) not in current_path:
            new_path = f"{current_path};{install_dir}" if current_path else str(install_dir)
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            print("✅ PATH mis à jour!")
        else:
            print("✅ FFmpeg déjà dans le PATH")
            
    except Exception as e:
        print(f"⚠️  Impossible de modifier le PATH automatiquement: {e}")
        print(f"💡 Ajoutez manuellement au PATH:\n   {install_dir}")
    
    # Nettoyer
    print("\n🧹 Nettoyage...")
    try:
        shutil.rmtree(temp_dir)
    except:
        pass
    
    print("\n" + "=" * 70)
    print("✅ Installation terminée!")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: Redémarrez votre terminal ou votre ordinateur")
    print("   pour que les modifications du PATH prennent effet.")
    print("\n🎬 Vous pouvez maintenant utiliser la fonction de fusion des vidéos!")
    print("=" * 70)
    
    return True


def install_ffmpeg_linux():
    """Installe FFmpeg sur Linux"""
    print("Installation sur Linux...")
    print("Exécutez: sudo apt-get update && sudo apt-get install -y ffmpeg")
    print("Ou: sudo yum install -y ffmpeg")
    return False


def install_ffmpeg_macos():
    """Installe FFmpeg sur macOS"""
    print("Installation sur macOS...")
    print("Exécutez: brew install ffmpeg")
    return False


def main():
    """Point d'entrée principal"""
    system = sys.platform
    
    if system == "win32":
        if install_ffmpeg_windows():
            input("\nAppuyez sur Entrée pour quitter...")
    elif system == "darwin":
        install_ffmpeg_macos()
    else:
        install_ffmpeg_linux()


if __name__ == "__main__":
    main()