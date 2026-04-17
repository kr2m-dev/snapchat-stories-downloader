#!/usr/bin/env python3
"""
Script d'installation de Chrome pour Windows
Nécessaire pour Selenium
"""

import os
import sys
import urllib.request
import subprocess
from pathlib import Path


def download_file(url: str, dest: str) -> bool:
    """Télécharge un fichier"""
    try:
        print(f"⬇️  Téléchargement depuis: {url}")
        print("   Cela peut prendre quelques minutes...")
        
        def report_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            sys.stdout.write(f"\r   Progression: {percent:.1f}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, dest, reporthook=report_hook)
        print("\n✅ Téléchargement terminé!")
        return True
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


def install_chrome():
    """Installe Google Chrome sur Windows"""
    print("=" * 70)
    print("🌐 Installation de Google Chrome pour Windows")
    print("=" * 70)
    
    # Vérifier si Chrome est déjà installé
    chrome_paths = [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path(os.environ.get('LOCALAPPDATA', '')) / "Google/Chrome/Application/chrome.exe",
    ]
    
    for path in chrome_paths:
        if path.exists():
            print(f"✅ Chrome est déjà installé: {path}")
            return True
    
    # Télécharger Chrome
    temp_dir = Path(os.environ.get('TEMP', 'C:/temp'))
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    installer_path = temp_dir / "chrome_installer.exe"
    
    # URL d'installation offline de Chrome
    chrome_url = "https://dl.google.com/chrome/install/GoogleChromeStandaloneEnterprise64.msi"
    
    if not download_file(chrome_url, str(installer_path)):
        print("❌ Impossible de télécharger Chrome")
        print("💡 Alternative: Téléchargez manuellement depuis https://www.google.com/chrome/")
        return False
    
    # Installer
    print("\n📦 Installation de Chrome...")
    print("   Veuillez patienter, cela peut prendre quelques minutes...")
    
    try:
        # Installation silencieuse
        result = subprocess.run(
            ['msiexec', '/i', str(installer_path), '/qn', '/norestart'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0 or result.returncode == 3010:  # 3010 = redémarrage requis
            print("✅ Chrome installé avec succès!")
            
            # Nettoyer
            try:
                installer_path.unlink()
            except:
                pass
            
            print("\n⚠️  IMPORTANT: Redémarrez votre ordinateur pour finaliser l'installation")
            return True
        else:
            print(f"❌ Erreur d'installation: {result.returncode}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def install_chromedriver():
    """Installe ChromeDriver"""
    print("\n" + "=" * 70)
    print("🔧 Installation de ChromeDriver")
    print("=" * 70)
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ ChromeDriver sera installé automatiquement par webdriver-manager")
        return True
    except ImportError:
        print("⚠️  webdriver-manager non installé")
        print("💡 Installez avec: pip install webdriver-manager")
        return False


def main():
    """Point d'entrée principal"""
    print("\n" + "=" * 70)
    print("🚀 Installation de Chrome + ChromeDriver")
    print("=" * 70)
    print()
    
    # Installer Chrome
    chrome_ok = install_chrome()
    
    # Installer ChromeDriver (via webdriver-manager)
    driver_ok = install_chromedriver()
    
    print("\n" + "=" * 70)
    if chrome_ok:
        print("✅ Installation terminée!")
        print("=" * 70)
        print("\n⚠️  REDÉMARREZ votre ordinateur avant d'utiliser Selenium")
        print("\n🎬 Vous pouvez maintenant lancer: python api_server.py")
    else:
        print("❌ Installation échouée")
        print("=" * 70)
        print("\n💡 Installez Chrome manuellement depuis:")
        print("   https://www.google.com/chrome/")
    print("=" * 70)
    
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()