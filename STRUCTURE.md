# 📂 Structure du Projet

```
snapchat-stories-downloader/
│
├── 📄 main.py                      # Point d'entrée principal (CLI)
│
├── 🖥️  gui.py                       # Interface graphique (CustomTkinter)
│
├── 📥 snapchat_downloader.py       # Logique de téléchargement
│   └── Class: SnapchatDownloader
│       - Extraction des URLs des stories
│       - Téléchargement parallèle
│       - Conservation de l'ordre chronologique
│
├── 🎬 video_merger.py             # Fusion des vidéos avec FFmpeg
│   └── Class: VideoMerger
│       - Normalisation du format (9:16)
│       - Concaténation simple
│       - Transitions (fade)
│
├── 🔧 install_ffmpeg.py           # Script d'installation FFmpeg (Windows)
│
├── 🚀 build_executable.py         # Création d'exécutable standalone
│
├── ▶️  run.bat                     # Lanceur Windows (double-clic)
│
├── 📋 requirements.txt            # Dépendances Python
│
├── 📝 __init__.py                 # Package initialization
│
├── 📖 README.md                   # Documentation complète
│
└── 📚 GUIDE_RAPIDE.md             # Guide de démarrage rapide
```

## 🔗 Flux de données

```
┌─────────────────────────────────────────────────────────┐
│  URL Snapchat (story ou profil)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  snapchat_downloader.py                                 │
│  ├─ Extraction du username                              │
│  ├─ Appel des APIs (snapchat.com, etc.)                 │
│  ├─ Parsing des médias                                  │
│  └─ Récupération des URLs des stories                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Téléchargement asynchrone (asyncio + aiohttp)          │
│  ├─ Création d'un dossier par utilisateur               │
│  ├─ Téléchargement parallèle (3 simultanés)             │
│  └─ Sauvegarde avec nom ordonné (0001, 0002, etc.)      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  video_merger.py (optionnel - si --merge)               │
│  ├─ Normalisation en 1080x1920 (format mobile)        │
│  ├─ Concaténation avec FFmpeg                           │
│  ├─ Ajout de transitions (optionnel)                    │
│  └─ Création du montage final                           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Résultat                                               │
│  downloads/username/                                    │
│  ├── 0001_username_1234567890.mp4                       │
│  ├── 0002_username_1234567891.mp4                       │
│  ├── ...                                                │
│  └── username_montage.mp4  ← Vidéo finale fusionnée     │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Points clés

### Conservation de l'ordre
- Les stories sont numérotées (0001, 0002, etc.)
- Le timestamp est inclus dans le nom de fichier
- Tri automatique avant fusion

### Format de sortie
- **Résolution:** 1080x1920 (9:16, format mobile)
- **Codec:** H.264 (libx264)
- **Audio:** AAC 128kbps
- **Container:** MP4

### Performances
- Téléchargement parallèle configurable (1-5)
- Timeout de 60 secondes par fichier
- Gestion des erreurs et reprises

## 🛠️ Dépendances principales

| Package | Usage |
|---------|-------|
| `requests` | Requêtes HTTP synchrones |
| `aiohttp` | Requêtes HTTP asynchrones |
| `aiofiles` | Opérations fichiers async |
| `beautifulsoup4` | Parsing HTML |
| `customtkinter` | Interface graphique moderne |

## 🔌 APIs utilisées

L'application essaie plusieurs sources pour récupérer les stories:

1. **Snapchat Web** - API officielle (si accessible)
2. **Snapify** - Service tiers
3. **Snapdownloader** - Service alternatif
4. **Parsing HTML** - Fallback si les APIs échouent

## 📱 Interface graphique

### Composants
- **Champ URL:** Avec bouton "Coller"
- **Exemples:** Liens de test prédéfinis
- **Options:** Dossier, concurrence, fusion, transitions
- **Barre de progression:** Avec pourcentage
- **Journal:** Log en temps réel

### Fonctionnalités
- Gestion des erreurs avec messages explicites
- Threading pour ne pas bloquer l'interface
- Vérification automatique de FFmpeg
- Menu d'aide intégré