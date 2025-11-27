# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
OGLight Patcher - Adapts OGLight for OGame Ninja
Version: 2.1 - Updated for OGLight 5.3.2 + BUGFIXES
"""

import hashlib
import sys
import requests

# Configuration
WEBSTORE_URL = "https://update.greasyfork.org/scripts/514909/OGLight.user.js"
EXPECTED_SHA256 = "75f877eb9d6435e9c9466b1bc9dfc0e768f1a5e37ae311b1770c999b317e748c"
OUTPUT_FILE = "OGLight_Ninja.user.js"

def download_file(url):
    """Downloads the file from URL"""
    print(f"[*] Downloading file from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print("[+] Download completed!")
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"[!] Error downloading file: {e}")
        sys.exit(1)

def validate_sha256(content, expected_sha):
    """Validates the file's SHA256"""
    actual_sha = hashlib.sha256(content).hexdigest()
    print(f"[*] Expected SHA256: {expected_sha}")
    print(f"[*] Current SHA256:  {actual_sha}")

    if actual_sha != expected_sha:
        print("[!] SHA256 mismatch! The file has been modified or there's a new version.")
        print("[!] Update EXPECTED_SHA256 if the change is intentional.")
        sys.exit(1)

    print("[+] SHA256 validated successfully!")

def apply_patches(content):
    """Applies all patches to the content"""
    print("\n[*] Applying patches...")

    # Convert bytes to string
    text = content.decode('utf-8')

    # Patch 1: Rename script
    text = text.replace(
        '@name            OGLight',
        "@name            OGLight Ninja (CellMaster's Patcher)",
        1
    )
    print("  [+] Patch 1/15: Script name changed")

    # Patch 2: Replace @match with universal pattern
    text = text.replace(
        '// @match           https://*.ogame.gameforge.com/game/*\n',
        '// @match           *://*/bots/*/browser/html/*?page=*\n',
        1
    )
    print("  [+] Patch 2/15: @match simplified to universal pattern")

    # Patch 3: Remove auto-update URLs (prevents overwriting patched version)
    text = text.replace(
        '// @downloadURL https://update.greasyfork.org/scripts/514909/OGLight.user.js\n',
        '',
        1
    )
    text = text.replace(
        '// @updateURL https://update.greasyfork.org/scripts/514909/OGLight.meta.js\n',
        '',
        1
    )
    print("  [+] Patch 3/15: Auto-update URLs removed")

    # Patch 4: Inject variables after ==/UserScript==
    userscript_injection = r'''// ==/UserScript==

	const universeNum = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href)[1];
	const lang = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href)[2];
	const UNIVERSE = "s" + universeNum + "-" + lang;
	const PROTOCOL = window.location.protocol;
	const HOST = window.location.host;
	const PLAYER_ID = document.querySelector("meta[name=ogame-player-id]").content;
	const localStoragePrefix = UNIVERSE + "-" + PLAYER_ID + "-";
'''
    text = text.replace('// ==/UserScript==', userscript_injection, 1)
    print("  [+] Patch 4/15: Environment variables injected")

    # Patch 5: Add prefix to localStorage
    count = text.count("localStorage.getItem('ogl-ptreTK')")
    text = text.replace(
        "localStorage.getItem('ogl-ptreTK')",
        "localStorage.getItem(localStoragePrefix+'ogl-ptreTK')",
        2
    )
    text = text.replace(
        "localStorage.setItem('ogl-ptreTK',",
        "localStorage.setItem(localStoragePrefix+'ogl-ptreTK',",
        1
    )
    print(f"  [+] Patch 5/15: localStorage prefixed ({count+1} occurrences)")

    # Patch 6: Replace Server ID retrieval
    text = text.replace(
        "this.server.id = window.location.host.replace(/\\D/g,'');",
        "this.server.id=document.querySelector('head meta[name=\"ogame-universe\"]').getAttribute('content').replace(/\\D/g,'');",
        1
    )
    print("  [+] Patch 6/15: Server ID via meta tag")

    # Patch 7: Replace Lang retrieval
    text = text.replace(
        'this.account.lang = /oglocale=([a-z]+);/.exec(document.cookie)[1];',
        'this.account.lang=lang;',
        1
    )
    print("  [+] Patch 7/15: Lang via variable")

    # Patch 8: Replace crypto.randomUUID()
    uuid_replacement = r'''let uuid = ['xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
}), 0];'''
    text = text.replace('let uuid = [crypto.randomUUID(), 0];', uuid_replacement, 1)
    print("  [+] Patch 8/15: crypto.randomUUID() replaced")

    # Patch 9: Fix playerData.xml URL
    text = text.replace(
        'url:`https://${window.location.host}/api/playerData.xml?id=${player.uid}`,',
        'url:`${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/playerData.xml?id=${player.uid}`,',
        1
    )
    print("  [+] Patch 9/15: playerData.xml URL fixed")

    # Patch 10: Fix serverData.xml URL
    text = text.replace(
        'url:`https://${window.location.host}/api/serverData.xml`,',
        'url:`${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/serverData.xml`,',
        1
    )
    print("  [+] Patch 10/15: serverData.xml URL fixed")

    # Patch 11: Fix player link
    text = text.replace(
        '${player.name} <a href="https://${window.location.host}/game/index.php?page=highscore',
        '${player.name} <a href="${window.location.protocol}//${window.location.host}${window.location.pathname}?page=highscore',
        1
    )
    print("  [+] Patch 11/15: Player link fixed")

    # Patch 12: Fix message URL
    text = text.replace(
        'href:`https://${window.location.host}/game/index.php?page=componentOnly&component=messagedetails&messageId=${message.id}`',
        'href:`${window.location.protocol}//${window.location.host}${window.location.pathname}?page=componentOnly&component=messagedetails&messageId=${message.id}`',
        1
    )
    print("  [+] Patch 12/15: Message URL fixed")

    # Patch 13: Remove generic URLs
    count = text.count('https://${window.location.host}/game/index.php')
    text = text.replace('https://${window.location.host}/game/index.php', '', 30)
    print(f"  [+] Patch 13/15: Generic URLs removed ({count} occurrences)")

    # Patch 14: ADAPT multi-session logic for OGame Ninja (not remove - just adapt!)
    # Extract old_block directly from text (no external file needed)
    start_marker = '// get the account ID in cookies'
    end_marker = "const accountID = cookieAccounts[cookieAccounts.length-1].replace(/\\D/g, '');"

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker, start_idx)

    if start_idx == -1 or end_idx == -1:
        print("  [!] Patch 14/15: FAILED - Could not find multi-session block!")
        sys.exit(1)

    old_block = text[start_idx:end_idx + len(end_marker)]

    # ADAPTED VERSION: Use meta tag instead of cookies, but keep validation logic
    new_block = '''// get the account ID from meta tag (OGame Ninja adaptation)
        const accountMeta = document.querySelector('head meta[name="ogame-player-id"]');

        // validate session exists (adapted for OGame Ninja)
        if(!accountMeta || !accountMeta.content)
        {
            console.error('[OGLight Ninja] No player ID found in meta tag - session may be invalid');
            alert('Session error: Unable to retrieve player ID. Please refresh the page.');
            return;
        }

        const accountID = accountMeta.getAttribute('content').replace(/\\D/g, '');

        // additional validation
        if(!accountID || accountID === '0')
        {
            console.error('[OGLight Ninja] Invalid player ID:', accountID);
            alert('Session error: Invalid player ID detected. Please refresh the page.');
            return;
        }'''

    if old_block in text:
        text = text.replace(old_block, new_block, 1)
        print("  [+] Patch 14/15: Multi-session logic ADAPTED for OGame Ninja (keeps validation)")
    else:
        print("  [!] Patch 14/15: FAILED - Old text not found!")
        sys.exit(1)

    # Patch 15: Add error handling in variable extraction (BUGFIX - prevents crash)
    text = text.replace(
        '''	const universeNum = /browser\\/html\\/s(\\d+)-(\\w+)/.exec(window.location.href)[1];
	const lang = /browser\\/html\\/s(\\d+)-(\\w+)/.exec(window.location.href)[2];''',
        '''	const urlMatch = /browser\\/html\\/s(\\d+)-(\\w+)/.exec(window.location.href);
	if(!urlMatch) { console.error('[OGLight Ninja] Invalid URL - expected format: browser/html/sXXX-xx'); throw new Error('Invalid OGame Ninja URL format'); }
	const universeNum = urlMatch[1];
	const lang = urlMatch[2];''',
        1
    )
    print("  [+] Patch 15/15: Regex error handling (BUGFIX - prevents crash on invalid URLs)")

    print("[+] All 15 patches applied successfully!\n")

    return text.encode('utf-8')

def save_file(content, filename):
    """Saves the patched file"""
    print(f"[*] Saving file: {filename}")
    try:
        with open(filename, 'wb') as f:
            f.write(content)
        print(f"[+] File saved successfully!")
    except Exception as e:
        print(f"[!] Error saving file: {e}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("OGLight Patcher - OGame Ninja Edition v2.1")
    print("Supported OGLight version: 5.3.2 + BUGFIXES")
    print("=" * 60)
    print()

    # 1. Download file
    content = download_file(WEBSTORE_URL)

    # 2. Validate SHA256
    validate_sha256(content, EXPECTED_SHA256)

    # 3. Apply patches
    patched_content = apply_patches(content)

    # 4. Save file
    save_file(patched_content, OUTPUT_FILE)

    print()
    print("=" * 60)
    print("Process completed successfully!")
    print(f"Generated file: {OUTPUT_FILE}")
    print("Install the file in OGame Ninja browser/Tampermonkey")
    print("=" * 60)

if __name__ == "__main__":
    main()
