# 📸 Snapchat Downloader - Réalité du Projet

## 🎯 Résumé Honnête

Ce projet est un **téléchargeur de contenus publics Snapchat** (Spotlights/Highlights), PAS un téléchargeur de stories éphémères 24h.

**Ce qui fonctionne réellement :** ✅ Télécharger les vidéos publiques d'un profil  
**Ce qui ne fonctionne PAS :** ❌ Les stories éphémères 24h (impossible techniquement)

---

## 📊 Tableau de Fonctionnalités

| Fonctionnalité | Statut | Explication |
|----------------|--------|-------------|
| **Télécharger profils publics** | ✅ **FONCTIONNE** | Spotlights, highlights, contenus permanents |
| **Télécharger stories 24h** | ❌ **IMPOSSIBLE** | Nécessite connexion + amitié + API interne |
| **Stories privées** | ❌ **IMPOSSIBLE** | Chiffrement serveur, accès restreint |
| **Fusion vidéos** | ✅ **FONCTIONNE** | FFmpeg, concaténation, transitions |
| **Interface web** | ✅ **FONCTIONNE** | Serveur Flask, upload cookies, monitoring |
| **Déploiement AWS** | ✅ **FONCTIONNE** | Docker, Ubuntu, cloud-ready |
| **Cookies Snapchat** | ✅ **FONCTIONNE** | Pour accéder à web.snapchat.com |
| **Selenium headless** | ✅ **FONCTIONNE** | Chrome automatisé, scraping web |

---

## 🎭 La Grande Illusion des "Stories"

### ❌ Pourquoi les stories 24h sont impossibles

Les stories Snapchat éphémères (24h) sont :

1. **Chiffrées** sur les serveurs Snapchat
2. **Accessibles uniquement** via l'app mobile officielle
3. **Nécessitent une connexion** active et valide
4. **Nécessitent d'être ami** avec l'utilisateur
5. **Jamais exposées** sur story.snapchat.com (web)
6. **Protégées par** Snapchat Shield (anti-scraping)

### ✅ Ce que vous téléchargez réellement

Quand vous utilisez ce tool avec `https://www.snapchat.com/add/username` :

- **Spotlights** : Contenus publics postés par l'utilisateur
- **Highlights** : Stories sauvegardées mises en avant
- **Vidéos de profil** : Contenus publics permanents

**Ce SONT PAS** les stories éphémères de 24h.

---

## 🔧 Architecture Technique

### Composants Réels

```
┌─────────────────────────────────────────────────────────┐
│  URL Profil Snapchat (snapchat.com/add/username)      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  API Server (Flask) - Port 5000                         │
│  ├─ Interface web moderne                               │
│  ├─ Upload cookies JSON                                  │
│  ├─ Monitoring temps réel                               │
│  └─ Threading pour downloads parallèles               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Selenium + Chrome Headless                             │
│  ├─ Connexion à web.snapchat.com                        │
│  ├─ Injection des cookies                               │
│  ├─ Scraping du HTML                                    │
│  ├─ Extraction des URLs de médias                       │
│  └─ Accès profil public uniquement                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Téléchargement Async (aiohttp)                         │
│  ├─ Télécharge les vidéos publiques                     │
│  ├─ Sauvegarde ordonnée (0001, 0002...)                 │
│  └─ Dossier par utilisateur                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  Fusion FFmpeg (optionnel)                              │
│  ├─ Normalisation 1080x1920 (9:16)                      │
│  ├─ Concaténation simple ou avec transitions            │
│  └─ Vidéo finale unique                                 │
└─────────────────────────────────────────────────────────┘
```

### Ce qui se passe réellement

```python
# Votre URL
https://www.snapchat.com/add/citizennasri

# Le système accède à
https://story.snapchat.com/s/citizennasri

# Et récupère
- Les spotlights publics ✅
- Les highlights sauvegardés ✅
- Les stories éphémères 24h ❌ (inaccessible)
```

---

## 🚀 Comment Utiliser (Version Réaliste)

### 1. Prérequis

- Python 3.8+
- Chrome/Chromium installé
- FFmpeg installé (optionnel mais recommandé)

### 2. Installation

```bash
git clone https://github.com/kr2m-dev/snapchat-stories-downloader.git
cd snapchat-stories-downloader
pip install -r requirements.txt
```

### 3. Lancer le serveur

```bash
python api_server.py --host 0.0.0.0 --port 5000
```

### 4. Utilisation

1. **Ouvrez** : http://localhost:5000
2. **Entrez l'URL** : `https://www.snapchat.com/add/username`
3. **Upload cookies** (optionnel mais recommandé) - voir COOKIES_GUIDE.md
4. **Cliquez** "Lancer le téléchargement"
5. **Attendez** : Le système va scraper les contenus publics

### 5. Résultat

Les fichiers sont dans :
```
downloads/
└── username/
    ├── 0001_username.mp4       ← Vidéo publique 1
    ├── 0002_username.mp4     ← Vidéo publique 2
    └── username_montage.mp4   ← Fusion (si activée)
```

---

## 🍪 Pourquoi les Cookies sont Nécessaires

Sans cookies valides de web.snapchat.com :
- ❌ Redirection vers page de login
- ❌ Accès bloqué au profil
- ❌ Aucune vidéo trouvée

Avec cookies valides :
- ✅ Accès au profil public
- ✅ Visionnage des spotlights
- ✅ Scraping possible

**Même avec cookies**, vous ne pouvez PAS accéder aux stories 24h car elles ne sont pas sur la version web.

---

## 🆚 Comparatif Honnête

| Site/Outil | Méthode | Fonctionne pour stories 24h ? | Légauté |
|------------|---------|--------------------------------|---------|
| **Ce projet** | Scraping web public | ❌ Non | ✅ Légal (contenus publics) |
| **megastory.org** | API privée/Bots | ✅ Oui (prétendu) | ⚠️ Grise (CGU) |
| **snapinsta** | Sites tiers | ❌ Non | ⚠️ Grise |
| **Bot Snapchat** | App mobile + réseau comptes | ✅ Oui | ❌ Illégal (contre CGU) |

---

## ⚠️ Limitations Techniques Confirmées

### Impossibles (2026)

1. **Stories éphémères 24h**
   - Localisation : Serveurs Snapchat uniquement
   - Accès : App mobile + amitié requise
   - Protection : Chiffrement + anti-scraping

2. **Stories privées**
   - Nécessite : Compte ami avec l'utilisateur
   - Protection : Paramètres de confidentialité

3. **Stories expirées**
   - Supprimées après 24h (par design Snapchat)

### Possibles ✅

1. **Spotlights publics**
   - Accessibles sur web.snapchat.com
   - Scrapable avec Selenium

2. **Highlights**
   - Stories sauvegardées par l'utilisateur
   - Mises en avant sur le profil

3. **Vidéos de profil**
   - Contenus publics permanents

---

## 🎯 Ce que les Utilisateurs Veulent VRAIMENT

### Demande initiale
> "Télécharger les stories Snapchat d'un utilisateur"

### Réalité
> "Télécharger les contenus publics permanents d'un profil Snapchat"

### Différence
- **Stories 24h** : Éphémères, privées, impossibles
- **Contenus publics** : Permanents, accessibles, fonctionnels

---

## 🔧 Solutions Alternatives (si besoin réel)

### Si vous voulez VRAIMENT les stories 24h :

#### Option 1 : API Snapchat Business
- **Coût** : Payant, négociation nécessaire
- **Accès** : Partenariat Snapchat requis
- **Utilisation** : Analyse marketing légale

#### Option 2 : Bot Réseau ( contre CGU )
- **Méthode** : Réseau de comptes bots qui suivent
- **Risque** : Bannissement, action légale possible
- **Complexité** : Très élevée

#### Option 3 : Screen Recording Automatisé
- **Méthode** : App mobile + capture d'écran
- **Outils** : Appium, scrcpy, ffmpeg
- **Limitation** : Nécessite appareil physique

#### Option 4 : Collaboration avec l'Utilisateur
- **Méthode** : L'utilisateur partage ses stories
- **Légauté** : 100% légal avec consentement

---

## ✅ Ce que vous avez REELLEMENT

Un **outil fonctionnel et légal** pour :

1. ✅ Scraper les profils Snapchat publics
2. ✅ Télécharger les spotlights/highlights
3. ✅ Fusionner les vidéos avec FFmpeg
4. ✅ Interface web professionnelle
5. ✅ Déploiement AWS/Ubuntu
6. ✅ Support cookies pour authentification
7. ✅ Téléchargement parallèle
8. ✅ Monitoring temps réel

---

## 📝 Conclusion

### Ce projet est :
- ✅ **Techniquement impressionnant**
- ✅ **Fonctionnel** pour son usage réel
- ✅ **Légal** (contenus publics uniquement)
- ❌ **Pas un téléchargeur de stories 24h**

### Pourquoi c'est quand même utile :
- Beaucoup de contenus Snapchat sont publics (Spotlights)
- L'outil fonctionne bien pour ça
- Interface propre et moderne
- Déployable sur serveur

### Recommandation :
**Gardez ce projet** comme "Snapchat Public Downloader" ou "Snapchat Spotlight Downloader". Ne prétendez pas que ça télécharge des stories 24h.

---

## 🆘 Support

Si vous avez des questions sur les limitations ou besoin d'aide pour l'utilisation réelle (contenus publics), ouvrez une issue sur GitHub.

**URL du projet** : https://github.com/kr2m-dev/snapchat-stories-downloader

---

*Document créé le 17 avril 2026 - Version réaliste et honnête du projet*