# Dockerfile pour Snapchat Stories Downloader
# Conçu pour AWS/Ubuntu Server

FROM ubuntu:22.04

# Éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    ffmpeg \
    chromium-browser \
    chromium-chromedriver \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libgbm1 \
    libgtk-3-0 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    fonts-liberation \
    libcurl4 \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de l'application
WORKDIR /app

# Copier les fichiers de l'application
COPY requirements.txt .
COPY *.py .
COPY run_server.sh .

# Créer un environnement virtuel et installer les dépendances
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer les dépendances Python
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Créer le répertoire de téléchargement
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Exposer le port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Commande de démarrage
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "5000"]