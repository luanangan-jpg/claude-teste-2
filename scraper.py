import feedparser
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser as date_parser

SOURCES_FILE = "sources.json"
DATA_FILE = "news.json"
BULLETIN_FILE = "bulletin.json"

# Regras de inclusão e exclusão documentadas para classificação temática precisa
THEMES_RULES = {
    "Geopolítica e Segurança": {
        "include": ["guerra", "war ", "military", "militar", "nato", "otan", "míssil", "missile", "armas", "weapons", "defesa", "defense", "nuclear", "ataque", "attack", "tropas", "troops", "exército", "army", "conflito", "terroris", "refém", "paz", "peace", "fronteira", "border", "espionagem", "rebelde"],
        "exclude": ["guerra comercial"]
    },
    "Política Internacional": {
        "include": ["eleição", "election", "parlamento", "parliament", "congresso", "congress", "senado", "senate", "primeiro-ministro", "prime minister", "governo", "diplomacia", "embaixador", "onu ", "un ", "votação", "vote", "partido", "party", "candidato", "líder", "leader", "democracia", "ditadura", "ministro", "cúpula"],
        "exclude": ["brasil", "brazil", "lula", "bolsonaro", "stf", "tse", "planalto"]
    },
    "Política Brasileira": {
        "include": ["eleição", "eleições", "tse", "stf", "congresso", "senado", "câmara", "deputados", "lula", "bolsonaro", "governo federal", "planalto", "ministro", "prefeito", "vereador", "pablo marçal", "boulos", "nunes", "moraes", "pacheco", "lira", "partido"],
        "exclude": ["biden", "trump", "macron", "putin", "eleições americanas", "eua", "usa"]
    },
    "Economia Internacional": {
        "include": ["economia", "economy", "inflação", "inflation", "mercado", "market", "ações", "stocks", "banco central", "central bank", "juros", "interest rates", "fmi", "imf", "pib", "fed ", "federal reserve", "wall street", "empresas", "business", "desemprego", "petróleo", "oil"],
        "exclude": ["brasil", "brazil", "ibovespa", "copom", "selic", "haddad"]
    },
    "Economia Brasileira": {
        "include": ["economia", "inflação", "ibovespa", "copom", "selic", "dólar", "real", "fazenda", "haddad", "banco central", "campos neto", "pib", "imposto", "taxação", "tributária", "mercado financeiro", "desemprego"],
        "exclude": ["fed ", "federal reserve", "wall street"]
    },
    "Comércio e Finanças": {
        "include": ["comércio", "trade", "tarifas", "tariffs", "exportação", "importação", "wto", "omc", "cadeia de suprimentos", "supply chain", "investimento", "acordo comercial", "mercosul", "união europeia", "ações", "bolsa de valores", "criptomoeda", "bitcoin"],
        "exclude": []
    },
    "Meio Ambiente e Clima": {
        "include": ["clima", "climate", "meio ambiente", "environment", "emissão", "emission", "aquecimento", "warming", "amazônia", "amazon", "floresta", "chuvas", "enchentes", "floods", "queimadas", "wildfire", "seca", "drought", "carbon", "carbono", "temperatura", "fumaça", "poluição", "desastre"],
        "exclude": []
    },
    "Ciência, Tecnologia e Inovação": {
        "include": ["tecnologia", "tech ", "ai ", "artificial intelligence", "inteligência artificial", "espaço", "space", "nasa", "ciência", "science", "apple", "google", "meta", "musk", "spacex", "software", "cibersegurança", "cybersecurity", "internet", "redes sociais", "x ", "twitter", "telegram"],
        "exclude": ["alienígena"]
    },
    "Direitos Humanos, Sociedade e Migrações": {
        "include": ["direitos", "rights", "migrante", "migrant", "refugiado", "refugee", "asilo", "asylum", "protesto", "protest", "greve", "strike", "lgbt", "mulheres", "women", "racismo", "racism", "desigualdade", "inequality", "indígena", "violência", "crime", "polícia", "assassinato"],
        "exclude": []
    },
    "Saúde": {
        "include": ["saúde", "health", "doença", "disease", "vírus", "virus", "pandemia", "pandemic", "vacina", "vaccine", "oms", "who ", "hospital", "câncer", "cancer", "epidemia", "mpox", "covid", "médico", "pacientes", "sus "],
        "exclude": ["vírus de computador"]
    },
    "Direito Internacional e Instituições": {
        "include": ["tribunal internacional", "international court", "lei", "law", "justiça", "justice", "icc ", "tpi ", "icj", "cij", "tratado", "treaty", "cortes", "direitos humanos un", "prisão", "julgamento", "extradição"],
        "exclude": ["stf", "stj"]
    },
    "Cultura, Mídia e Sociedade": {
        "include": ["cultura", "culture", "filme", "movie", "música", "music", "arte", "art", "olimpíadas", "olympics", "esportes", "sports", "futebol", "soccer", "entretenimento", "entertainment", "famosos", "celebrity", "cinema", "oscar", "medalha", "paralimpíada"],
        "exclude": []
    }
}

# Tabela explícita fonte -> região
SOURCE_REGION_MAP = {
    "G1 - Mundo": "América do Sul",
    "Folha de S.Paulo - Mundo": "América do Sul",
    "Estadão - Internacional": "América do Sul",
    "Agência Brasil": "América do Sul",
    "Poder360": "América do Sul",
    "CNN Brasil": "América do Sul",
    "BBC News Brasil": "América do Sul",
    "UOL Notícias": "América do Sul"
}

def categorize(title, summary, source_name, origin):
    text = f"{title} {summary}".lower()
    
    # --- REGION ---
    # 1. Regra explícita da fonte
    if source_name in SOURCE_REGION_MAP:
        region = SOURCE_REGION_MAP[source_name]
    else:
        # 2. Análise de conteúdo se for agência internacional
        if any(w in text for w in ["usa", "us", "eua", "estados unidos", "biden", "washington", "trump", "kamala", "harris", "new york", "los angeles", "canadá", "canada", "méxico", "mexico"]):
            region = "América do Norte"
        elif any(w in text for w in ["brasil", "brazil", "argentina", "venezuela", "chile", "colômbia", "colombia", "lula", "bolsonaro", "maduro", "são paulo", "rio de janeiro", "buenos aires", "américa do sul", "américa latina"]):
            region = "América do Sul"
        elif any(w in text for w in ["europa", "europe", "russia", "rússia", "ukraine", "ucrânia", "putin", "macron", "reino unido", "uk", "london", "paris", "berlim", "alemanha", "frança", "espanha", "itália", "moscou", "kyiv", "kiev"]):
            region = "Europa"
        elif any(w in text for w in ["china", "japan", "japão", "índia", "india", "asia", "ásia", "taiwan", "korea", "coreia", "beijing", "xi jinping", "tóquio", "tokyo"]):
            region = "Ásia"
        elif any(w in text for w in ["israel", "gaza", "palestine", "palestina", "iran", "irã", "oriente médio", "middle east", "síria", "syria", "hamas", "lebanon", "líbano", "tel aviv", "jerusalém"]):
            region = "Oriente Médio"
        elif any(w in text for w in ["áfrica", "africa", "sudão", "sudan", "nigeria", "egito", "egypt", "congo", "pretória", "cairo"]):
            region = "África"
        elif any(w in text for w in ["australia", "austrália", "nova zelândia", "new zealand", "oceania", "sydney"]):
            region = "Oceania"
        else:
            region = "Global"

    # --- THEME ---
    best_theme = "Outros / Multitemático"
    max_score = 0
    
    for theme, rules in THEMES_RULES.items():
        score = 0
        if any(exc in text for exc in rules["exclude"]):
            continue
            
        for inc in rules["include"]:
            if inc in text:
                score += 2 if inc in title.lower() else 1
                
        # Handle overlaps
        if theme == "Economia Brasileira" and origin != "brasil" and "brasil" not in text:
            score = 0
        if theme == "Política Brasileira" and origin != "brasil" and "brasil" not in text:
            score = 0

        if score > max_score:
            max_score = score
            best_theme = theme

    return region, best_theme

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext[:300] + "..." if len(cleantext) > 300 else cleantext

def get_og_image(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_og = soup.find('meta', property='og:image')
            if meta_og and meta_og.get('content'):
                return meta_og['content']
    except Exception:
        pass
    return None

def get_fallback_image(theme):
    # Mapping themes to english keywords for loremflickr
    # loremflickr is a free service that returns a real photo based on keywords via Flickr
    theme_keywords = {
        "Geopolítica e Segurança": "military",
        "Política Internacional": "politics",
        "Política Brasileira": "brasil,politics",
        "Economia Internacional": "economy",
        "Economia Brasileira": "economy,brasil",
        "Comércio e Finanças": "finance",
        "Meio Ambiente e Clima": "nature,climate",
        "Ciência, Tecnologia e Inovação": "technology",
        "Direitos Humanos, Sociedade e Migrações": "society,people",
        "Saúde": "health",
        "Direito Internacional e Instituições": "justice,law",
        "Cultura, Mídia e Sociedade": "culture,art",
        "Outros / Multitemático": "news"
    }
    keyword = theme_keywords.get(theme, "news")
    # Using 800x450 resolution which fits standard widescreen
    return f"https://loremflickr.com/800/450/{keyword}?lock={hash(keyword) % 1000}"

def extract_image(entry, summary_html, article_url, theme):
    # 1. RSS media:content
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url')
    # 2. RSS media_thumbnail
    if 'media_thumbnail' in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get('url')
    # 3. RSS enclosures
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image'):
                return enc.get('href')
    # 4. Embedded image in summary
    img_match = re.search(r'<img[^>]+src="([^">]+)"', summary_html)
    if img_match:
        return img_match.group(1)
    
    # 5. Scrape original site for og:image
    og_img = get_og_image(article_url)
    if og_img:
        return og_img
        
    # 6. Final fallback: Theme-based real photo via loremflickr API
    return get_fallback_image(theme)

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
                
                # Classify theme and region FIRST so we can use theme for fallback image
                region, theme = categorize(title, summary, src['name'], src['origin'])
                
                image_url = extract_image(entry, summary_html, url, theme)
                
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
    all_news = all_news[:150]
    
    output_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "articles": all_news
    }
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    highlights = [n for n in all_news if n['image']][:6]
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

    dist = {}
    for n in all_news:
        dist[n['theme']] = dist.get(n['theme'], 0) + 1
    
    print("\n--- DISTRIBUIÇÃO DE TEMAS ---")
    for t, c in sorted(dist.items(), key=lambda x: x[1], reverse=True):
        print(f"{t}: {c}")
    print("-----------------------------\n")

if __name__ == "__main__":
    scrape()
