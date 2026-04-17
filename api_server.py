#!/usr/bin/env python3
"""
API Server pour Snapchat Stories Downloader
Serveur Flask headless pour AWS/Ubuntu
Tout s'exécute côté serveur avec sa bande passante
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import asyncio

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import du downloader
try:
    from snapchat_pro_downloader import SnapchatProDownloader as SnapchatDownloader
    logger.info("Using PRO downloader with direct scraping")
except ImportError:
    from selenium_downloader import SeleniumSnapchatDownloader as SnapchatDownloader
    logger.info("Using Selenium downloader")
from video_merger import VideoMerger

app = Flask(__name__)
CORS(app)

# Configuration
DOWNLOAD_DIR = Path(os.environ.get('DOWNLOAD_DIR', './downloads'))
DOWNLOAD_DIR.mkdir(exist_ok=True)
MAX_CONCURRENT = int(os.environ.get('MAX_CONCURRENT', '3'))

# Stockage des téléchargements en cours
downloads: Dict[str, dict] = {}


HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snapchat Stories Downloader - Serveur</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            padding: 40px 0;
        }
        
        h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #fffc00, #ff0050);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #888;
            font-size: 1.1em;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 0.9em;
        }
        
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #fffc00;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, #fffc00, #ff0050);
            border: none;
            border-radius: 10px;
            color: #000;
            font-size: 1.2em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            opacity: 0.9;
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .status.success {
            background: rgba(0,255,0,0.1);
            border: 1px solid #0f0;
            display: block;
        }
        
        .status.error {
            background: rgba(255,0,0,0.1);
            border: 1px solid #f00;
            display: block;
        }
        
        .status.loading {
            background: rgba(255,252,0,0.1);
            border: 1px solid #fffc00;
            display: block;
        }
        
        .downloads-list {
            margin-top: 30px;
        }
        
        .download-item {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .download-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .download-id {
            font-family: monospace;
            color: #fffc00;
        }
        
        .download-status {
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-pending { background: #666; }
        .status-downloading { background: #fffc00; color: #000; }
        .status-merging { background: #ff9900; color: #000; }
        .status-completed { background: #0f0; color: #000; }
        .status-failed { background: #f00; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #fffc00, #ff0050);
            transition: width 0.3s;
        }
        
        .download-links {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }
        
        .download-links a {
            color: #fffc00;
            text-decoration: none;
            font-size: 0.9em;
        }
        
        .download-links a:hover {
            text-decoration: underline;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #fffc00;
        }
        
        .stat-label {
            color: #888;
            font-size: 0.9em;
        }
        
        .logs {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
            white-space: pre-wrap;
        }
        
        .log-entry {
            margin-bottom: 5px;
            padding: 3px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .log-time {
            color: #666;
        }
        
        @media (max-width: 600px) {
            h1 { font-size: 1.8em; }
            .card { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📸 Snapchat Stories Downloader</h1>
            <p class="subtitle">Serveur AWS/Ubuntu - Exécution côté serveur</p>
        </header>
        
        <div class="card">
            <div class="input-group">
                <label for="url">🔗 URL Snapchat (story ou profil)</label>
                <input type="text" id="url" placeholder="https://snapchat.com/t/... ou https://www.snapchat.com/add/...">
            </div>
            
            <div class="input-group">
                <label for="cookies">🍪 Fichier cookies JSON (optionnel mais recommandé)</label>
                <input type="file" id="cookies" accept=".json" style="padding: 10px; background: rgba(0,0,0,0.3); border: 2px dashed rgba(255,255,255,0.2); border-radius: 10px; color: #fff; width: 100%;">
                <small style="color: #888; display: block; margin-top: 5px;">Sans cookies, le téléchargement échouera probablement. Voir COOKIES_GUIDE.md</small>
            </div>
            
            <div class="input-group">
                <label for="username">👤 Nom personnalisé (optionnel)</label>
                <input type="text" id="username" placeholder="Laissez vide pour auto-détection">
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="merge" checked>
                <label for="merge" style="margin: 0;">🎬 Fusionner les vidéos en une seule</label>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="transitions" checked>
                <label for="transitions" style="margin: 0;">✨ Ajouter des transitions (fade)</label>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="keepIndividual" checked>
                <label for="keepIndividual" style="margin: 0;">💾 Conserver les fichiers individuels</label>
            </div>
            
            <button id="downloadBtn" onclick="startDownload()">
                🚀 Lancer le téléchargement
            </button>
            
            <div id="status" class="status"></div>
        </div>
        
        <div class="card">
            <h2>📊 Statistiques</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="statTotal">0</div>
                    <div class="stat-label">Téléchargements</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statActive">0</div>
                    <div class="stat-label">En cours</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statCompleted">0</div>
                    <div class="stat-label">Terminés</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statFailed">0</div>
                    <div class="stat-label">Échoués</div>
                </div>
            </div>
        </div>
        
        <div class="card downloads-list">
            <h2>📥 Téléchargements récents</h2>
            <div id="downloadsList"></div>
        </div>
        
        <div class="card">
            <h2>📝 Logs serveur</h2>
            <div id="logs" class="logs">En attente de connexion...</div>
        </div>
    </div>
    
    <script>
        let downloadId = null;
        let statusInterval = null;
        let logsInterval = null;
        
async function startDownload() {
    const url = document.getElementById('url').value.trim();
    const username = document.getElementById('username').value.trim();
    const merge = document.getElementById('merge').checked;
    const transitions = document.getElementById('transitions').checked;
    const keepIndividual = document.getElementById('keepIndividual').checked;
    const cookiesFile = document.getElementById('cookies').files[0];

    if (!url) {
        showStatus('Veuillez entrer une URL', 'error');
        return;
    }

    const btn = document.getElementById('downloadBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Téléchargement en cours...';
    showStatus('Téléchargement démarré côté serveur...', 'loading');

    try {
        // Upload cookies si fourni
        if (cookiesFile) {
            showStatus('Upload des cookies...', 'loading');
            const cookiesForm = new FormData();
            cookiesForm.append('file', cookiesFile);
            
            const cookiesResponse = await fetch('/api/cookies', {
                method: 'POST',
                body: cookiesForm
            });
            
            const cookiesData = await cookiesResponse.json();
            if (!cookiesData.success) {
                showStatus('Erreur upload cookies: ' + cookiesData.error, 'error');
                btn.disabled = false;
                btn.textContent = '🚀 Lancer le téléchargement';
                return;
            }
            showStatus('Cookies uploadés, démarrage du téléchargement...', 'loading');
        }

        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                url: url,
                username: username,
                merge: merge,
                transitions: transitions,
                keep_individual: keepIndividual
            })
        });

        const data = await response.json();

        if (data.success) {
            downloadId = data.download_id;
            showStatus(`Téléchargement démarré! ID: ${downloadId}`, 'loading');
            startStatusPolling();
        } else {
            showStatus(data.error || 'Erreur inconnue', 'error');
            btn.disabled = false;
            btn.textContent = '🚀 Lancer le téléchargement';
        }
    } catch (error) {
        showStatus('Erreur de connexion au serveur', 'error');
        btn.disabled = false;
        btn.textContent = '🚀 Lancer le téléchargement';
    }
}
        
        function startStatusPolling() {
            if (statusInterval) clearInterval(statusInterval);
            if (logsInterval) clearInterval(logsInterval);
            
            statusInterval = setInterval(async () => {
                await updateStatus();
            }, 2000);
            
            logsInterval = setInterval(async () => {
                await updateLogs();
            }, 3000);
            
            updateStatus();
            updateLogs();
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Mettre à jour les stats
                document.getElementById('statTotal').textContent = data.stats.total;
                document.getElementById('statActive').textContent = data.stats.active;
                document.getElementById('statCompleted').textContent = data.stats.completed;
                document.getElementById('statFailed').textContent = data.stats.failed;
                
                // Mettre à jour la liste
                updateDownloadsList(data.downloads);
                
                // Vérifier si notre téléchargement est terminé
                if (downloadId && data.downloads[downloadId]) {
                    const dl = data.downloads[downloadId];
                    if (dl.status === 'completed') {
                        showStatus('Téléchargement terminé!', 'success');
                        document.getElementById('downloadBtn').disabled = false;
                        document.getElementById('downloadBtn').textContent = '🚀 Lancer le téléchargement';
                        clearInterval(statusInterval);
                    } else if (dl.status === 'failed') {
                        showStatus(`Échec: ${dl.error || 'Erreur inconnue'}`, 'error');
                        document.getElementById('downloadBtn').disabled = false;
                        document.getElementById('downloadBtn').textContent = '🚀 Lancer le téléchargement';
                        clearInterval(statusInterval);
                    }
                }
            } catch (error) {
                console.error('Erreur update:', error);
            }
        }
        
        function updateDownloadsList(downloads) {
            const list = document.getElementById('downloadsList');
            let html = '';
            
            Object.entries(downloads).reverse().slice(0, 10).forEach(([id, dl]) => {
                const statusClass = `status-${dl.status}`;
                const statusText = {
                    'pending': 'En attente',
                    'downloading': 'Téléchargement...',
                    'merging': 'Fusion...',
                    'completed': 'Terminé',
                    'failed': 'Échoué'
                }[dl.status] || dl.status;
                
                let links = '';
                if (dl.files && dl.files.length > 0) {
                    links = '<div class="download-links">' + 
                        dl.files.map(f => `<a href="/api/download/${id}/${f}" target="_blank">📥 ${f}</a>`).join('') +
                        '</div>';
                }
                
                html += `
                    <div class="download-item">
                        <div class="download-header">
                            <span class="download-id">${id.substring(0, 8)}...</span>
                            <span class="download-status ${statusClass}">${statusText}</span>
                        </div>
                        <div style="color: #888; font-size: 0.9em;">${dl.url}</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${dl.progress || 0}%"></div>
                        </div>
                        ${links}
                    </div>
                `;
            });
            
            list.innerHTML = html || '<p style="color: #666; text-align: center;">Aucun téléchargement</p>';
        }
        
        async function updateLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                const logsDiv = document.getElementById('logs');
                logsDiv.innerHTML = data.logs.map(log => 
                    `<div class="log-entry"><span class="log-time">${log.time}</span> ${log.message}</div>`
                ).join('');
                logsDiv.scrollTop = logsDiv.scrollHeight;
            } catch (error) {
                console.error('Erreur logs:', error);
            }
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.className = `status ${type}`;
            status.textContent = message;
        }
        
        // Démarrer le polling au chargement
        startStatusPolling();
    </script>
</body>
</html>
"""


def download_worker(download_id: str, url: str, options: dict):
    """Thread worker pour le téléchargement"""
    logger.info(f"[Worker {download_id}] Démarrage du téléchargement pour {url}")
    
    downloads[download_id]['status'] = 'downloading'
    downloads[download_id]['progress'] = 10
    
    try:
        # Vérifier si un fichier cookies a été uploadé
        cookies_file = options.get('cookies_file')
        if not cookies_file:
            # Chercher un fichier cookies.json dans le dossier
            potential_files = ['snapchat_cookies.json', 'cookies.json']
            for f in potential_files:
                if Path(f).exists():
                    cookies_file = f
                    break
        
        # Créer le downloader
        downloader_kwargs = {
            'output_dir': str(DOWNLOAD_DIR),
            'headless': True
        }
        if cookies_file and Path(cookies_file).exists():
            downloader_kwargs['cookies_file'] = cookies_file
            logger.info(f"[Worker {download_id}] Cookies trouvés: {cookies_file}")
        
        downloader = SnapchatDownloader(**downloader_kwargs)
        
        # Télécharger
        success = downloader.download_sync(url, max_concurrent=MAX_CONCURRENT)
        
        if success:
            downloads[download_id]['progress'] = 50
            
            # Fusionner si demandé
            if options.get('merge', True):
                downloads[download_id]['status'] = 'merging'
                downloads[download_id]['progress'] = 60
                
                # Trouver le dossier créé
                username = downloader.extract_username_from_url(url)
                user_dir = DOWNLOAD_DIR / (username or "unknown")
                
                if user_dir.exists():
                    merger = VideoMerger()
                    result = merger.create_montage(
                        user_dir,
                        keep_individual=options.get('keep_individual', True),
                        use_transitions=options.get('transitions', True)
                    )
                    
                    if result:
                        logger.info(f"[Worker {download_id}] Fusion réussie: {result}")
            
            # Lister les fichiers créés
            user_dir = DOWNLOAD_DIR / (username or "unknown")
            if user_dir.exists():
                files = [f.name for f in user_dir.iterdir() if f.is_file()]
                downloads[download_id]['files'] = files
            
            downloads[download_id]['status'] = 'completed'
            downloads[download_id]['progress'] = 100
            logger.info(f"[Worker {download_id}] Téléchargement terminé avec succès")
        else:
            downloads[download_id]['status'] = 'failed'
            downloads[download_id]['error'] = 'Échec du téléchargement'
            logger.error(f"[Worker {download_id}] Échec du téléchargement")
    
    except Exception as e:
        downloads[download_id]['status'] = 'failed'
        downloads[download_id]['error'] = str(e)
        logger.error(f"[Worker {download_id}] Erreur: {e}")


@app.route('/')
def index():
    """Page d'accueil / Interface web"""
    return render_template_string(HTML_INTERFACE)


@app.route('/api/download', methods=['POST'])
def start_download():
    """Démarrer un nouveau téléchargement"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'success': False, 'error': 'URL manquante'}), 400
    
    url = data['url']
    
    if 'snapchat.com' not in url:
        return jsonify({'success': False, 'error': 'URL invalide'}), 400
    
    # Créer un ID unique
    download_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(url) % 10000}"
    
    # Initialiser le téléchargement
    downloads[download_id] = {
        'id': download_id,
        'url': url,
        'status': 'pending',
        'progress': 0,
        'created_at': datetime.now().isoformat(),
        'files': [],
        'error': None
    }
    
    # Options
    options = {
        'merge': data.get('merge', True),
        'transitions': data.get('transitions', True),
        'keep_individual': data.get('keep_individual', True)
    }
    
    # Lancer dans un thread séparé
    thread = threading.Thread(
        target=download_worker,
        args=(download_id, url, options)
    )
    thread.daemon = True
    thread.start()
    
    logger.info(f"Nouveau téléchargement démarré: {download_id} pour {url}")
    
    return jsonify({
        'success': True,
        'download_id': download_id,
        'message': 'Téléchargement démarré'
    })


@app.route('/api/status')
def get_status():
    """Obtenir le statut de tous les téléchargements"""
    stats = {
        'total': len(downloads),
        'active': sum(1 for d in downloads.values() if d['status'] in ['pending', 'downloading', 'merging']),
        'completed': sum(1 for d in downloads.values() if d['status'] == 'completed'),
        'failed': sum(1 for d in downloads.values() if d['status'] == 'failed')
    }
    
    return jsonify({
        'stats': stats,
        'downloads': downloads
    })


@app.route('/api/download/<download_id>/<filename>')
def download_file(download_id: str, filename: str):
    """Télécharger un fichier"""
    # Sécuriser le nom de fichier
    filename = secure_filename(filename)
    
    # Trouver le dossier
    for dl in downloads.values():
        if dl['id'] == download_id:
            username = dl.get('username', 'unknown')
            file_path = DOWNLOAD_DIR / username / filename
            
            if file_path.exists():
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename
                )
    
    return jsonify({'error': 'Fichier non trouvé'}), 404


@app.route('/api/logs')
def get_logs():
    """Obtenir les logs récents"""
    try:
        with open('server.log', 'r') as f:
            lines = f.readlines()[-100:]  # Dernières 100 lignes
            logs = []
            for line in lines:
                # Parser le format de log
                parts = line.strip().split(' - ', 2)
                if len(parts) >= 3:
                    logs.append({
                        'time': parts[0],
                        'level': parts[1],
                        'message': parts[2]
                    })
            return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'logs': [{'time': 'now', 'message': f'Erreur lecture logs: {e}'}]})


@app.route('/api/health')
def health_check():
    """Vérification de santé"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'downloads_active': sum(1 for d in downloads.values() if d['status'] in ['pending', 'downloading'])
    })


@app.route('/api/cookies', methods=['POST'])
def upload_cookies():
    """Upload un fichier cookies JSON"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'error': 'Le fichier doit être au format JSON'}), 400
        
        # Sauvegarder le fichier
        filename = 'snapchat_cookies.json'
        filepath = Path(filename)
        file.save(filepath)
        
        # Vérifier que c'est un JSON valide
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return jsonify({'success': False, 'error': 'Format JSON invalide - attendu une liste'}), 400
        except json.JSONDecodeError:
            filepath.unlink()
            return jsonify({'success': False, 'error': 'Fichier JSON invalide'}), 400
        
        logger.info(f"Cookies uploadés: {filepath.absolute()}")
        return jsonify({
            'success': True,
            'message': 'Cookies sauvegardés avec succès',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Erreur upload cookies: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Snapchat Stories Downloader Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host (défaut: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port (défaut: 5000)')
    parser.add_argument('--debug', action='store_true', help='Mode debug')
    
    args = parser.parse_args()
    
    logger.info(f"=" * 60)
    logger.info(f"🚀 Démarrage du serveur")
    logger.info(f"📡 Host: {args.host}:{args.port}")
    logger.info(f"📁 Downloads: {DOWNLOAD_DIR.absolute()}")
    logger.info(f"=" * 60)
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        threaded=True
    )


if __name__ == '__main__':
    main()