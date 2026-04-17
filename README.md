# 🚀 Snapchat Stories Downloader

Application Python complète pour télécharger et fusionner les stories Snapchat.

## ✨ Fonctionnalités

- 📥 **Téléchargement parallèle** - Téléchargez plusieurs stories simultanément
- 🔗 **Extraction automatique** - Détecte automatiquement les stories depuis une URL
- 📂 **Organisation automatique** - Crée un dossier par utilisateur
- 🎬 **Fusion des vidéos** - Combine toutes les stories en une seule vidéo avec FFmpeg
- ✨ **Transitions fluides** - Ajoute des effets de fondu entre les vidéos
- 🖥️ **Interface graphique** - Interface moderne et intuitive (CustomTkinter)
- 💻 **Ligne de commande** - Utilisable aussi en CLI

## 📋 Prérequis

- Python 3.8 ou supérieur
- FFmpeg (pour la fusion des vidéos) - optionnel mais recommandé

## 🚀 Installation

### 1. Installer Python

Téléchargez Python depuis [python.org](https://python.org) et cochez "Add Python to PATH" pendant l'installation.

### 2. Télécharger l'application

```bash
git clone https://github.com/votre-repo/snapchat-stories-downloader.git
cd snapchat-stories-downloader
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer FFmpeg (optionnel mais recommandé)

**Windows - Méthode automatique:**
```bash
python install_ffmpeg.py
```

**Windows - Manuel:**
1. Téléchargez FFmpeg depuis [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extrayez dans `C:\Program Files\FFmpeg`
3. Ajoutez `C:\Program Files\FFmpeg\bin` au PATH système

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

## 🎯 Utilisation

### Interface Graphique (Recommandé)

```bash
python main.py --gui
# ou simplement
python gui.py
```

### Ligne de Commande

**Téléchargement simple:**
```bash
python main.py "https://snapchat.com/t/i9nYZgjr"
```

**Avec fusion des vidéos:**
```bash
python main.py "https://snapchat.com/t/i9nYZgjr" --merge
```

**Avec transitions:**
```bash
python main.py "https://snapchat.com/t/i9nYZgjr" --merge --with-transitions
```

**Options complètes:**
```bash
python main.py "https://www.snapchat.com/add/citizennasri" \
  --output ./mes_stories \
  --concurrent 3 \
  --merge \
  --with-transitions \
  --no-keep-individual
```

### Options disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| `--output, -o` | Dossier de sortie | `downloads` |
| `--concurrent, -c` | Téléchargements simultanés (1-5) | `3` |
| `--merge, -m` | Fusionner en une vidéo | `False` |
| `--with-transitions, -t` | Ajouter des transitions | `False` |
| `--no-keep-individual` | Supprimer fichiers individuels | `False` |
| `--ffmpeg-path` | Chemin FFmpeg | `ffmpeg` |
| `--gui` | Lancer interface graphique | `False` |

## 📁 Structure des fichiers

```
snapchat-stories-downloader/
├── main.py                 # Point d'entrée principal
├── gui.py                  # Interface graphique
├── snapchat_downloader.py  # Logique de téléchargement
├── video_merger.py         # Fusion vidéo avec FFmpeg
├── install_ffmpeg.py       # Script d'installation FFmpeg
├── requirements.txt        # Dépendances Python
└── README.md              # Documentation
```

## 🔧 Fonctionnement technique

### 1. Extraction des URLs

L'application utilise plusieurs méthodes pour extraire les URLs des stories:
- API Snapchat Web
- Services tiers (Snapify, etc.)
- Parsing HTML de la page publique

### 2. Téléchargement parallèle

Les stories sont téléchargées en parallèle avec:
- `asyncio` pour la gestion asynchrone
- `aiohttp` pour les requêtes HTTP
- Limite de concurrence configurable (1-5 simultanés)

### 3. Fusion des vidéos

Les vidéos sont fusionnées avec FFmpeg:
- Normalisation au format 9:16 (1080x1920)
- Concaténation simple ou avec transitions
- Format de sortie MP4 haute qualité

## 🎨 Format de sortie

### Stories individuelles
```
downloads/
└── username/
    ├── 0001_username_1234567890.mp4
    ├── 0002_username_1234567891.jpg
    ├── 0003_username_1234567892.mp4
    └── ...
```

### Vidéo fusionnée (avec --merge)
```
downloads/
└── username/
    ├── 0001_username_1234567890.mp4
    ├── ...
    └── username_montage.mp4  ← Vidéo finale
```

## ⚠️ Limitations

- Les stories privées ne peuvent pas être téléchargées
- Les stories expirées (>24h) ne sont pas accessibles
- Nécessite un lien public valide
- Le profil doit être public

## 🔒 Confidentialité

- Aucune donnée utilisateur n'est stockée
- Téléchargement anonyme
- Les fichiers restent sur votre ordinateur

## 🐛 Dépannage

### "FFmpeg non trouvé"
```bash
# Vérifier l'installation
ffmpeg -version

# Si non installé, exécuter:
python install_ffmpeg.py
```

### "Aucune story trouvée"
- Vérifiez que le lien est public
- Assurez-vous que les stories n'ont pas expiré
- Essayez avec un autre profil public

### "Erreur de téléchargement"
- Vérifiez votre connexion internet
- Réduisez le nombre de téléchargements simultanés: `--concurrent 1`
- Essayez à nouveau (les APIs peuvent être temporairement indisponibles)

## 📜 Licence

Ce projet est fourni à titre éducatif. Respectez les conditions d'utilisation de Snapchat.

## 🙏 Remerciements

- FFmpeg - Outil de traitement vidéo
- CustomTkinter - Interface graphique moderne
- aiohttp - Requêtes HTTP asynchrones

## 🤝 Contribution

Les contributions sont les bienvenues! Ouvrez une issue ou une pull request.

---

**⚠️ Avertissement:** Cet outil est destiné à un usage personnel et éducatif. Respectez les droits d'auteur et la vie privée des utilisateurs.