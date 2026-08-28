import feedparser
import json
import re
from datetime import datetime, timezone
from dateutil import parser as date_parser

SOURCES_FILE = "sources.json"
DATA_FILE = "news.json"
BULLETIN_FILE = "bulletin.json"

def categorize(title, summary, source_name):
    text = (title + " " + summary).lower()
    
    # REGION
    region = "Global"
    if any(w in text for w in ["usa", "us", "eua", "estados unidos", "biden", "washington", "trump", "kamala", "harris"]):
        region = "América do Norte"
    elif any(w in text for w in ["brasil", "brazil", "argentina", "venezuela", "chile", "colômbia", "colombia", "lula", "bolsonaro", "maduro"]):
        region = "América do Sul"
    elif any(w in text for w in ["europa", "europe", "russia", "rússia", "ukraine", "ucrânia", "putin", "macron", "reino unido", "uk", "london", "paris", "berlim", "alemanha"]):
        region = "Europa"
    elif any(w in text for w in ["china", "japan", "japão", "índia", "india", "asia", "ásia", "taiwan", "korea", "coreia", "beijing", "xi jinping"]):
        region = "Ásia"
    elif any(w in text for w in ["israel", "gaza", "palestine", "palestina", "iran", "irã", "oriente médio", "middle east", "síria", "syria", "hamas", "lebanon", "líbano"]):
        region = "Oriente Médio"
    elif any(w in text for w in ["áfrica", "africa", "sudão", "sudan", "nigeria", "egito", "egypt", "congo"]):
        region = "África"
    elif any(w in text for w in ["australia", "austrália", "nova zelândia", "new zealand", "oceania"]):
        region = "Oceania"

    # THEME (Improved logic to avoid Outros)
    theme = "Outros / Multitemático"
    
    if any(w in text for w in ["war", "guerra", "military", "militar", "nato", "otan", "missile", "míssil", "weapons", "armas", "defense", "defesa", "nuclear", "ataque", "attack", "troops", "tropas"]):
        theme = "Geopolítica e Segurança"
    elif any(w in text for w in ["election", "eleição", "eleições", "vote", "voto", "parliament", "parlamento", "congress", "congresso", "senado", "senate", "supreme court", "stf", "ministro", "governo", "presidente", "lawmaker", "campaign", "campanha"]):
        if region == "América do Sul" and ("brasil" in text or "brazil" in text or "g1" in source_name.lower() or "poder360" in source_name.lower()):
            theme = "Política Brasileira"
        else:
            theme = "Política Internacional"
    elif any(w in text for w in ["economy", "economia", "inflation", "inflação", "market", "mercado", "stocks", "ações", "bank", "banco", "tax", "imposto", "juros", "interest rates", "trade", "comércio", "tarifas", "tariffs", "pib", "gdp"]):
        if region == "América do Sul" and ("brasil" in text or "brazil" in text or "g1" in source_name.lower() or "poder360" in source_name.lower()):
            theme = "Economia e Política Brasileira"
        else:
            theme = "Economia Internacional"
    elif any(w in text for w in ["climate", "clima", "environment", "meio ambiente", "emission", "emissão", "warming", "aquecimento", "amazônia", "amazon", "floresta", "chuvas", "enchentes", "floods", "wildfire", "fogo", "queimadas"]):
        theme = "Meio Ambiente e Clima"
    elif any(w in text for w in ["technology", "tecnologia", "tech", "ai", "artificial intelligence", "inteligência artificial", "space", "espaço", "nasa", "science", "ciência", "apple", "google", "meta", "musk", "spacex", "software"]):
        theme = "Ciência, Tecnologia e Inovação"
    elif any(w in text for w in ["rights", "direitos", "migrant", "migrante", "refugee", "refugiado", "asylum", "asilo", "protest", "protesto", "strike", "greve", "lgbt", "women", "mulheres", "racism", "racismo"]):
        theme = "Direitos Humanos, Sociedade e Migrações"
    elif any(w in text for w in ["health", "saúde", "disease", "doença", "virus", "vírus", "pandemic", "pandemia", "vaccine", "vacina", "who", "oms", "hospital", "cancer", "câncer"]):
        theme = "Saúde Global"
    elif any(w in text for w in ["court", "tribunal", "law", "lei", "justice", "justiça", "un", "onu", "icc", "tpi", "icj", "cij", "treaty", "tratado"]):
        theme = "Direito Internacional e Instituições"
    elif any(w in text for w in ["culture", "cultura", "movie", "filme", "music", "música", "art", "arte", "olympics", "olimpíadas", "sports", "esportes", "futebol", "soccer", "entertainment", "entretenimento", "celebrity", "famosos"]):
        theme = "Cultura, Mídia e Sociedade"
    
    # Se sobrou, avaliamos um pouco mais amplo para evitar multitemático se tiver palavra de finança global
    if theme == "Outros / Multitemático":
        if any(w in text for w in ["dólar", "dollar", "euro", "moeda", "currency", "fmi", "imf", "world bank", "banco mundial"]):
            theme = "Comércio e Finanças Globais"

    return region, theme

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext[:200] + "..." if len(cleantext) > 200 else cleantext

def extract_image(entry, summary_html):
    # Try media_content
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url')
    # Try media_thumbnail
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    # Try enclosures
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image'):
                return enc.get('href')
    # Regex from summary
    img_match = re.search(r'<img[^>]+src="([^">]+)"', summary_html)
    if img_match:
        return img_match.group(1)
    
    return None

def scrape():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        sources = json.load(f)

    all_news = []
    seen_urls = set()

    for src in sources:
        limit = 15 if src['origin'] == 'brasil' else 8
        try:
            feed = feedparser.parse(src['url'])
            for entry in feed.entries[:limit]: 
                url = entry.link
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                title = entry.title
                summary_html = entry.get('summary', entry.get('description', ''))
                summary = clean_html(summary_html)
                image_url = extract_image(entry, summary_html)
                
                try:
                    if 'published' in entry:
                        dt = date_parser.parse(entry.published)
                    elif 'updated' in entry:
                        dt = date_parser.parse(entry.updated)
                    else:
                        dt = datetime.now(timezone.utc)
                except Exception:
                    dt = datetime.now(timezone.utc)
                    
                dt = dt.astimezone(timezone.utc)
                
                region, theme = categorize(title, summary, src['name'])
                
                all_news.append({
                    "title": title,
                    "url": url,
                    "summary": summary,
                    "source": src['name'],
                    "origin": src['origin'],
                    "image": image_url,
                    "published_at": dt.isoformat(),
                    "region": region,
                    "theme": theme
                })
        except Exception as e:
            pass

    all_news.sort(key=lambda x: x['published_at'], reverse=True)
    
    # We want at least 50 if possible, let's just keep up to 150
    all_news = all_news[:150]
    
    output_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "articles": all_news
    }
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    # Carousel top 5-8 highlights (e.g., 6 most recent with images)
    highlights = [n for n in all_news if n['image']][:6]
    # Fallback if not enough images
    if len(highlights) < 6:
        for n in all_news:
            if n not in highlights:
                highlights.append(n)
            if len(highlights) == 6:
                break

    bulletin = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "highlights": highlights
    }
    with open(BULLETIN_FILE, "w", encoding="utf-8") as f:
        json.dump(bulletin, f, ensure_ascii=False, indent=2)

    # Print distribution
    dist = {}
    for n in all_news:
        dist[n['theme']] = dist.get(n['theme'], 0) + 1
    
    print("\n--- DISTRIBUIÇÃO DE TEMAS ---")
    for t, c in sorted(dist.items(), key=lambda x: x[1], reverse=True):
        print(f"{t}: {c}")
    print("-----------------------------\n")

if __name__ == "__main__":
    scrape()
