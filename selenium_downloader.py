#!/usr/bin/env python3
"""
Snapchat Downloader avec Selenium (Headless)
Pour serveur AWS/Ubuntu sans interface graphique
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
from urllib.parse import urljoin

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium non installé. Installez avec: pip install selenium webdriver-manager")

from snapchat_downloader import StoryItem


class SeleniumSnapchatDownloader:
    """
    Downloader Snapchat utilisant Selenium headless
    Fonctionne sur serveur AWS/Ubuntu sans interface graphique
    """
    
    def __init__(self, output_dir: str = "downloads", headless: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.driver = None
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium requis. Installez: pip install selenium webdriver-manager")
    
    def _create_driver(self):
        """Crée le driver Chrome en mode headless"""
        try:
            logger.info("Création du driver Chrome headless...")
            
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Options essentielles pour le mode headless/serveur
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--disable-setuid-sandbox')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Preferences pour le téléchargement automatique
            prefs = {
                'download.default_directory': str(self.output_dir.absolute()),
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            # Essayer de trouver Chrome
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/usr/local/bin/google-chrome',
                '/snap/bin/chromium',
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if Path(path).exists():
                    chrome_binary = path
                    break
            
            if chrome_binary:
                chrome_options.binary_location = chrome_binary
                logger.info(f"Chrome trouvé: {chrome_binary}")
            else:
                logger.warning("Chrome non trouvé dans les chemins standards")
            
            # Créer le driver
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"webdriver_manager a échoué: {e}")
                logger.info("Tentative avec chromedriver système...")
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.set_page_load_timeout(30)
            logger.info("✅ Driver Chrome créé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur création driver: {e}")
            raise
    
    def _close_driver(self):
        """Ferme le driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver fermé")
            except:
                pass
            finally:
                self.driver = None
    
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
    
    def download_from_website(self, url: str, username: str) -> List[StoryItem]:
        """
        Utilise un site de téléchargement pour obtenir les stories
        """
        stories = []
        
        try:
            self._create_driver()
            
            # Essayer différents sites de téléchargement
            websites = [
                {
                    'name': 'sssinstagram',
                    'url': 'https://sssinstagram.com/snapchat-video-downloader',
                    'input_selector': 'input[name="url"]',
                    'button_selector': 'button[type="submit"]',
                    'result_selector': '.download-item, .media-item, video, img',
                    'wait_time': 10
                },
                {
                    'name': 'savefrom',
                    'url': 'https://savefrom.net/snapchat-video-downloader',
                    'input_selector': '#sf_url',
                    'button_selector': '#sf_submit',
                    'result_selector': '.link-download, video, .download-link',
                    'wait_time': 15
                },
                {
                    'name': 'snapinsta',
                    'url': 'https://snapinsta.app',
                    'input_selector': 'input[name="url"]',
                    'button_selector': 'button[type="submit"]',
                    'result_selector': '.download-item, video, img',
                    'wait_time': 10
                }
            ]
            
            for site in websites:
                try:
                    logger.info(f"🌐 Tentative avec {site['name']}...")
                    
                    # Ouvrir le site
                    self.driver.get(site['url'])
                    logger.info(f"   Page chargée: {site['name']}")
                    
                    # Attendre que la page charge
                    time.sleep(3)
                    
                    # Trouver et remplir l'input
                    try:
                        input_field = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, site['input_selector']))
                        )
                        input_field.clear()
                        input_field.send_keys(url)
                        logger.info(f"   URL entrée")
                    except TimeoutException:
                        logger.warning(f"   Input non trouvé, essai du sélecteur alternatif")
                        # Essayer de trouver n'importe quel input
                        inputs = self.driver.find_elements(By.TAG_NAME, 'input')
                        for inp in inputs:
                            if inp.is_displayed():
                                inp.send_keys(url)
                                logger.info(f"   URL entrée (sélecteur alternatif)")
                                break
                    
                    # Cliquer sur le bouton
                    try:
                        button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, site['button_selector']))
                            
                        )
                        button.click()
                        logger.info(f"   Bouton cliqué")
                    except:
                        # Essayer de trouver n'importe quel bouton
                        buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                        for btn in buttons:
                            if btn.is_displayed():
                                try:
                                    btn.click()
                                    logger.info(f"   Bouton cliqué (sélecteur alternatif)")
                                    break
                                except:
                                    pass
                    
                    # Attendre les résultats
                    logger.info(f"   Attente des résultats ({site['wait_time']}s)...")
                    time.sleep(site['wait_time'])
                    
                    # Chercher les URLs de médias
                    # 1. Chercher les balises video
                    videos = self.driver.find_elements(By.TAG_NAME, 'video')
                    for i, video in enumerate(videos):
                        src = video.get_attribute('src')
                        if src and 'http' in src:
                            stories.append(StoryItem(
                                url=src,
                                type='video',
                                index=len(stories),
                                username=username
                            ))
                            logger.info(f"   ✅ Vidéo trouvée: {src[:60]}...")
                    
                    # 2. Chercher les balises img
                    images = self.driver.find_elements(By.TAG_NAME, 'img')
                    for i, img in enumerate(images):
                        src = img.get_attribute('src')
                        if src and 'http' in src and not 'logo' in src.lower():
                            stories.append(StoryItem(
                                url=src,
                                type='image',
                                index=len(stories),
                                username=username
                            ))
                    
                    # 3. Chercher les liens de téléchargement
                    links = self.driver.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        if href and any(ext in href.lower() for ext in ['.mp4', '.jpg', '.jpeg', '.png']):
                            if href not in [s.url for s in stories]:
                                stories.append(StoryItem(
                                    url=href,
                                    type='video' if '.mp4' in href else 'image',
                                    index=len(stories),
                                    username=username
                                ))
                                logger.info(f"   ✅ Lien trouvé: {href[:60]}...")
                    
                    if stories:
                        logger.info(f"✅ {len(stories)} médias trouvés via {site['name']}")
                        return stories
                    else:
                        logger.warning(f"⚠️  Aucun média trouvé via {site['name']}")
                
                except Exception as e:
                    logger.warning(f"⚠️  {site['name']} a échoué: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ Erreur Selenium: {e}")
        
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
        
        # Méthode 1: Utiliser Selenium avec sites de téléchargement
        stories = self.download_from_website(url, username)
        
        if stories:
            logger.info(f"✅ {len(stories)} stories trouvées via Selenium")
            return stories
        
        logger.warning("⚠️  Aucune story trouvée via Selenium")
        return stories
    
    async def download_story(self, session: aiohttp.ClientSession, story: StoryItem) -> bool:
        """Télécharge une story individuelle"""
        try:
            filename = self.output_dir / story.username / story.get_filename()
            filename.parent.mkdir(parents=True, exist_ok=True)
            
            if filename.exists():
                logger.info(f"⏭️  {filename.name} existe déjà")
                return True
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://story.snapchat.com/',
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
            logger.error(f"❌ Erreur téléchargement: {e}")
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
        """Méthode synchrone pour télécharger"""
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
        logger.info(f"   - Vidéos: {sum(1 for s in stories if s.type == 'video')}")
        logger.info(f"   - Images: {sum(1 for s in stories if s.type == 'image')}")
        
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


if __name__ == '__main__':
    # Test
    print("=" * 60)
    print("Test du downloader Selenium")
    print("=" * 60)
    
    try:
        downloader = SeleniumSnapchatDownloader(headless=True)
        url = input("\nURL Snapchat: ").strip()
        if url:
            success = downloader.download_sync(url)
            if success:
                print("\n✅ Téléchargement réussi!")
            else:
                print("\n❌ Échec du téléchargement")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nAppuyez sur Entrée pour quitter...")