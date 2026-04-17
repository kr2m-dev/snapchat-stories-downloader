#!/bin/bash
# Script de déploiement sur AWS EC2

set -e

echo "======================================"
echo "  Déploiement AWS EC2"
echo "======================================"

# Configuration
KEY_FILE="${1:-snapchat-key.pem}"
SERVER_IP="${2:-}"
USER="${3:-ubuntu}"

if [ -z "$SERVER_IP" ]; then
    echo "Usage: ./deploy_aws.sh [clé.pem] [IP_SERVEUR] [utilisateur]"
    echo "Exemple: ./deploy_aws.sh mykey.pem 3.15.227.42 ubuntu"
    exit 1
fi

echo ""
echo "Connexion à: $USER@$SERVER_IP"
echo ""

# Créer une archive du projet
echo "[1/5] Création de l'archive..."
tar -czf snapchat-downloader.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='downloads' \
    --exclude='.git' \
    --exclude='*.mp4' \
    --exclude='*.jpg' \
    *.py *.txt *.sh *.md Dockerfile

# Transférer sur le serveur
echo "[2/5] Transfert des fichiers..."
scp -i "$KEY_FILE" snapchat-downloader.tar.gz $USER@$SERVER_IP:~/

# Exécuter les commandes sur le serveur
echo "[3/5] Installation sur le serveur..."
ssh -i "$KEY_FILE" $USER@$SERVER_IP << 'EOF'
    # Mise à jour du système
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv ffmpeg chromium-browser chromium-chromedriver
    
    # Créer le répertoire de l'application
    mkdir -p ~/snapchat-downloader
    cd ~/snapchat-downloader
    
    # Extraire l'archive
    tar -xzf ~/snapchat-downloader.tar.gz
    
    # Créer l'environnement virtuel
    python3 -m venv venv
    source venv/bin/activate
    
    # Installer les dépendances
    pip install -r requirements.txt
    
    # Créer le répertoire de téléchargement
    mkdir -p downloads
    chmod 777 downloads
    
    # Configurer le firewall (si ufw est actif)
    sudo ufw allow 5000/tcp || true
    
    # Créer un service systemd
    sudo tee /etc/systemd/system/snapchat-downloader.service > /dev/null << EOFSERVICE
[Unit]
Description=Snapchat Stories Downloader
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/snapchat-downloader
Environment="PATH=/home/$USER/snapchat-downloader/venv/bin"
Environment="DOWNLOAD_DIR=/home/$USER/snapchat-downloader/downloads"
Environment="PORT=5000"
ExecStart=/home/$USER/snapchat-downloader/venv/bin/python api_server.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOFSERVICE
    
    # Recharger et démarrer le service
    sudo systemctl daemon-reload
    sudo systemctl enable snapchat-downloader
    sudo systemctl restart snapchat-downloader
    
    echo ""
    echo "======================================"
    echo "Installation terminée!"
    echo "======================================"
    echo ""
    echo "Status du service:"
    sudo systemctl status snapchat-downloader --no-pager
    echo ""
    echo "Accès: http://$(curl -s ifconfig.me):5000"
    echo ""
EOF

# Nettoyer
echo "[4/5] Nettoyage..."
rm -f snapchat-downloader.tar.gz

echo "[5/5] Terminé!"
echo ""
echo "======================================"
echo "  Déploiement réussi!"
echo "======================================"
echo ""
echo "URL d'accès: http://$SERVER_IP:5000"
echo ""
echo "Commandes utiles:"
echo "  ssh -i $KEY_FILE $USER@$SERVER_IP"
echo "  sudo systemctl status snapchat-downloader"
echo "  sudo journalctl -u snapchat-downloader -f"
echo ""