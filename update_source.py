import json
import urllib.request
import traceback

PROXY_SOURCE_URL = "https://githubusercontent.com"
OUTPUT_FILE = "source.json"

def main():
    print(f"Fetching pre-converted source from community proxy: {PROXY_SOURCE_URL}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        req = urllib.request.Request(PROXY_SOURCE_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        data["name"] = "Stremio (SideStore/LiveContainer)"
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Safely mirrored update metadata to {OUTPUT_FILE}")

    except Exception as e:
        print("!!! AN ERROR OCCURRED DURING SCRIPT RUN !!!")
        print(f"Error details: {e}")
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
