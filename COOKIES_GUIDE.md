# 🍪 Guide Cookies Snapchat - Version PRO

## 🎯 Pourquoi les cookies sont nécessaires

Snapchat bloque l'accès aux stories publiques sans session valide. Les cookies permettent au script de **simuler une connexion** et d'accéder au contenu.

---

## 📋 Méthode 1: Extension Chrome (Recommandée - Facile)

### Étape 1: Installer l'extension
1. Ouvrez Chrome
2. Allez sur le Chrome Web Store
3. Cherchez "EditThisCookie" ou "Cookie-Editor"
4. Installez l'extension

### Étape 2: Se connecter à Snapchat Web
1. Allez sur https://web.snapchat.com
2. Connectez-vous avec votre compte
3. **Important**: Laissez l'onglet ouvert

### Étape 3: Extraire les cookies
1. Cliquez sur l'icône de l'extension (dans la barre d'outils)
2. Cherchez les cookies du domaine **.snapchat.com**
3. Copiez ces cookies essentiels:
   - `_scid`
   - `_scs`
   - `sc-a-cookie`
   - `sc-cookies-accepted`
   - `web_client_id`

### Étape 4: Créer le fichier
Créez un fichier `snapchat_cookies.json`:
```json
[
  {
    "name": "_scid",
    "value": "votre_valeur_ici",
    "domain": ".snapchat.com",
    "path": "/"
  },
  {
    "name": "_scs",
    "value": "votre_valeur_ici",
    "domain": ".snapchat.com",
    "path": "/"
  },
  {
    "name": "sc-a-cookie",
    "value": "votre_valeur_ici",
    "domain": ".snapchat.com",
    "path": "/"
  }
]
```

---

## 📋 Méthode 2: Console Développeur (Plus complète)

### Étape 1: Ouvrir Snapchat Web
1. Allez sur https://web.snapchat.com
2. Connectez-vous
3. Appuyez sur **F12** pour ouvrir les outils développeur

### Étape 2: Accéder aux cookies
1. Allez dans l'onglet **Application** (ou **Stockage** sur Firefox)
2. Dans le menu de gauche, cliquez sur **Cookies**
3. Sélectionnez **https://web.snapchat.com**

### Étape 3: Copier les valeurs
Copiez ces cookies dans un fichier JSON:
```json
[
  {
    "name": "_scid",
    "value": "XXXX",
    "domain": ".snapchat.com",
    "path": "/",
    "secure": true,
    "httpOnly": false
  },
  {
    "name": "_scs",
    "value": "XXXX",
    "domain": ".snapchat.com",
    "path": "/",
    "secure": true,
    "httpOnly": false
  },
  {
    "name": "sc-a-cookie",
    "value": "XXXX",
    "domain": ".snapchat.com",
    "path": "/",
    "secure": true,
    "httpOnly": true
  },
  {
    "name": "web_client_id",
    "value": "XXXX",
    "domain": ".snapchat.com",
    "path": "/",
    "secure": true,
    "httpOnly": false
  }
]
```

### Étape 4: Sauvegarder
Sauvegardez dans `snapchat_cookies.json`

---

## 📋 Méthode 3: Script Python Automatique (Avancé)

Si vous voulez automatiser l'extraction:

```python
# save_cookies.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time

# Lancer Chrome
driver = webdriver.Chrome()
driver.get("https://web.snapchat.com")

print("Connectez-vous manuellement...")
input("Appuyez sur Entrée après connexion...")

# Sauvegarder les cookies
cookies = driver.get_cookies()
with open('snapchat_cookies.json', 'w') as f:
    json.dump(cookies, f, indent=2)

print("✅ Cookies sauvegardés!")
driver.quit()
```

---

## 🚀 Utilisation avec l'API

### Méthode 1: Ligne de commande
```bash
python snapchat_pro_downloader.py "https://snapchat.com/t/i9nYZgjr" --cookies snapchat_cookies.json
```

### Méthode 2: API Server
1. Placez le fichier `snapchat_cookies.json` dans le dossier du projet
2. Modifiez `api_server.py` pour charger automatiquement les cookies:

```python
# Dans api_server.py, ligne ~570
downloader = SnapchatProDownloader(
    output_dir=str(DOWNLOAD_DIR),
    headless=True,
    cookies_file='snapchat_cookies.json'  # Ajoutez cette ligne
)
```

### Méthode 3: Upload via l'interface web (à implémenter)
Vous pouvez ajouter une fonctionnalité pour uploader les cookies via l'interface web.

---

## ⚠️ Important - Durée de validité

Les cookies Snapchat expirent après:
- **Session**: Quand vous vous déconnectez
- **Time-based**: Souvent 30 jours

**Solution**: Rafraîchissez régulièrement vos cookies

---

## 🔒 Sécurité des cookies

⚠️ **ATTENTION**: Les cookies contiennent votre session Snapchat

- **Ne partagez JAMAIS** votre fichier cookies
- **Ne poussez PAS** sur GitHub
- Le fichier `.gitignore` ignore déjà `snapchat_cookies.json`

---

## 🧪 Test rapide

Après avoir créé le fichier cookies:

```bash
# Test ligne de commande
python snapchat_pro_downloader.py "https://snapchat.com/t/i9nYZgjr" --cookies snapchat_cookies.json

# Vous devriez voir:
# ✅ Cookies chargés depuis snapchat_cookies.json
# 👤 Utilisateur détecté: i9nYZgjr
# 🌐 Accès à https://story.snapchat.com/s/i9nYZgjr
# ✅ X stories trouvées
```

---

## 💡 Conseils

### Si ça ne marche pas:
1. Vérifiez que vous êtes bien connecté sur web.snapchat.com
2. Essayez de rafraîchir la page et de recopier les cookies
3. Vérifiez que les cookies n'ont pas expiré
4. Utilisez plus de cookies (pas seulement _scid et _scs)

### Pour les stories privées:
- Vous devez être ami avec l'utilisateur
- Les cookies doivent être d'une session connectée
- Le profil doit autoriser la visualisation

---

## 📝 Format JSON attendu

```json
[
  {
    "name": "nom_du_cookie",
    "value": "valeur_du_cookie",
    "domain": ".snapchat.com",
    "path": "/",
    "secure": true,
    "httpOnly": false
  }
]
```

---

## 🆘 Dépannage

### "Cookies invalides"
- Vérifiez le format JSON
- Assurez-vous que les cookies ne sont pas expirés
- Essayez de recopier depuis le navigateur

### "Session invalide"
- Les cookies ont probablement expiré
- Reconnectez-vous et réexportez

### "Accès refusé"
- Le profil est peut-être privé
- Vous n'êtes peut-être pas connecté avec les bons cookies

---

## ✅ Checklist

- [ ] Connecté sur web.snapchat.com
- [ ] Cookies extraits avec extension ou console
- [ ] Fichier snapchat_cookies.json créé
- [ ] Format JSON valide vérifié
- [ ] Test avec ligne de commande réussi
- [ ] Cookies NE PAS pousser sur GitHub

---

**Besoin d'aide ?** Ouvrez une issue sur GitHub avec:
- Votre méthode d'extraction
- Le message d'erreur exact
- Les étapes déjà tentées