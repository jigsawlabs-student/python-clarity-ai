import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import List
from readability import Document
from fastapi import APIRouter, HTTPException

class Source:
    def __init__(self, url: str, text: str):
        self.url = url
        self.text = text

class SearchEngine:
    def __init__(self, source_count: int=10):
        self.source_count = source_count
        self.exclude_list = ["google", "facebook", "twitter", "instagram", "youtube", "tiktok"]
    
    def get_links(self, query: str) -> List[str]:
        response = requests.get(f"https://www.google.com/search?q={query}")
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('/url?q='):
                cleaned_href = href.replace('/url?q=', '').split('&')[0]
                if cleaned_href not in links:
                    links.append(cleaned_href)

        filtered_links = [link for idx, link in enumerate(links) if urlparse(link).hostname and
                          not any(site in urlparse(link).hostname for site in self.exclude_list) and
                          links.index(link) == idx][:self.source_count]
        return filtered_links
    
    def clean_text(self, parsed):
        soup = BeautifulSoup(parsed, 'html.parser')
        source_text = ''.join([str(s) for s in soup.find_all(text=True) if s.parent.name not in ['style', 'script']])
        source_text = source_text.strip().replace('\n', ' ').replace('\r', '')
        source_text = source_text[:1500]
        return source_text
    
    def scrape_sources(self, links: List[str]) -> List[Source]:
        sources = []
        for link in links:
            try:
                response = requests.get(link)
                doc = Document(response.content)
                parsed = doc.summary()
                
                source_text = self.clean_text(parsed)
                
                source = Source(url=link, text=source_text)
                sources.append(source)
            except Exception as e:
                print(e)
        return sources
    
    def search(self, query: str) -> dict:
        try:
            links = self.get_links(query)
            sources = self.scrape_sources(links)
            return sources
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Internal Server Error")

