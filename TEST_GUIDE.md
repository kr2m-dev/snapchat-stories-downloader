# 🧪 Guide de Test - Snapchat Stories Downloader

## 📋 Sommaire
1. [Test Local (Windows)](#test-local-windows)
2. [Test avec Docker](#test-avec-docker)
3. [Test sur Serveur Ubuntu/AWS](#test-sur-serveur-ubuntuaws)
4. [Dépannage](#dépannage)

---

## 🖥️ Test Local (Windows)

### Prérequis
- Python 3.8+
- Chrome ou Chromium installé
- FFmpeg installé (optionnel mais recommandé)

### Étapes

#### 1. Installer les dépendances
```bash
cd snapchat-stories-downloader
pip install -r requirements.txt
```

#### 2. Tester l'import des modules
```bash
python -c "from selenium_downloader import SeleniumSnapchatDownloader; print('✅ OK')"
python -c "from api_server import app; print('✅ API OK')"
```

#### 3. Lancer le serveur
```bash
python api_server.py --host 0.0.0.0 --port 5000
```

Vous devriez voir :
```
🚀 Démarrage du serveur
📡 Host: 0.0.0.0:5000
📁 Downloads: C:\Users\...\downloads
```

#### 4. Ouvrir l'interface web
Dans votre navigateur, allez sur :
```
http://localhost:5000
```

Vous devriez voir l'interface avec :
- Un champ pour l'URL
- Des options (fusion, transitions, etc.)
- Un bouton "Lancer le téléchargement"

#### 5. Tester un téléchargement
1. Collez une URL Snapchat (ex: `https://snapchat.com/t/i9nYZgjr`)
2. Cliquez sur "Lancer le téléchargement"
3. Attendez (peut prendre 30-60 secondes)
4. Vérifiez les logs dans le terminal

#### 6. Vérifier les résultats
Les fichiers téléchargés sont dans :
```
snapchat-stories-downloader/downloads/[username]/
```

---

## 🐳 Test avec Docker

### Prérequis
- Docker installé
- Docker Compose (optionnel)

### Étapes

#### 1. Construire l'image
```bash
cd snapchat-stories-downloader
docker build -t snapchat-downloader .
```

**Temps estimé :** 5-10 minutes (première fois)

#### 2. Lancer le conteneur
```bash
docker run -d \
  --name snapchat-downloader \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  snapchat-downloader
```

#### 3. Vérifier les logs
```bash
docker logs -f snapchat-downloader
```

#### 4. Tester l'application
Ouvrez : `http://localhost:5000`

#### 5. Arrêter le conteneur
```bash
docker stop snapchat-downloader
docker rm snapchat-downloader
```

---

## ☁️ Test sur Serveur Ubuntu/AWS

### Méthode 1: Déploiement Automatique

#### 1. Préparer votre clé SSH
```bash
chmod 600 votre-clé.pem
```

#### 2. Lancer le script de déploiement
```bash
./deploy_aws.sh votre-clé.pem IP_DU_SERVEUR ubuntu
```

**Exemple :**
```bash
./deploy_aws.sh snapchat-key.pem 3.15.227.42 ubuntu
```

#### 3. Accéder à l'application
```
http://IP_DU_SERVEUR:5000
```

### Méthode 2: Déploiement Manuel

#### 1. Se connecter au serveur
```bash
ssh -i votre-clé.pem ubuntu@IP_DU_SERVEUR
```

#### 2. Installer les dépendances
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg chromium-browser chromium-chromedriver
```

#### 3. Transférer les fichiers
Sur votre machine locale :
```bash
scp -i votre-clé.pem -r snapchat-stories-downloader/* ubuntu@IP_DU_SERVEUR:~/snapchat-downloader/
```

#### 4. Sur le serveur, installer et lancer
```bash
ssh -i votre-clé.pem ubuntu@IP_DU_SERVEUR
cd ~/snapchat-downloader
chmod +x run_server.sh
./run_server.sh
```

#### 5. En arrière-plan (recommandé)
```bash
# Lancer avec nohup
nohup ./run_server.sh > server.log 2>&1 &

# Ou utiliser screen
screen -S snapchat
./run_server.sh
# Puis Ctrl+A, D pour détacher
```

#### 6. Configurer le pare-feu AWS
Dans la console AWS :
1. Sélectionnez votre instance EC2
2. Onglet "Security"
3. Cliquez sur le Security Group
4. "Edit inbound rules"
5. Ajoutez une règle :
   - Type : Custom TCP
   - Port : 5000
   - Source : 0.0.0.0/0 (ou votre IP seulement)
   - Description : Snapchat Downloader

---

## 🔍 Vérifications

### Tester l'API directement

#### Health check
```bash
curl http://localhost:5000/api/health
```

Réponse attendue :
```json
{
  "status": "ok",
  "timestamp": "2026-04-17T...",
  "downloads_active": 0
}
```

#### Démarrer un téléchargement
```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://snapchat.com/t/i9nYZgjr",
    "merge": true,
    "transitions": true,
    "keep_individual": true
  }'
```

Réponse :
```json
{
  "success": true,
  "download_id": "20260417_143022_1234",
  "message": "Téléchargement démarré"
}
```

#### Vérifier le statut
```bash
curl http://localhost:5000/api/status
```

#### Voir les logs
```bash
# En temps réel
tail -f server.log

# Dernieres 50 lignes
tail -n 50 server.log
```

---

## 🚨 Dépannage

### ❌ "Chrome not found" sur Ubuntu
```bash
# Installer Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# Ou Chromium
sudo apt-get install -y chromium-browser chromium-chromedriver
```

### ❌ "chromedriver not found"
```bash
# Verifier l'installation
which chromedriver
which chromium.chromedriver

# Creer un lien symbolique
sudo ln -s /usr/bin/chromedriver /usr/local/bin/chromedriver
```

### ❌ Permission denied sur downloads
```bash
chmod 777 downloads
# Ou
sudo chown -R $USER:$USER downloads
```

### ❌ Port 5000 déjà utilisé
```bash
# Trouver le processus
sudo lsof -i :5000

# Le tuer
sudo kill -9 <PID>

# Ou utiliser un autre port
python api_server.py --port 5001
```

### ❌ "No module named 'selenium'"
```bash
# Reactiver l'environnement virtuel
source venv/bin/activate

# Reinstaller
pip install selenium webdriver-manager
```

### ❌ Chrome se ferme immédiatement
```bash
# Verifier que Chrome peut s'executer en mode headless
chromium-browser --headless --disable-gpu --dump-dom https://www.google.com

# Si erreur, installer les dependances manquantes
sudo apt-get install -y libgbm1 libgtk-3-0
```

### ❌ Problèmes de mémoire sur AWS (t2.micro)
```bash
# Ajouter de la swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Rendre permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📊 Monitoring

### Utilisation CPU/Mémoire
```bash
# Sur le serveur
htop

# Ou
top
```

### Logs du service systemd
```bash
sudo journalctl -u snapchat-downloader -f
```

### Redémarrer le service
```bash
sudo systemctl restart snapchat-downloader
```

---

## ✅ Checklist de Validation

- [ ] `pip install -r requirements.txt` réussi sans erreur
- [ ] `python api_server.py` démarre sans erreur
- [ ] Interface web accessible sur `http://localhost:5000`
- [ ] Health check API répond `{"status": "ok"}`
- [ ] Test de téléchargement réussi (même si 0 stories trouvées)
- [ ] Logs montrent l'activité Selenium
- [ ] Docker build réussi (si testé)
- [ ] Déploiement AWS réussi (si testé)
- [ ] Pare-feu AWS configuré (port 5000 ouvert)
- [ ] Accès depuis internet fonctionne

---

## 💡 Conseils

### Pour le développement
```bash
# Mode debug (plus de logs)
python api_server.py --debug

# Mode verbose Selenium
export SELENIUM_LOG_LEVEL=DEBUG
```

### Pour la production
```bash
# Limiter les logs
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Utiliser un reverse proxy (nginx)
# Voir section déploiement dans README.md
```

---

**Besoin d'aide ?** Consultez le fichier `server.log` et ouvrez une issue sur GitHub avec :
1. Le contenu du log d'erreur
2. La commande utilisée
3. Votre OS et version