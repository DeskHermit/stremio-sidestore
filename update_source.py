#!/usr/bin/env python3

import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

UPSTREAM_URL = (
    "https://gorlev.github.io/stremio-altstore/stremio-ios.json"
)
OUTPUT_FILE = Path(__file__).resolve().parent / "source.json"
BUNDLE_ID = "com.stremio.pal"


def fetch_source():
    request = urllib.request.Request(
        UPSTREAM_URL,
        headers={
            "User-Agent": "Stremio-SideStore-Source-Updater/1.0",
            "Accept": "application/json",
        },
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))


def require_text(obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing or invalid {key}")
    return value


def validate_app(app):
    for key in (
        "name",
        "bundleIdentifier",
        "developerName",
        "localizedDescription",
        "iconURL",
    ):
        require_text(app, key)

    versions = app.get("versions")
    if not isinstance(versions, list) or not versions:
        raise ValueError("Stremio has no versions")

    seen = set()

    for version in versions:
        if not isinstance(version, dict):
            raise ValueError("Invalid version entry")

        number = require_text(version, "version")
        build = require_text(version, "buildVersion")
        date = require_text(version, "date")
        datetime.fromisoformat(date.replace("Z", "+00:00"))

        identity = (number, build)
        if identity in seen:
            raise ValueError(f"Duplicate version/build: {identity}")
        seen.add(identity)

        size = version.get("size")
        if type(size) is not int or size <= 0:
            raise ValueError(f"Invalid download size for {identity}")

        url = urlsplit(require_text(version, "downloadURL"))
        if (
            url.scheme != "https"
            or url.netloc != "dl.strem.io"
            or not url.path.startswith("/apple/")
            or "/ios/" not in url.path
            or not url.path.lower().endswith(".ipa")
        ):
            raise ValueError(
                f"Expected an official Stremio iOS IPA: {url.geturl()}"
            )

        digest = version.get("sha256")
        if digest is not None and (
            not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-fA-F]{64}", digest)
        ):
            raise ValueError(f"Invalid SHA-256 for {identity}")

    permissions = app.get("appPermissions")
    if not isinstance(permissions, dict):
        raise ValueError("Missing appPermissions")


def write_source(data):
    content = json.dumps(
        data, indent=2, ensure_ascii=False, sort_keys=True
    ) + "\n"

    if OUTPUT_FILE.exists():
        if OUTPUT_FILE.read_text(encoding="utf-8") == content:
            print("No changes.")
            return

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=OUTPUT_FILE.parent,
            prefix=".source-",
            suffix=".json",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)

        os.replace(temporary_path, OUTPUT_FILE)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    print(f"Updated {OUTPUT_FILE.name}")


def main():
    source_url = os.environ.get("SOURCE_URL", "").strip()
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(
            "Set SOURCE_URL to your repository's public raw source.json URL"
        )

    print(f"Fetching {UPSTREAM_URL}")
    upstream = fetch_source()

    if not isinstance(upstream, dict):
        raise ValueError("Upstream source must be a JSON object")

    apps = upstream.get("apps")
    if not isinstance(apps, list):
        raise ValueError("Upstream source has no apps array")

    matches = [
        app for app in apps
        if isinstance(app, dict)
        and app.get("bundleIdentifier") == BUNDLE_ID
    ]
    if len(matches) != 1:
        raise ValueError("Expected exactly one full Stremio app")

    app = matches[0]
    validate_app(app)

    app.pop("marketplaceID", None)

    latest = app["versions"][0]
    for destination, origin in (
        ("version", "version"),
        ("versionDate", "date"),
        ("versionDescription", "localizedDescription"),
        ("downloadURL", "downloadURL"),
        ("size", "size"),
        ("minOSVersion", "minOSVersion"),
    ):
        if origin in latest:
            app[destination] = latest[origin]
        else:
            app.pop(destination, None)

    source_id = hashlib.sha256(source_url.encode()).hexdigest()[:16]
    data = {
        "name": "Stremio (SideStore)",
        "identifier": f"community.stremio.mirror.{source_id}",
        "subtitle": "Unofficial Stremio source for iPhone and iPad",
        "description": (
            "Unofficial mirror of gorlev/stremio-altstore. "
            "IPA downloads are hosted by Stremio at dl.strem.io."
        ),
        "website": "https://github.com/gorlev/stremio-altstore",
        "iconURL": app["iconURL"],
        "tintColor": "7055D9",
        "sourceURL": source_url,
        "apps": [app],
        "news": [],
    }

    write_source(data)
    print(
        f"Latest upstream release: {latest['version']} "
        f"(build {latest['buildVersion']})"
    )
    print(f"SideStore source URL: {source_url}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Update failed: {error}", file=sys.stderr)
        sys.exit(1)
