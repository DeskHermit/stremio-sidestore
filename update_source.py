import json
import urllib.request
import traceback

OFFICIAL_SOURCE_URL = "https://strem.io"
OUTPUT_FILE = "source.json"

def main():
    print(f"Fetching official source from: {OFFICIAL_SOURCE_URL}")
    try:
        req = urllib.request.Request(
            OFFICIAL_SOURCE_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
        
        print("Successfully downloaded source JSON. Parsing apps...")
        
        if "apps" in data:
            for app in data["apps"]:
                app_name = app.get("name", "Unknown App")
                print(f"Processing app: {app_name}")
                
                if "versions" in app and app["versions"]:
                    latest_version_dir = app["versions"][0].get("downloadURL", "").replace("manifest.json", "")
                    if latest_version_dir and not app.get("iconURL"):
                        app["iconURL"] = f"{latest_version_dir}AppIcon60x60@2x.png"
                
                for version in app.get("versions", []):
                    original_url = version.get("downloadURL", "")
                    if "manifest.json" in original_url:
                        direct_ipa_url = original_url.replace("manifest.json", "Stremio.ipa")
                        version["downloadURL"] = direct_ipa_url
                        print(f" -> Converted version {version.get('version')} to direct IPA target")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Success! Saved modified configuration to {OUTPUT_FILE}")

    except Exception as e:
        print("!!! AN ERROR OCCURRED DURING EXECUTION !!!")
        print(str(e))
        traceback.print_exc()
        raise e

if __name__ == "__main__":
    main()
