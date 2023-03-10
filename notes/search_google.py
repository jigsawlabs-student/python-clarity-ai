import requests
from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urlparse
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

class Source(BaseModel):
    url: str
    text: str

def search(query: str):
    try:
        source_count = 4

        # GET LINKS
        response = requests.get(f"https://www.google.com/search?q={query}")
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('/url?q='):
                cleaned_href = href.replace('/url?q=', '').split('&')[0]
                if cleaned_href not in links:
                    links.append(cleaned_href)

        exclude_list = ["google", "facebook", "twitter", "instagram", "youtube", "tiktok"]
        filtered_links = [link for idx, link in enumerate(links) if urlparse(link).hostname and
                          not any(site in urlparse(link).hostname for site in exclude_list) and
                          links.index(link) == idx][:source_count]

        # SCRAPE TEXT FROM LINKS
        sources = []

        for link in filtered_links:
            response = requests.get(link)
            # here the sources and summary looks different 
            # 1. Is it different from what 
            doc = Document(response.content)
            parsed = doc.summary()
            
            soup = BeautifulSoup(parsed, 'html.parser')
            source_text = ''.join([str(s) for s in soup.find_all(text=True) if s.parent.name not in ['style', 'script']])
            source_text = source_text.strip().replace('\n', ' ').replace('\r', '')
            source_text = source_text[:1500]
            source = Source(url=link, text=source_text)
            sources.append(source)

        return {"sources": sources}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")



