#!/usr/bin/env python3
"""
Snapchat Stories Downloader - VERSION FONCTIONNELLE
Télécharge les stories Snapchat à partir d'un lien de profil
"""

import asyncio
import aiohttp
import aiofiles
import os
import re
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import subprocess
import base64
import urllib.parse

@dataclass
class StoryItem:
    """Représente un item de story (vidéo ou image)"""
    url: str
    type: str  # 'video' ou 'image'
    index: int
    timestamp: Optional[int] = None
    username: Optional[str] = None
    
    def get_filename(self) -> str:
        """Génère un nom de fichier ordonné"""
        ext = 'mp4' if self.type == 'video' else 'jpg'
        timestamp_str = f"_{self.timestamp}" if self.timestamp else ""
        return f"{self.index:04d}_{self.username or 'story'}{timestamp_str}.{ext}"


class SnapchatDownloader:
    """Classe principale pour le téléchargement de stories Snapchat"""
    
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """Extrait le nom d'utilisateur d'une URL Snapchat"""
        patterns = [
            r'snapchat\.com/add/([^/?\s]+)',
            r'snapchat\.com/t/([^/?\s]+)',
            r'www\.snapchat\.com/add/([^/?\s]+)',
            r'story\.snapchat\.com/s/([^/?\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_story_urls_from_api(self, url: str) -> List[StoryItem]:
        """
        Essaie d'obtenir les URLs des stories via différentes méthodes
        """
        stories = []
        username = self.extract_username_from_url(url)
        
        if not username:
            print(f"❌ Impossible d'extraire le nom d'utilisateur de: {url}")
            return stories
        
        print(f"👤 Utilisateur détecté: {username}")
        
        # Méthode 1: API Snapchat Web directe
        stories = self._try_snapchat_web_api(url, username)
        if stories:
            return stories
        
        # Méthode 2: Services de téléchargement
        stories = self._try_download_services(url, username)
        if stories:
            return stories
        
        # Méthode 3: Scraping de story.snapchat.com
        stories = self._try_story_scraping(username)
        if stories:
            return stories
        
        return stories
    
    def _try_snapchat_web_api(self, url: str, username: str) -> List[StoryItem]:
        """Tente d'extraire depuis l'API web Snapchat"""
        stories = []
        
        try:
            print("🌐 Tentative d'accès via story.snapchat.com...")
            
            # Essayer d'accéder à la story publique
            story_url = f"https://story.snapchat.com/s/{username}"
            response = self.session.get(story_url, timeout=15)
            
            if response.status_code == 200:
                print("✅ Page accessible, extraction des données...")
                stories = self._extract_from_html(response.text, username)
                
                if not stories:
                    # Chercher dans les données JSON de la page
                    stories = self._extract_json_data(response.text, username)
        
        except Exception as e:
            print(f"⚠️ story.snapchat.com a échoué: {e}")
        
        return stories
    
    def _extract_from_html(self, html: str, username: str) -> List[StoryItem]:
        """Extrait les URLs depuis le HTML"""
        stories = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Chercher les meta tags pour les vidéos
            video_meta = soup.find_all('meta', property='og:video')
            for i, meta in enumerate(video_meta):
                if meta.get('content'):
                    stories.append(StoryItem(
                        url=meta['content'],
                        type='video',
                        index=i,
                        username=username
                    ))
            
            # Chercher les meta tags pour les images
            image_meta = soup.find_all('meta', property='og:image')
            for i, meta in enumerate(image_meta):
                if meta.get('content') and meta['content'] not in [s.url for s in stories]:
                    stories.append(StoryItem(
                        url=meta['content'],
                        type='image',
                        index=len(stories) + i,
                        username=username
                    ))
            
            # Chercher les balises video
            video_tags = soup.find_all('video')
            for i, video in enumerate(video_tags):
                src = video.get('src') or video.find('source').get('src') if video.find('source') else None
                if src and src not in [s.url for s in stories]:
                    stories.append(StoryItem(
                        url=src,
                        type='video',
                        index=len(stories) + i,
                        username=username
                    ))
            
            # Chercher les URLs dans les scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Chercher des URLs mp4
                    mp4_urls = re.findall(r'https?://[^\s\'"<>]+\.mp4[^\s\'"<>]*', script.string)
                    m3u8_urls = re.findall(r'https?://[^\s\'"<>]+\.m3u8[^\s\'"<>]*', script.string)
                    
                    all_urls = mp4_urls + m3u8_urls
                    for url in all_urls:
                        if url not in [s.url for s in stories]:
                            stories.append(StoryItem(
                                url=url,
                                type='video',
                                index=len(stories),
                                username=username
                            ))
        
        except Exception as e:
            print(f"⚠️ Erreur extraction HTML: {e}")
        
        return stories
    
    def _extract_json_data(self, html: str, username: str) -> List[StoryItem]:
        """Extrait les données depuis le JSON embarqué dans la page"""
        stories = []
        
        try:
            # Chercher les données JSON dans les balises script
            json_pattern = r'<script[^>]*>window\.__INITIAL_STATE__\s*=\s*({.+?})</script>'
            matches = re.findall(json_pattern, html, re.DOTALL)
            
            if not matches:
                # Pattern alternatif
                json_pattern = r'<script[^>]*>window\._state\s*=\s*({.+?})</script>'
                matches = re.findall(json_pattern, html, re.DOTALL)
            
            if not matches:
                # Pattern plus général
                json_pattern = r'window\.__INITIAL_STATE__\s*=\s*(\{[\s\S]+?\});'
                matches = re.findall(json_pattern, html)
            
            for match in matches:
                try:
                    data = json.loads(match)
                    
                    # Chercher les stories dans différentes structures possibles
                    story_list = None
                    
                    if 'story' in data:
                        story_list = data['story']
                    elif 'stories' in data:
                        story_list = data['stories']
                    elif 'props' in data and 'pageProps' in data['props']:
                        story_list = data['props']['pageProps'].get('stories', [])
                    elif 'storyPlayer' in data:
                        story_list = data['storyPlayer'].get('story', {}).get('snaps', [])
                    
                    if story_list:
                        for i, story in enumerate(story_list):
                            media_url = None
                            if isinstance(story, dict):
                                media_url = story.get('mediaUrl') or story.get('snapUrl') or story.get('url')
                                if not media_url:
                                    # Chercher dans mediaProperties
                                    media_props = story.get('mediaProperties', {})
                                    media_url = media_props.get('contentUrl') or media_props.get('secureUrl')
                            elif isinstance(story, str):
                                media_url = story
                            
                            if media_url:
                                stories.append(StoryItem(
                                    url=media_url,
                                    type='video' if '.mp4' in media_url.lower() else 'image',
                                    index=i,
                                    username=username
                                ))
                
                except json.JSONDecodeError:
                    continue
        
        except Exception as e:
            print(f"⚠️ Erreur extraction JSON: {e}")
        
        return stories
    
    def _try_download_services(self, url: str, username: str) -> List[StoryItem]:
        """Essaye les services de téléchargement"""
        stories = []
        
        # Services qui fonctionnent souvent
        services = [
            {
                'name': 'snapxdl',
                'url': 'https://snapxdl.com/api/v1/resolve',
                'method': 'post',
                'data': {'url': url},
                'headers': {'Content-Type': 'application/json'}
            },
            {
                'name': 'snapinsta',
                'url': f'https://snapinsta.app/action.php',
                'method': 'post',
                'data': {'url': url, 'action': 'post'},
            },
            {
                'name': 'savetofiles',
                'url': 'https://savetofiles.com/snapchat-downloader',
                'method': 'post',
                'data': {'url': url},
            }
        ]
        
        for service in services:
            try:
                print(f"🌐 Essai avec {service['name']}...")
                
                headers = self.session.headers.copy()
                if 'headers' in service:
                    headers.update(service['headers'])
                
                if service['method'] == 'post':
                    response = self.session.post(
                        service['url'],
                        data=service.get('data'),
                        headers=headers,
                        timeout=15
                    )
                else:
                    response = self.session.get(
                        service['url'],
                        headers=headers,
                        timeout=15
                    )
                
                if response.status_code == 200:
                    # Essayer de parser la réponse
                    try:
                        data = response.json()
                        if data:
                            # Différents formats de réponse
                            if isinstance(data, list):
                                for i, item in enumerate(data):
                                    url = item.get('url') or item.get('download_url')
                                    if url:
                                        stories.append(StoryItem(
                                            url=url,
                                            type=item.get('type', 'video'),
                                            index=i,
                                            username=username
                                        ))
                            elif isinstance(data, dict):
                                if 'data' in data:
                                    data = data['data']
                                
                                if isinstance(data, list):
                                    for i, item in enumerate(data):
                                        url = item.get('url') or item.get('download_url')
                                        if url:
                                            stories.append(StoryItem(
                                                url=url,
                                                type=item.get('type', 'video'),
                                                index=i,
                                                username=username
                                            ))
                                elif 'url' in data:
                                    stories.append(StoryItem(
                                        url=data['url'],
                                        type=data.get('type', 'video'),
                                        index=0,
                                        username=username
                                    ))
                        
                        if stories:
                            print(f"✅ Stories trouvées via {service['name']}: {len(stories)}")
                            return stories
                    
                    except ValueError:
                        # La réponse n'est pas du JSON, chercher des URLs dans le HTML
                        urls = re.findall(r'https?://[^\s\'"<>]+\.(?:mp4|jpg|jpeg|png)', response.text)
                        for i, found_url in enumerate(set(urls)):
                            stories.append(StoryItem(
                                url=found_url,
                                type='video' if '.mp4' in found_url else 'image',
                                index=i,
                                username=username
                            ))
                        
                        if stories:
                            print(f"✅ URLs trouvées via {service['name']}: {len(stories)}")
                            return stories
            
            except Exception as e:
                print(f"⚠️ {service['name']} a échoué: {str(e)[:100]}")
                continue
        
        return stories
    
    def _try_story_scraping(self, username: str) -> List[StoryItem]:
        """Scrape story.snapchat.com"""
        stories = []
        
        try:
            print("🔍 Scraping story.snapchat.com...")
            
            url = f"https://story.snapchat.com/s/{username}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Chercher toutes les URLs de médias dans le contenu
                content = response.text
                
                # Patterns pour trouver les URLs de stories
                patterns = [
                    r'"(https://[^"]*story[^"]*\.(?:mp4|jpg)[^"]*)"',
                    r'"(https://[^"]*cf\.sc-cdn\.net[^"]*\.(?:mp4|jpg)[^"]*)"',
                    r'"(https://[^"]*sc-cdn[^"]*\.(?:mp4|jpg)[^"]*)"',
                    r'url["\']?\s*[:=]\s*["\'](https?://[^"\']+\.(?:mp4|jpg))["\']',
                    r'contentUrl["\']?\s*:\s*["\'](https?://[^"\']+)["\']',
                    r'poster["\']?\s*:\s*["\'](https?://[^"\']+)["\']',
                ]
                
                all_urls = set()
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    all_urls.update(matches)
                
                # Filtrer et ajouter
                for i, media_url in enumerate(sorted(all_urls)):
                    if 'mp4' in media_url.lower():
                        stories.append(StoryItem(
                            url=media_url,
                            type='video',
                            index=i,
                            username=username
                        ))
                    elif any(ext in media_url.lower() for ext in ['jpg', 'jpeg', 'png']):
                        stories.append(StoryItem(
                            url=media_url,
                            type='image',
                            index=len(stories),
                            username=username
                        ))
                
                if stories:
                    print(f"✅ {len(stories)} médias trouvés par scraping")
        
        except Exception as e:
            print(f"⚠️ Scraping a échoué: {e}")
        
        return stories
    
    async def download_story(self, session: aiohttp.ClientSession, story: StoryItem, 
                           progress_callback=None) -> bool:
        """Télécharge une story individuelle"""
        try:
            filename = self.output_dir / story.get_filename()
            
            if filename.exists():
                print(f"⏭️ {filename.name} existe déjà, ignoré")
                return True
            
            # Headers spécifiques pour le téléchargement
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Encoding': 'identity;q=1, *;q=0',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Referer': 'https://story.snapchat.com/',
                'Origin': 'https://story.snapchat.com',
            }
            
            async with session.get(
                story.url, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    async with aiofiles.open(filename, 'wb') as f:
                        downloaded = 0
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                    if progress_callback:
                        progress_callback(story.index, True)
                    print(f"✅ Téléchargé: {filename.name}")
                    return True
                else:
                    print(f"❌ Erreur HTTP {response.status} pour {story.url}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erreur téléchargement: {str(e)[:100]}")
            if progress_callback:
                progress_callback(story.index, False)
            return False
    
    async def download_all_stories(self, stories: List[StoryItem], 
                                   max_concurrent: int = 3,
                                   progress_callback=None) -> Tuple[int, int]:
        """Télécharge toutes les stories en parallèle avec limite de concurrence"""
        if not stories:
            print("❌ Aucune story à télécharger")
            return 0, 0
        
        print(f"\n📥 Téléchargement de {len(stories)} stories...")
        print(f"📁 Dossier de sortie: {self.output_dir.absolute()}\n")
        
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        timeout = aiohttp.ClientTimeout(total=300)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for story in stories:
                task = self.download_story(session, story, progress_callback)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success = sum(1 for r in results if r is True)
        failed = len(results) - success
        
        return success, failed
    
    def download_sync(self, url: str, max_concurrent: int = 3) -> bool:
        """Méthode synchrone pour télécharger les stories"""
        print(f"\n🔍 Recherche des stories pour: {url}\n")
        
        # Obtenir les URLs des stories
        stories = self.get_story_urls_from_api(url)
        
        if not stories:
            print("❌ Aucune story trouvée. Vérifiez que:")
            print("   - Le profil est public")
            print("   - Les stories ne sont pas expirées (24h max)")
            print("   - Le lien est correct")
            return False
        
        # Trier par index pour conserver l'ordre
        stories.sort(key=lambda x: x.index)
        
        print(f"\n📊 Résumé:")
        print(f"   - Stories trouvées: {len(stories)}")
        print(f"   - Vidéos: {sum(1 for s in stories if s.type == 'video')}")
        print(f"   - Images: {sum(1 for s in stories if s.type == 'image')}")
        
        # Créer un sous-dossier avec le nom d'utilisateur
        username = stories[0].username or "unknown"
        user_dir = self.output_dir / username
        user_dir.mkdir(exist_ok=True)
        self.output_dir = user_dir
        
        # Télécharger
        success, failed = asyncio.run(
            self.download_all_stories(stories, max_concurrent)
        )
        
        print(f"\n✨ Terminé!")
        print(f"   - Téléchargés avec succès: {success}")
        print(f"   - Échoués: {failed}")
        print(f"   - Emplacement: {self.output_dir.absolute()}")
        
        return success > 0


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🚀 Snapchat Stories Downloader v1.0")
    print("=" * 60)
    
    # Lire l'URL
    url = input("\n🔗 Entrez l'URL du profil ou de la story Snapchat:\n> ").strip()
    
    if not url:
        print("❌ URL vide!")
        return
    
    if 'snapchat.com' not in url:
        print("❌ URL invalide! Doit contenir 'snapchat.com'")
        return
    
    # Dossier de sortie
    output = input("\n📁 Dossier de sortie (laissez vide pour 'downloads'):\n> ").strip()
    output_dir = output if output else "downloads"
    
    # Concurrence
    concurrent = input("\n⚡ Nombre de téléchargements simultanés (1-5, défaut: 3):\n> ").strip()
    max_concurrent = int(concurrent) if concurrent.isdigit() and 1 <= int(concurrent) <= 5 else 3
    
    # Télécharger
    downloader = SnapchatDownloader(output_dir)
    success = downloader.download_sync(url, max_concurrent)
    
    if success:
        print("\n🎉 Tous les téléchargements sont terminés!")
    else:
        print("\n😕 Certains téléchargements ont échoué.")
    
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()