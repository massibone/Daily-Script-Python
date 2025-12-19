#!/usr/bin/env python3
"""
Social Media Profile Image Downloader
Scarica immagini da profili social (Instagram, Twitter, etc.)

Supporta:
- Instagram (tramite instaloader)
- Twitter/X (tramite tweepy)
- Download batch multipli profili
- Gestione rate limits e retry
- Metadata EXIF preservation

Usage:
    python download_images_profile.py @username --platform instagram
    python download_images_profile.py @username1 @username2 --platform twitter
    python download_images_profile.py --file usernames.txt --platform instagram

NOTA: Richiede autenticazione per alcune piattaforme.
Leggere README per configurazione credenziali.
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocialImageDownloader:
    """Classe base per download immagini social"""
    
    def __init__(self, output_dir='downloaded_images', max_posts=50):
        self.output_dir = Path(output_dir)
        self.max_posts = max_posts
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'downloaded': 0,
            'skipped': 0,
            'failed': 0
        }
    
    def sanitize_filename(self, filename):
        """Rimuove caratteri non validi dai nomi file"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def download_image(self, url, filepath, headers=None):
        """Scarica una singola immagine"""
        try:
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Salva file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.stats['downloaded'] += 1
            logger.info(f"✓ Scaricato: {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Errore download {url}: {e}")
            self.stats['failed'] += 1
            return False
    
    def print_stats(self):
        """Stampa statistiche download"""
        print(f"\n{'='*60}")
        print(f"📊 STATISTICHE DOWNLOAD")
        print(f"{'='*60}")
        print(f"✓ Scaricate:  {self.stats['downloaded']}")
        print(f"⊘ Saltate:    {self.stats['skipped']}")
        print(f"✗ Fallite:    {self.stats['failed']}")
        print(f"{'='*60}\n")


class InstagramDownloader(SocialImageDownloader):
    """Download immagini da Instagram usando instaloader"""
    
    def __init__(self, output_dir='downloaded_images', max_posts=50, 
                 username=None, password=None):
        super().__init__(output_dir, max_posts)
        self.username = username
        self.password = password
        self.loader = None
        
        try:
            import instaloader
            self.instaloader = instaloader
            self.loader = instaloader.Instaloader(
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=True,
                compress_json=False,
                max_connection_attempts=3
            )
            
            # Login se credenziali fornite
            if self.username and self.password:
                logger.info(f"🔐 Login come {self.username}...")
                self.loader.login(self.username, self.password)
                logger.info("✓ Login effettuato")
                
        except ImportError:
            raise ImportError(
                "instaloader non installato. Esegui: pip install instaloader"
            )
        except Exception as e:
            logger.error(f"Errore login Instagram: {e}")
    
    def download_profile(self, profile_name):
        """Scarica immagini da profilo Instagram"""
        logger.info(f"\n📸 Download profilo Instagram: @{profile_name}")
        
        # Rimuove @ se presente
        profile_name = profile_name.lstrip('@')
        
        try:
            profile = self.instaloader.Profile.from_username(
                self.loader.context, 
                profile_name
            )
            
            logger.info(f"👤 Profilo: {profile.full_name}")
            logger.info(f"📊 Post totali: {profile.mediacount}")
            logger.info(f"👥 Followers: {profile.followers}")
            
            # Crea cartella profilo
            profile_dir = self.output_dir / f"instagram_{profile_name}"
            profile_dir.mkdir(exist_ok=True)
            
            # Download posts
            downloaded = 0
            for post in profile.get_posts():
                if downloaded >= self.max_posts:
                    logger.info(f"⚠ Raggiunto limite {self.max_posts} post")
                    break
                
                try:
                    # Nome file
                    date_str = post.date.strftime("%Y%m%d_%H%M%S")
                    shortcode = post.shortcode
                    
                    # Download immagine principale
                    if post.typename == 'GraphImage':
                        filename = f"{date_str}_{shortcode}.jpg"
                        filepath = profile_dir / filename
                        
                        if filepath.exists():
                            logger.info(f"⊘ Già esistente: {filename}")
                            self.stats['skipped'] += 1
                            continue
                        
                        self.download_image(post.url, filepath)
                        
                        # Salva metadata
                        self._save_metadata(post, profile_dir / f"{date_str}_{shortcode}.json")
                        downloaded += 1
                    
                    # Post multipli (carousel)
                    elif post.typename == 'GraphSidecar':
                        for idx, node in enumerate(post.get_sidecar_nodes(), 1):
                            if node.is_video:
                                continue
                            
                            filename = f"{date_str}_{shortcode}_{idx}.jpg"
                            filepath = profile_dir / filename
                            
                            if not filepath.exists():
                                self.download_image(node.display_url, filepath)
                        
                        self._save_metadata(post, profile_dir / f"{date_str}_{shortcode}.json")
                        downloaded += 1
                    
                    # Attendi tra download (rate limiting)
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Errore post {post.shortcode}: {e}")
                    self.stats['failed'] += 1
                    continue
            
            logger.info(f"✓ Download completato: {downloaded} post")
            return profile_dir
            
        except Exception as e:
            logger.error(f"Errore download profilo {profile_name}: {e}")
            return None
    
    def _save_metadata(self, post, filepath):
        """Salva metadata post in JSON"""
        try:
            metadata = {
                'shortcode': post.shortcode,
                'date': post.date.isoformat(),
                'caption': post.caption if post.caption else '',
                'likes': post.likes,
                'comments': post.comments,
                'location': post.location.name if post.location else None,
                'is_video': post.is_video,
                'url': f"https://www.instagram.com/p/{post.shortcode}/"
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Impossibile salvare metadata: {e}")


class TwitterDownloader(SocialImageDownloader):
    """Download immagini da Twitter/X usando tweepy"""
    
    def __init__(self, output_dir='downloaded_images', max_posts=50,
                 bearer_token=None, api_key=None, api_secret=None,
                 access_token=None, access_secret=None):
        super().__init__(output_dir, max_posts)
        
        try:
            import tweepy
            
            if bearer_token:
                # Twitter API v2 (consigliato)
                self.client = tweepy.Client(bearer_token=bearer_token)
            elif all([api_key, api_secret, access_token, access_secret]):
                # Twitter API v1.1
                auth = tweepy.OAuth1UserHandler(
                    api_key, api_secret,
                    access_token, access_secret
                )
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
            else:
                raise ValueError(
                    "Fornire bearer_token (API v2) o credenziali complete (API v1.1)"
                )
            
            logger.info("✓ Autenticazione Twitter completata")
            
        except ImportError:
            raise ImportError(
                "tweepy non installato. Esegui: pip install tweepy"
            )
    
    def download_profile(self, username):
        """Scarica immagini da profilo Twitter"""
        logger.info(f"\n🐦 Download profilo Twitter: @{username}")
        
        username = username.lstrip('@')
        
        try:
            # Crea cartella profilo
            profile_dir = self.output_dir / f"twitter_{username}"
            profile_dir.mkdir(exist_ok=True)
            
            # Ottieni tweet con media
            tweets = self.api.user_timeline(
                screen_name=username,
                count=self.max_posts,
                include_rts=False,
                exclude_replies=True,
                tweet_mode='extended'
            )
            
            logger.info(f"📊 Trovati {len(tweets)} tweet")
            
            downloaded = 0
            for tweet in tweets:
                # Verifica presenza media
                if 'media' not in tweet.entities:
                    continue
                
                for idx, media in enumerate(tweet.entities['media'], 1):
                    if media['type'] == 'photo':
                        # URL immagine alta qualità
                        img_url = media['media_url_https'] + ':large'
                        
                        # Nome file
                        date_str = tweet.created_at.strftime("%Y%m%d_%H%M%S")
                        filename = f"{date_str}_{tweet.id}_{idx}.jpg"
                        filepath = profile_dir / filename
                        
                        if filepath.exists():
                            self.stats['skipped'] += 1
                            continue
                        
                        if self.download_image(img_url, filepath):
                            downloaded += 1
                        
                        # Salva metadata
                        metadata = {
                            'tweet_id': str(tweet.id),
                            'date': tweet.created_at.isoformat(),
                            'text': tweet.full_text,
                            'likes': tweet.favorite_count,
                            'retweets': tweet.retweet_count,
                            'url': f"https://twitter.com/{username}/status/{tweet.id}"
                        }
                        
                        json_file = profile_dir / f"{date_str}_{tweet.id}.json"
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                time.sleep(1)  # Rate limiting
            
            logger.info(f"✓ Download completato: {downloaded} immagini")
            return profile_dir
            
        except Exception as e:
            logger.error(f"Errore download profilo {username}: {e}")
            return None


class GenericDownloader(SocialImageDownloader):
    """Download generico da URL pubblici"""
    
    def download_from_url_list(self, urls: List[str], prefix='image'):
        """Scarica lista di URL"""
        logger.info(f"\n🔗 Download da {len(urls)} URL")
        
        for idx, url in enumerate(urls, 1):
            ext = Path(url).suffix or '.jpg'
            filename = f"{prefix}_{idx:03d}{ext}"
            filepath = self.output_dir / filename
            
            if filepath.exists():
                logger.info(f"⊘ Già esistente: {filename}")
                self.stats['skipped'] += 1
                continue
            
            self.download_image(url, filepath)
            time.sleep(1)
        
        return self.output_dir


def load_credentials(config_file='social_config.json'):
    """Carica credenziali da file JSON"""
    if not Path(config_file).exists():
        logger.warning(f"File config non trovato: {config_file}")
        return {}
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Errore lettura config: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(
        description='Download immagini da profili social',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  # Instagram (richiede login)
  python download_images_profile.py @natgeo --platform instagram --max 30
  
  # Twitter
  python download_images_profile.py @NASA --platform twitter --max 50
  
  # Multipli profili
  python download_images_profile.py @user1 @user2 @user3 --platform instagram
  
  # Da file
  python download_images_profile.py --file usernames.txt --platform instagram

Configurazione:
  Crea file 'social_config.json' con credenziali:
  {
    "instagram": {
      "username": "tuo_username",
      "password": "tua_password"
    },
    "twitter": {
      "bearer_token": "tuo_token"
    }
  }
        """
    )
    
    parser.add_argument(
        'usernames',
        nargs='*',
        help='Username profili da scaricare (es: @username)'
    )
    parser.add_argument(
        '--platform', '-p',
        choices=['instagram', 'twitter', 'generic'],
        required=True,
        help='Piattaforma social'
    )
    parser.add_argument(
        '--file', '-f',
        help='File con lista usernames (uno per riga)'
    )
    parser.add_argument(
        '--output', '-o',
        default='downloaded_images',
        help='Cartella output (default: downloaded_images)'
    )
    parser.add_argument(
        '--max', '-m',
        type=int,
        default=50,
        help='Numero massimo post da scaricare (default: 50)'
    )
    parser.add_argument(
        '--config', '-c',
        default='social_config.json',
        help='File configurazione credenziali (default: social_config.json)'
    )
    
    args = parser.parse_args()
    
    # Carica usernames da file se specificato
    usernames = args.usernames or []
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_users = [line.strip() for line in f if line.strip()]
                usernames.extend(file_users)
        except Exception as e:
            logger.error(f"Errore lettura file: {e}")
            return
    
    if not usernames:
        logger.error("Specificare almeno un username o --file")
        parser.print_help()
        return
    
    # Carica credenziali
    credentials = load_credentials(args.config)
    
    try:
        # Inizializza downloader
        if args.platform == 'instagram':
            ig_creds = credentials.get('instagram', {})
            downloader = InstagramDownloader(
                output_dir=args.output,
                max_posts=args.max,
                username=ig_creds.get('username'),
                password=ig_creds.get('password')
            )
        
        elif args.platform == 'twitter':
            tw_creds = credentials.get('twitter', {})
            downloader = TwitterDownloader(
                output_dir=args.output,
                max_posts=args.max,
                bearer_token=tw_creds.get('bearer_token'),
                api_key=tw_creds.get('api_key'),
                api_secret=tw_creds.get('api_secret'),
                access_token=tw_creds.get('access_token'),
                access_secret=tw_creds.get('access_secret')
            )
        
        else:
            downloader = GenericDownloader(
                output_dir=args.output,
                max_posts=args.max
            )
        
        # Download per ogni username
        print(f"\n{'='*60}")
        print(f"🚀 Avvio download da {args.platform.upper()}")
        print(f"{'='*60}")
        print(f"Profili: {len(usernames)}")
        print(f"Max post per profilo: {args.max}")
        print(f"Output: {args.output}/")
        print(f"{'='*60}\n")
        
        for username in usernames:
            try:
                downloader.download_profile(username)
            except Exception as e:
                logger.error(f"Errore profilo {username}: {e}")
                continue
        
        # Stampa statistiche finali
        downloader.print_stats()
        print(f"✅ Download completato! File salvati in: {args.output}/\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Download interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Errore fatale: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
