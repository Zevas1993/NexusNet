import requests
from bs4 import BeautifulSoup
def fetch_url(url:str):
    r=requests.get(url, timeout=10); r.raise_for_status()
    soup=BeautifulSoup(r.text, 'html.parser')
    for s in soup(['script','style']): s.decompose()
    text='\n'.join(t.strip() for t in soup.get_text().splitlines() if t.strip())
    title=soup.title.string if soup.title else url
    return {'id':url,'text':text[:4000],'title':title}