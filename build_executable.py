#!/usr/bin/env python3
"""
Script de création d'un exécutable standalone
Utilise PyInstaller pour créer un fichier .exe
"""

import subprocess
import sys
import shutil
from pathlib import Path


def check_pyinstaller():
    """Vérifie que PyInstaller est installé"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Installe PyInstaller"""
    print("📦 Installation de PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installé!")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def build_executable():
    """Crée l'exécutable"""
    print("=" * 70)
    print("🚀 Création de l'exécutable Snapchat Stories Downloader")
    print("=" * 70)
    
    # Vérifier PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    # Nettoyer les anciens builds
    print("\n🧹 Nettoyage des anciens builds...")
    for folder in ["build", "dist"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
    
    # Créer le fichier .spec si nécessaire
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'requests',
        'aiohttp',
        'aiofiles',
        'bs4',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SnapchatStoriesDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
'''
    
    with open('SnapchatStoriesDownloader.spec', 'w') as f:
        f.write(spec_content)
    
    # Commande PyInstaller
    print("\n🔨 Création de l'exécutable...")
    print("   Cela peut prendre plusieurs minutes...")
    print()
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SnapchatStoriesDownloader",
        "--clean",
        "--noconfirm",
        "gui.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n" + "=" * 70)
            print("✅ Exécutable créé avec succès!")
            print("=" * 70)
            print(f"\n📦 Emplacement: {Path('dist/SnapchatStoriesDownloader.exe').absolute()}")
            print("\n💡 Vous pouvez maintenant:")
            print("   1. Distribuer ce fichier .exe")
            print("   2. Le déplacer où vous voulez")
            print("   3. Le lancer sans avoir Python installé")
            print("\n⚠️  Note: FFmpeg doit toujours être installé séparément pour la fusion des vidéos")
            print("=" * 70)
            return True
        else:
            print("❌ Erreur lors de la création")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def create_installer():
    """Crée un installateur (optionnel avec NSIS)"""
    print("\n📦 Création d'un installateur...")
    print("   (Nécessite NSIS: https://nsis.sourceforge.io/)")
    
    nsis_script = '''; Snapchat Stories Downloader Installer
!include "MUI2.nsh"

!define APPNAME "Snapchat Stories Downloader"
!define COMPANYNAME "SnapchatDownloader"
!define DESCRIPTION "Téléchargeur de stories Snapchat"
!define VERSION "1.0.0"

Name "${APPNAME}"
OutFile "SnapchatStoriesDownloader_Setup.exe"
InstallDir "$PROGRAMFILES64\\${APPNAME}"
InstallDirRegKey HKCU "Software\\${APPNAME}" ""
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "French"

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\\SnapchatStoriesDownloader.exe"
    File "README.md"
    
    CreateShortcut "$SMPROGRAMS\\${APPNAME}.lnk" "$INSTDIR\\SnapchatStoriesDownloader.exe"
    CreateShortcut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\SnapchatStoriesDownloader.exe"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    WriteRegStr HKCU "Software\\${APPNAME}" "" $INSTDIR
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSION}"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\SnapchatStoriesDownloader.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\Uninstall.exe"
    
    Delete "$SMPROGRAMS\\${APPNAME}.lnk"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    
    RMDir "$INSTDIR"
    
    DeleteRegKey HKCU "Software\\${APPNAME}"
    DeleteRegKey HKCU "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
SectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    print("   Script NSIS créé: installer.nsi")
    print("   Compilez-le avec NSIS pour créer l'installateur")


def main():
    """Point d'entrée"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Créateur d'exécutable")
    parser.add_argument("--installer", action="store_true", help="Créer aussi un installateur NSIS")
    args = parser.parse_args()
    
    success = build_executable()
    
    if success and args.installer:
        create_installer()
    
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()