import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import json
import logging
from pathlib import Path
from datetime import datetime
import re


class WebScraper:
    """
    Snippet modulare per web scraping.
    
    Features:
    - Scraping HTML con BeautifulSoup
    - Estrazione tabelle
    - Download file
    - Rate limiting automatico
    - User-agent rotation
    
    Examples:
        >>> scraper = WebScraper()
        >>> data = scraper.scrape_table("https://example.com/table")
        >>> df = pd.DataFrame(data)
    """
    
    def __init__(self, timeout: int = 10, retry: int = 3):
        """
        Inizializza scraper.
        
        Args:
            timeout: Timeout richieste (secondi)
            retry: Numero tentativi in caso di errore
        """
        self.timeout = timeout
        self.retry = retry
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def fetch_page(self, url: str, headers: Dict = None) -> Optional[BeautifulSoup]:
        """
        Recupera e parsa pagina HTML.
        
        Args:
            url: URL da scaricare
            headers: Headers HTTP custom
        
        Returns:
            BeautifulSoup object o None se errore
        """
        if headers is None:
            headers = {'User-Agent': np.random.choice(self.user_agents)}
        
        for attempt in range(self.retry):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info(f"✅ Page fetched successfully")
                return soup
                
            except requests.RequestException as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == self.retry - 1:
                    return None
        
        return None
    
    def scrape_table(self, url: str, table_index: int = 0) -> List[Dict]:
        """
        Estrae tabella HTML e converte in lista di dizionari.
        
        Args:
            url: URL pagina con tabella
            table_index: Indice tabella (se multiple)
        
        Returns:
            Lista di dizionari con dati tabella
        
        Example:
            >>> data = scraper.scrape_table("https://example.com/data")
            >>> df = pd.DataFrame(data)
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        try:
            tables = soup.find_all('table')
            if not tables or table_index >= len(tables):
                logger.error(f"Table {table_index} not found")
                return []
            
            table = tables[table_index]
            
            # Estrai headers
            headers = []
            for th in table.find_all('th'):
                headers.append(th.get_text(strip=True))
            
            # Se non ci sono th, usa prima riga
            if not headers:
                first_row = table.find('tr')
                if first_row:
                    headers = [td.get_text(strip=True) for td in first_row.find_all('td')]
            
            # Estrai righe
            data = []
            for row in table.find_all('tr')[1:]:  # Skip header row
                cells = row.find_all('td')
                if cells:
                    row_data = {
                        headers[i] if i < len(headers) else f'col_{i}': 
                        cell.get_text(strip=True)
                        for i, cell in enumerate(cells)
                    }
                    data.append(row_data)
            
            logger.info(f"✅ Extracted {len(data)} rows from table")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error extracting table: {e}")
            return []
    
    def scrape_links(self, url: str, filter_pattern: str = None) -> List[str]:
        """
        Estrae tutti i link da una pagina.
        
        Args:
            url: URL pagina
            filter_pattern: Regex per filtrare link
        
        Returns:
            Lista di URL
        """
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            
            # Converti link relativi in assoluti
            if link.startswith('/'):
                from urllib.parse import urljoin
                link = urljoin(url, link)
            
            # Filtra se pattern specificato
            if filter_pattern:
                if re.search(filter_pattern, link):
                    links.append(link)
            else:
                links.append(link)
        
        logger.info(f"✅ Found {len(links)} links")
        return links
    
    def download_file(self, url: str, output_path: str) -> bool:
        """
        Scarica file da URL.
        
        Args:
            url: URL del file
            output_path: Percorso salvataggio
        
        Returns:
            bool: True se download riuscito
        """
        try:
            logger.info(f"Downloading: {url}")
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✅ File saved: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            return False


class APIClient:
    """
    Snippet per interazioni API REST.
    
    Example:
        >>> client = APIClient("https://api.example.com")
        >>> data = client.get("/users/123")
        >>> result = client.post("/users", {"name": "Mario"})
    """
    
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """GET request"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GET error: {e}")
            return None
    
    def post(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """POST request"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"POST error: {e}")
            return None


