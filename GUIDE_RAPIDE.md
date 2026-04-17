# 🚀 Guide Rapide - Snapchat Stories Downloader

## 📦 Installation (5 minutes)

### 1. Installer FFmpeg (recommandé)

**Option A - Automatique (Windows):**
```
double-cliquez sur: install_ffmpeg.py
```

**Option B - Manuel:**
- Téléchargez: https://ffmpeg.org/download.html#build-windows
- Extrayez dans `C:\Program Files\FFmpeg`
- Redémarrez votre ordinateur

### 2. Installer les dépendances Python

Ouvrez un terminal dans le dossier du projet:
```bash
pip install -r requirements.txt
```

## 🎯 Utilisation

### Méthode 1: Interface Graphique (Recommandé)

```bash
python gui.py
```

Ou double-cliquez sur `run.bat`

**Étapes:**
1. Copiez-collez l'URL Snapchat
2. Cliquez sur "Télécharger"
3. Attendez la fin du téléchargement
4. La vidéo fusionnée sera créée automatiquement!

### Méthode 2: Ligne de Commande

**Télécharger + Fusionner:**
```bash
python main.py "https://snapchat.com/t/i9nYZgjr" --merge --with-transitions
```

**Télécharger seulement:**
```bash
python main.py "https://snapchat.com/t/i9nYZgjr"
```

## 📝 Exemples d'URLs

```
# Lien de story
https://snapchat.com/t/i9nYZgjr

# Lien de profil
https://www.snapchat.com/add/citizennasri
```

## ⚙️ Options avancées

```bash
# Changer le dossier de sortie
python main.py "URL" --output ./mes_stories

# Plus de téléchargements simultanés (attention à la connexion)
python main.py "URL" --concurrent 5

# Fusionner sans transitions
python main.py "URL" --merge

# Supprimer les fichiers individuels après fusion
python main.py "URL" --merge --no-keep-individual
```

## 📁 Résultat

Les fichiers sont organisés automatiquement:
```
downloads/
└── username/
    ├── 0001_username_1234567890.mp4  # Stories individuelles
    ├── 0002_username_1234567891.mp4
    ├── ...
    └── username_montage.mp4         # Vidéo fusionnée
```

## ⚠️ Résolution des problèmes

### "FFmpeg non trouvé"
- Installez FFmpeg avec `install_ffmpeg.py`
- Ou manuellement depuis https://ffmpeg.org
- **Redémarrez votre ordinateur** après l'installation

### "Aucune story trouvée"
- Vérifiez que le profil est **public**
- Assurez-vous que les stories n'ont pas **expiré** (< 24h)
- Essayez avec un autre profil public

### "Erreur de téléchargement"
- Vérifiez votre connexion internet
- Réduisez les téléchargements simultanés: `--concurrent 1`
- Certaines stories peuvent être indisponibles

## 💡 Astuces

1. **Format optimal:** Les vidéos sont automatiquement normalisées en 1080x1920 (9:16)

2. **Transitions:** Activez `--with-transitions` pour des fondus entre les stories

3. **Ordre:** Les stories sont automatiquement triées dans l'ordre chronologique

4. **Conservation:** Utilisez `--no-keep-individual` pour n'avoir que la vidéo finale

## 🎬 Créer un exécutable standalone

Pour distribuer l'application sans Python:

```bash
pip install pyinstaller
python build_executable.py
```

L'exécutable sera dans: `dist/SnapchatStoriesDownloader.exe`

## 📞 Support

En cas de problème:
1. Vérifiez que FFmpeg est bien installé: `ffmpeg -version`
2. Vérifiez les dépendances: `pip list | findstr customtkinter`
3. Consultez le fichier README.md pour plus de détails

---

**Prêt à commencer?** Lancez `python gui.py` et collez votre première URL! 🚀