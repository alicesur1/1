import urllib.request
import re

SOURCE_URL = "https://raw.githubusercontent.com/alicesur1/1/main/iptvorg.TR.m3u"
OUTPUT_FILE = "tr_sorted.m3u"

GROUP_KEYWORDS = {
    "Haber": ["haber", "news", "cnn", "ntv", "a haber", "24"],
    "Spor": ["spor", "sport", "bein", "s sport"],
    "Müzik": ["müzik", "music", "kral", "power"],
    "Çocuk": ["çocuk", "kids", "minika"],
    "Belgesel": ["belgesel", "discovery", "national"],
    "Dini": ["diyanet", "islam", "dini"]
}

GROUP_ORDER = ["Haber", "Spor", "Genel", "Müzik", "Çocuk", "Belgesel", "Dini"]
RES_ORDER = ["1080p", "720p", "SD"]

def get_resolution(name):
    n = name.lower()
    if "1080" in n:
        return "1080p"
    if "720" in n:
        return "720p"
    return "SD"

def get_group(name):
    n = name.lower()
    for group, keys in GROUP_KEYWORDS.items():
        for k in keys:
            if k in n:
                return group
    return "Genel"

def clean_name(name):
    return re.sub(r"\s*\(.*?p\)", "", name, flags=re.IGNORECASE).strip()

def download_lines():
    with urllib.request.urlopen(SOURCE_URL) as r:
        text = r.read().decode("utf-8", "ignore")
    return [l.strip() for l in text.splitlines() if l.strip()]

def main():
    lines = download_lines()
    channels = []

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            info = lines[i]
            name = info.split(",")[-1]
            j = i + 1

            # URL'yi bulana kadar ilerle
            while j < len(lines) and lines[j].startswith("#"):
                j += 1

            if j >= len(lines):
                break

            url = lines[j]

            res = get_resolution(name)
            group = get_group(name)
            clean = clean_name(name)

            channels.append({
                "res": res,
                "group": group,
                "name": f"{clean} ({res})",
                "url": url
            })
            i = j + 1
        else:
            i += 1

    if not channels:
        print("❌ Hiç kanal bulunamadı. Kaynak M3U formatını kontrol et.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("#EXTM3U\n\n")
        for res in RES_ORDER:
            for group in GROUP_ORDER:
                subset = [c for c in channels if c["res"] == res and c["group"] == group]
                if not subset:
                    continue

                out.write("############################\n")
                out.write(f"# {res} - {group}\n")
                out.write("############################\n")

                for c in subset:
                    out.write(f'#EXTINF:-1 group-title="{group}",{c["name"]}\n')
                    out.write(c["url"] + "\n")
                out.write("\n")

    print(f"✅ {len(channels)} kanal işlendi → tr_sorted.m3u oluşturuldu")

if __name__ == "__main__":
    main()