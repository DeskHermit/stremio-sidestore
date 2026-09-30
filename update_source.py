import json
import urllib.request

OFFICIAL_SOURCE_URL = "https://strem.io"
OUTPUT_FILE = "source.json"

try:
    # Fetch official Stremio source
    with urllib.request.urlopen(OFFICIAL_SOURCE_URL) as response:
        data = json.loads(response.read().decode())
    
    # Process apps to make them compatible with SideStore/LiveContainer
    if "apps" in data:
        for app in data["apps"]:
            # Standardize app icon to a direct asset if available
            if "versions" in app and app["versions"]:
                latest_version_dir = app["versions"][0].get("downloadURL", "").replace("manifest.json", "")
                if latest_version_dir:
                    app["iconURL"] = f"{latest_version_dir}AppIcon60x60@2x.png"
            
            # Loop through all versions and rewrite download URLs
            for version in app.get("versions", []):
                original_url = version.get("downloadURL", "")
                if "manifest.json" in original_url:
                    # Swap manifest.json logic with the raw binary file target
                    direct_ipa_url = original_url.replace("manifest.json", "Stremio.ipa")
                    version["downloadURL"] = direct_ipa_url

    # Save modified json back to repository
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Successfully generated SideStore compatible source.json")

except Exception as e:
    print(f"Error updating source file: {e}")
    exit(1)
