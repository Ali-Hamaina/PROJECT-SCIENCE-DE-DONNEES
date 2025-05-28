import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://medicament.ma"
LISTING_URL = f"{BASE_URL}/listing-des-medicaments/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_medicament_links(max_meds=5000):
    """Récupère les liens vers les pages de médicaments"""
    links = []
    page = 1
    while len(links) < max_meds:
        url = LISTING_URL + f"?page={page}"
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, "html.parser")
        trs = soup.select("tbody tr")
        if not trs:
            break
        for tr in trs:
            a = tr.find("a")
            if a and "href" in a.attrs:
                links.append(a["href"])
                if len(links) >= max_meds:
                    break
        page += 1
    return links

def extract_name_from_url(url):
    """Extrait le nom du médicament depuis l'URL"""
    if url.endswith('/'):
        url = url[:-1]
    return url.split("/")[-1]

def parse_medicament_page(url):
    """Parse une page de médicament et extrait les données"""
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return {}

    # Extract medicine slug from URL
    name = extract_name_from_url(url)

    soup = BeautifulSoup(res.text, "html.parser")
    data = {"name": name}

    table = soup.find("table", class_="table-details")
    if table:
        for row in table.find_all("tr"):
            field = row.find(class_='field')
            value = row.find(class_='value')
            if field and value:
                label = field.get_text(strip=True)
                content = value.get_text(separator=' ', strip=True)
                data[label] = content

        # Get Indication(s) with HTML line breaks preserved
        indications_row = table.find("tr", class_="field-indication")
        if indications_row:
            value = indications_row.find(class_="value")
            if value:
                data['Indication(s)'] = value.decode_contents().replace('<br>', '\n').strip()
    return data

def extract_boite(presentation):
    """Extrait les informations de boîte depuis la présentation"""
    if not presentation:
        return ""
    match = re.search(r"Boite\s+de\s+[\w\s'-]+", presentation, re.IGNORECASE)
    if match:
        return match.group(0)
    return ""

def extract_forme(name):
    """Extrait la forme pharmaceutique depuis le nom"""
    forms = ['comprime', 'gélule', 'solution', 'suspension', 'pommade', 'goutte', 'sirop', 'suppositoire',
             'capsule', 'poudre', 'gel', 'patch', 'sublingual', 'injectable', 'crème']
    if not name:
        return None
    lname = name.lower()
    for form in forms:
        if form in lname:
            return form
    return None

def extract_route(name, indication):
    """Détermine la voie d'administration"""
    name = str(name).lower() if name else ''
    indication = str(indication).lower() if indication else ''
    if "sublingual" in name or "sublingual" in indication:
        return "Sublinguale"
    if any(x in name for x in ["comprime", "gélule", "capsule", "orale"]):
        return "Orale"
    if "injectable" in name or "injection" in indication:
        return "Injectable"
    if "pommade" in name or "crème" in name or "topique" in indication:
        return "Cutanée"
    return None

def extract_unit_count(boite):
    """Extrait le nombre d'unités depuis la boîte"""
    if not boite or not isinstance(boite, str):
        return None
    match = re.search(r'(\d+)', boite)
    return int(match.group(1)) if match else None

def clean_price(price):
    """Nettoie et convertit le prix en nombre"""
    if not price or not isinstance(price, str):
        return None
    # Remove "dh", "dhs", spaces, and commas
    price = re.sub(r'[^\d.]', '', price)
    try:
        return float(price)
    except:
        return None

def main():
    """Fonction principale de scraping"""
    max_meds = 5000

    print(f"🔍 Début du scraping de {max_meds} médicaments...")
    links = get_medicament_links(max_meds)
    print(f"✅ Trouvé {len(links)} liens de médicaments.")
    
    all_data = []

    for i, link in enumerate(links):
        print(f"[{i+1}/{len(links)}] Scraping: {link}")
        data = parse_medicament_page(link)
        
        # Ajouter les champs calculés
        data["Boite"] = extract_boite(data.get("Présentation", ""))
        data["Forme"] = extract_forme(data.get("name", ""))
        data["Voie d'administration"] = extract_route(data.get("name", ""), data.get("Indication(s)", ""))
        data["Unités"] = extract_unit_count(data["Boite"])
        data["PPV_num"] = clean_price(data.get("PPV", ""))
        
        # Calculer le prix unitaire
        if data["Unités"] and data["PPV_num"]:
            data["Prix Unitaire"] = data["PPV_num"] / data["Unités"]
        else:
            data["Prix Unitaire"] = None

        all_data.append(data)
        time.sleep(0.5)  # Délai pour éviter de surcharger le serveur

    # Créer le DataFrame
    df = pd.DataFrame(all_data)

    # Réorganiser les colonnes
    cols = ["name", "Boite", "Forme", "Voie d'administration", "Unités", "PPV_num", "Prix Unitaire"] \
        + [c for c in df.columns if c not in ("name", "Boite", "Forme", "Voie d'administration", "Unités", "PPV_num", "Prix Unitaire")]
    df = df[cols]

    # Sauvegarder les données
    df.to_csv("medicament_ma_top5000.csv", index=False)
    print("💾 Données sauvegardées dans medicament_ma_top5000.csv")
    print(f"📊 Dataset final: {len(df)} médicaments avec {len(df.columns)} colonnes")
    print(df.head())

if __name__ == "__main__":
    main()