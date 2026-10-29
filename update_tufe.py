import json, re, os, sys, urllib.request
from datetime import datetime

JSON_FILE_PATH = "tufe-rates.json"

def fetch_latest_tufe_rate():
    now = datetime.now()
    target_key = f"{now.year}-{now.month:02d}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    sources = [
        "https://www.bloomberght.com/enflasyon",
        "https://finans.mynet.com/enflasyon-haberleri/"
    ]
    extracted_rate = None
    for url in sources:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as res:
                html = res.read().decode('utf-8', errors='ignore')
                matches = re.findall(r'(?:on\s*iki\s*ayl[ıi]k\s*ortalama|kira\s*art[ıi][sş]\s*oran[ıi])[^%0-9]{1,100}%\s*(\d{1,2}[.,]\d{1,2})', html, re.IGNORECASE)
                if matches:
                    val = float(matches[0].replace(',', '.'))
                    if 10.0 <= val <= 95.0:
                        extracted_rate = val
                        break
        except Exception:
            pass
    return target_key, extracted_rate

def update_rates_json(target_key, new_rate):
    if not os.path.exists(JSON_FILE_PATH): return False
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    rates = data.get("rates", {})
    if target_key in rates and rates[target_key] == new_rate:
        return False
    rates[target_key] = new_rate
    data["rates"] = dict(sorted(rates.items()))
    data["updatedAt"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

if __name__ == "__main__":
    k, r = fetch_latest_tufe_rate()
    if r is not None:
        update_rates_json(k, r)
