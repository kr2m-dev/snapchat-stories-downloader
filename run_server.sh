#!/bin/bash
# Script de démarrage du serveur pour Ubuntu

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Snapchat Stories Downloader Server${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si on est root
if [ "$EUID" -ne 0 ]; then 
    log_warn "Ce script devrait être exécuté en root pour certaines opérations"
fi

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 n'est pas installé. Installation..."
    apt-get update
    apt-get install -y python3 python3-pip python3-venv
fi

log_info "Python 3 détecté: $(python3 --version)"

# Vérifier FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    log_warn "FFmpeg n'est pas installé. Installation..."
    apt-get update
    apt-get install -y ffmpeg
fi

log_info "FFmpeg détecté: $(ffmpeg -version | head -1)"

# Vérifier Chrome/Chromium
if command -v google-chrome &> /dev/null; then
    log_info "Google Chrome détecté"
elif command -v chromium &> /dev/null; then
    log_info "Chromium détecté"
elif command -v chromium-browser &> /dev/null; then
    log_info "Chromium Browser détecté"
else
    log_warn "Chrome/Chromium n'est pas installé. Installation..."
    apt-get update
    apt-get install -y chromium-browser chromium-chromedriver
fi

# Créer l'environnement virtuel si nécessaire
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    log_info "Création de l'environnement virtuel..."
    python3 -m venv $VENV_DIR
fi

# Activer l'environnement virtuel
log_info "Activation de l'environnement virtuel..."
source $VENV_DIR/bin/activate

# Installer les dépendances
log_info "Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le répertoire de téléchargement
mkdir -p downloads
chmod 777 downloads

# Vérifier les variables d'environnement
if [ -z "$PORT" ]; then
    export PORT=5000
fi

# Configuration
export DOWNLOAD_DIR="./downloads"
export MAX_CONCURRENT=3

echo ""
log_info "======================================"
log_info "Configuration:"
log_info "  Port: $PORT"
log_info "  Dossier: $DOWNLOAD_DIR"
log_info "  Max concurrent: $MAX_CONCURRENT"
log_info "======================================"
echo ""

# Démarrer le serveur
log_info "Démarrage du serveur..."
log_info "Accès via: http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""

python3 api_server.py --host 0.0.0.0 --port $PORT