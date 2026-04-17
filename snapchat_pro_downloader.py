#!/usr/bin/env python3
"""
Snapchat PRO Downloader - Version avec scraping direct
Utilise Selenium pour se connecter à Snapchat Web et scraper les stories
"""

import os
import re
import json
import time
import logging
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from datetime import datetime

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class StoryItem:
    """Représente un item de story"""
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


class SnapchatProDownloader:
    """
    Downloader PRO pour Snapchat
    Scraping direct depuis Snapchat Web avec Selenium
    """
    
    def __init__(self, output_dir: str = "downloads", headless: bool = True, cookies_file: Optional[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.cookies_file = cookies_file
        self.driver = None
        self.session_cookies = None
        
        if cookies_file and Path(cookies_file).exists():
            self._load_cookies()
    
    def _load_cookies(self):
        """Charge les cookies depuis un fichier JSON"""
        try:
            with open(self.cookies_file, 'r') as f:
                self.session_cookies = json.load(f)
            logger.info(f"✅ Cookies chargés depuis {self.cookies_file}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger les cookies: {e}")
    
    def _save_cookies(self):
        """Sauvegarde les cookies dans un fichier"""
        if self.driver:
            try:
                cookies = self.driver.get_cookies()
                with open('snapchat_cookies.json', 'w') as f:
                    json.dump(cookies, f, indent=2)
                logger.info("✅ Cookies sauvegardés")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de sauvegarder les cookies: {e}")
    
    def _create_driver(self):
        """Crée le driver Chrome"""
        try:
            logger.info("Création du driver Chrome...")
            
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Options essentielles
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Désactiver les images pour accélérer le chargement (optionnel)
            # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            
            # Préférences
            prefs = {
                'profile.default_content_setting_values.notifications': 2,  # Bloquer notifications
                'profile.managed_default_content_settings.images': 1,  # 1 = enable, 2 = disable
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            # Créer le driver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"webdriver_manager a échoué: {e}")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.set_page_load_timeout(60)
            
            # Injecter les cookies si disponibles
            if self.session_cookies:
                self.driver.get("https://web.snapchat.com")
                time.sleep(2)
                for cookie in self.session_cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                logger.info("✅ Cookies injectés")
            
            logger.info("✅ Driver Chrome créé")
            
        except Exception as e:
            logger.error(f"❌ Erreur création driver: {e}")
            raise
    
    def _close_driver(self):
        """Ferme le driver"""
        if self.driver:
            try:
                self._save_cookies()
                self.driver.quit()
                logger.info("Driver fermé")
            except:
                pass
            finally:
                self.driver = None
    
    def extract_username_from_url(self, url: str) -> Optional[str]:
        """Extrait le nom d'utilisateur"""
        patterns = [
            r'snapchat\.com/add/([^/?\s]+)',
            r'snapchat\.com/t/([^/?\s]+)',
            r'story\.snapchat\.com/s/([^/?\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_stories_from_snapchat_web(self, username: str) -> List[StoryItem]:
        """
        Scraping direct depuis Snapchat Web
        """
        stories = []
        
        try:
            self._create_driver()
            
            # URL de la story publique
            story_url = f"https://story.snapchat.com/s/{username}"
            logger.info(f"🌐 Accès à {story_url}")
            
            self.driver.get(story_url)
            logger.info("⏳ Attente du chargement...")
            time.sleep(5)
            
            # Vérifier si la page demande un login
            try:
                # Chercher des éléments qui indiquent un login nécessaire
                login_indicators = [
                    "//div[contains(text(), 'Log in')]",
                    "//button[contains(text(), 'Log in')]",
                    "//input[@type='password']",
                    "//a[contains(@href, 'login')]"
                ]
                
                login_found = False
                for indicator in login_indicators:
                    try:
                        if self.driver.find_element(By.XPATH, indicator):
                            login_found = True
                            break
                    except:
                        pass
                
                if login_found:
                    logger.warning("⚠️ Page de login détectée - Cookies nécessaires")
                    logger.info("💡 Créez un fichier snapchat_cookies.json avec vos cookies")
                    return stories
                
            except Exception as e:
                logger.debug(f"Vérification login: {e}")
            
            # Méthode 1: Chercher les balises video
            logger.info("🔍 Recherche des vidéos...")
            videos = self.driver.find_elements(By.TAG_NAME, 'video')
            for i, video in enumerate(videos):
                try:
                    src = video.get_attribute('src')
                    if src and ('cf.sc-cdn.net' in src or 'snapchat' in src):
                        stories.append(StoryItem(
                            url=src,
                            type='video',
                            index=len(stories),
                            username=username
                        ))
                        logger.info(f"✅ Vidéo trouvée: {src[:60]}...")
                except:
                    pass
            
            # Méthode 2: Chercher dans les sources (pour les players complexes)
            try:
                sources = self.driver.find_elements(By.TAG_NAME, 'source')
                for source in sources:
                    src = source.get_attribute('src')
                    if src and src not in [s.url for s in stories]:
                        stories.append(StoryItem(
                            url=src,
                            type='video',
                            index=len(stories),
                            username=username
                        ))
            except:
                pass
            
            # Méthode 3: Extraction depuis le JavaScript/Network
            logger.info("🔍 Extraction depuis les requêtes réseau...")
            
            # Récupérer les logs du browser (qui contiennent les requêtes réseau)
            try:
                logs = self.driver.get_log('performance')
                for log in logs:
                    message = json.loads(log['message'])
                    if 'Network.responseReceived' in message['message']['method']:
                        response = message['message']['params']['response']
                        url = response.get('url', '')
                        
                        # Filtrer les URLs de médias Snapchat
                        if any(domain in url for domain in ['cf.sc-cdn.net', 'snapcdn.net', 'sc-cdn.net']):
                            if '.mp4' in url and url not in [s.url for s in stories]:
                                stories.append(StoryItem(
                                    url=url,
                                    type='video',
                                    index=len(stories),
                                    username=username
                                ))
                                logger.info(f"✅ Vidéo réseau: {url[:60]}...")
            except Exception as e:
                logger.debug(f"Extraction réseau: {e}")
            
            # Méthode 4: Attendre et cliquer sur les stories pour les charger
            if not stories:
                logger.info("⏳ Tentative de chargement par interaction...")
                try:
                    # Chercher les éléments cliquables (stories)
                    story_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid], [role="button"]')
                    for elem in story_elements[:5]:  # Limiter à 5 pour éviter les boucles
                        try:
                            elem.click()
                            time.sleep(2)
                            
                            # Chercher les vidéos après le clic
                            videos = self.driver.find_elements(By.TAG_NAME, 'video')
                            for video in videos:
                                src = video.get_attribute('src')
                                if src and src not in [s.url for s in stories]:
                                    stories.append(StoryItem(
                                        url=src,
                                        type='video',
                                        index=len(stories),
                                        username=username
                                    ))
                        except:
                            pass
                except Exception as e:
                    logger.debug(f"Interaction: {e}")
            
            # Méthode 5: Parse le HTML brut
            if not stories:
                logger.info("🔍 Analyse du HTML...")
                html = self.driver.page_source
                
                # Chercher les URLs de médias dans le HTML
                patterns = [
                    r'https://[^"\'<>\s]+\.mp4[^"\'<>\s]*',
                    r'https://[^"\'<>\s]+cf\.sc-cdn\.net[^"\'<>\s]*',
                    r'https://[^"\'<>\s]+sc-cdn[^"\'<>\s]*\.(mp4|jpg)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html)
                    for url in matches:
                        full_url = url if url.startswith('http') else f"https://{url}"
                        if full_url not in [s.url for s in stories]:
                            stories.append(StoryItem(
                                url=full_url,
                                type='video' if '.mp4' in full_url else 'image',
                                index=len(stories),
                                username=username
                            ))
            
            if stories:
                logger.info(f"✅ {len(stories)} stories trouvées")
            else:
                logger.warning("⚠️ Aucune story trouvée")
                logger.info("💡 Essayez de:")
                logger.info("   1. Vérifier que le profil est public")
                logger.info("   2. Utiliser des cookies de session valides")
                logger.info("   3. Vérifier que les stories ne sont pas expirées")
        
        except Exception as e:
            logger.error(f"❌ Erreur scraping: {e}")
        
        finally:
            self._close_driver()
        
        return stories
    
    def get_story_urls_from_api(self, url: str) -> List[StoryItem]:
        """Obtient les URLs des stories"""
        stories = []
        username = self.extract_username_from_url(url)
        
        if not username:
            logger.error(f"Impossible d'extraire le username de: {url}")
            return stories
        
        logger.info(f"👤 Utilisateur détecté: {username}")
        
        # Scraping direct
        stories = self.get_stories_from_snapchat_web(username)
        
        return stories
    
    async def download_story(self, session: aiohttp.ClientSession, story: StoryItem) -> bool:
        """Télécharge une story"""
        try:
            filename = self.output_dir / story.username / story.get_filename()
            filename.parent.mkdir(parents=True, exist_ok=True)
            
            if filename.exists():
                logger.info(f"⏭️  {filename.name} existe déjà")
                return True
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://web.snapchat.com/',
            }
            
            async with session.get(story.url, headers=headers) as response:
                if response.status == 200:
                    async with aiofiles.open(filename, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    logger.info(f"✅ Téléchargé: {filename.name}")
                    return True
                else:
                    logger.warning(f"❌ Erreur HTTP {response.status}")
                    return False
        
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return False
    
    async def download_all_stories(self, stories: List[StoryItem], max_concurrent: int = 3):
        """Télécharge toutes les stories"""
        if not stories:
            return 0, 0
        
        logger.info(f"\n📥 Téléchargement de {len(stories)} stories...")
        
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.download_story(session, story) for story in stories]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success = sum(1 for r in results if r is True)
        failed = len(results) - success
        
        return success, failed
    
    def download_sync(self, url: str, max_concurrent: int = 3) -> bool:
        """Méthode synchrone"""
        logger.info(f"\n🔍 Recherche des stories pour: {url}\n")
        
        # Obtenir les URLs
        stories = self.get_story_urls_from_api(url)
        
        if not stories:
            logger.error("❌ Aucune story trouvée")
            return False
        
        # Trier
        stories.sort(key=lambda x: x.index)
        
        logger.info(f"\n📊 Résumé:")
        logger.info(f"   - Stories trouvées: {len(stories)}")
        
        # Créer le dossier utilisateur
        username = stories[0].username or "unknown"
        user_dir = self.output_dir / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Télécharger
        success, failed = asyncio.run(
            self.download_all_stories(stories, max_concurrent)
        )
        
        logger.info(f"\n✨ Terminé!")
        logger.info(f"   - Téléchargés: {success}")
        logger.info(f"   - Échoués: {failed}")
        logger.info(f"   - Emplacement: {user_dir.absolute()}")
        
        return success > 0


def create_cookies_template():
    """Crée un template de fichier cookies"""
    template = [
        {
            "name": "_scid",
            "value": "VOTRE_SCID_ICI",
            "domain": ".snapchat.com",
            "path": "/"
        },
        {
            "name": "_scs",
            "value": "VOTRE_SCS_ICI", 
            "domain": ".snapchat.com",
            "path": "/"
        },
        {
            "name": "sc-a-cookie",
            "value": "VOTRE_COOKIE_ICI",
            "domain": ".snapchat.com",
            "path": "/"
        }
    ]
    
    with open('snapchat_cookies_template.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("✅ Template de cookies créé: snapchat_cookies_template.json")
    print("💡 Remplacez les valeurs par vos cookies réels depuis le navigateur")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Snapchat PRO Downloader')
    parser.add_argument('url', help='URL Snapchat')
    parser.add_argument('--cookies', help='Fichier cookies JSON')
    parser.add_argument('--create-template', action='store_true', help='Créer un template de cookies')
    
    args = parser.parse_args()
    
    if args.create_template:
        create_cookies_template()
    elif args.url:
        try:
            downloader = SnapchatProDownloader(
                headless=True,
                cookies_file=args.cookies
            )
            success = downloader.download_sync(args.url)
            if success:
                print("\n✅ Téléchargement réussi!")
            else:
                print("\n❌ Échec du téléchargement")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
    
    input("\nAppuyez sur Entrée pour quitter...")