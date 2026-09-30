import json
import urllib.request
import traceback

OFFICIAL_SOURCE_URL = "https://strem.io"
OUTPUT_FILE = "source.json"

def main():
    print(f"Fetching official source from: {OFFICIAL_SOURCE_URL}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        req = urllib.request.Request(OFFICIAL_SOURCE_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
        
        print("Successfully downloaded source JSON. Modifying URLs for SideStore compatibility...")
        
        if "apps" in data:
            for app in data["apps"]:
                app_name = app.get("name", "Unknown App")
                print(f"Processing app: {app_name}")
                
                for version in app.get("versions", []):
                    original_url = version.get("downloadURL", "")
                    if "manifest.json" in original_url:
                        direct_ipa_url = original_url.replace("manifest.json", "Stremio.ipa")
                        version["downloadURL"] = direct_ipa_url
                        print(f" -> Converted version {version.get('version')} to direct IPA download link.")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Saved modified configuration to {OUTPUT_FILE}")

    except Exception as e:
        print("!!! AN ERROR OCCURRED DURING SCRIPT RUN !!!")
        print(f"Error details: {e}")
        traceback.print_exc()
        exit(0) 

if __name__ == "__main__":
    main()
