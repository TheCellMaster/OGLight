# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
OGLight Patcher - Adapts OGLight for OGame Ninja
=================================================

Version: 2.8
Author: CellMaster
License: MIT
Source OGLight: https://greasyfork.org/scripts/514909-oglight

Description:
    This script downloads the official OGLight userscript and applies patches
    to make it compatible with OGame Ninja environment. The patches handle
    differences in URL structure, API endpoints, session management, and
    localStorage isolation for multi-account support.

Supported OGLight Version: 5.3.3

Usage:
    python patcher.py

Output:
    OGLight_Ninja.user.js - Ready to install in Tampermonkey/Greasemonkey

Patches Applied (19 total):
    1.  Script name changed to "OGLight Ninja"
    2.  @match pattern updated for Ninja URL structure
    3.  Auto-update URLs removed (prevents overwriting)
    4.  Environment variables injected with error handling (UNIVERSE, PLAYER_ID, etc.)
    5.  Team Key (PTRE) stored per universe (shared across accounts)
    6.  Server ID extracted from meta tag
    7.  Language extracted from URL
    8.  crypto.randomUUID() polyfill for compatibility (3 occurrences)
    9.  playerData.xml API URL fixed
    10. serverData.xml API URL fixed
    11. players.xml API URL fixed
    12. Player highscore link fixed (uses PROTOCOL/HOST)
    13. Message detail URL fixed (uses PROTOCOL/HOST)
    14. Generic game URLs converted to Ninja format
    15. Multi-session logic adapted (meta tag instead of cookies)
    16. DBName uses UNIVERSE variable for proper isolation
    17. French keyboard (AZERTY) detection fixed
    18. Legacy DB migration adapted for Ninja
    19. Remaining localStorage keys prefixed with UNIVERSE (multi-account isolation)

CHANGELOG:
----------
v1.0 - Initial release with 14 patches
v2.0 - Multi-session logic adapted for OGame Ninja
v2.1 - Regex error handling added
v2.2 - DBName uses UNIVERSE variable
v2.3 - French keyboard detection fixed
v2.4 - DB Migration fix added
v2.5 - Team Key storage optimization
       - Team Key (ogl-ptreTK) now stored per UNIVERSE instead of per PLAYER_ID
       - Before: s261-en-118964-ogl-ptreTK (required config for each account)
       - After:  s261-en-ogl-ptreTK (config once per universe, shared by all accounts)
       - This matches the original OGLight behavior where all accounts in same
         universe share the same Team Key automatically
v2.6 - Code optimization and bug fixes
       - Patch 4: Error handling now included directly (unified with old Patch 16)
       - Patch 8: Now converts ALL crypto.randomUUID() calls (1 array + 2 item.uid)
       - Patch 14: URLs now CONVERTED instead of REMOVED (fixes fetch/navigation)
       - Total patches reduced from 19 to 18 (cleaner code)
v2.7 - Full localStorage isolation for multi-account support
       - Patch 12 & 13: Now use PROTOCOL/HOST variables (consistency fix)
       - Patch 19: Added - Prefixes remaining localStorage keys with UNIVERSE
         - ogl-redirect, ogl_minipics, ogl_menulayout, ogl_colorblind, ogl_sidepanelleft
         - Prevents configuration conflicts in multi-account scenarios
       - Total patches: 19
v2.8 - Updated for OGLight 5.3.3
       - SHA256 updated for new version
       - Removed unnecessary replace() limits for future-proofing:
         - Patch 5: Team Key now uses unlimited replace (was limited to 2+1)
         - Patch 8b: item.uid now uses unlimited replace (was limited to 2)
         - Patch 14: Game URLs now uses unlimited replace (was limited to 30)
       - All patches verified compatible with 5.3.3 changes:
         - ogl-redirect: 1 get + 4 set (was 1+1)
         - ogl_menulayout: 1 get + 2 set (was 1+1)
       - Patcher is now more robust against future OGLight updates
"""

import hashlib
import sys
import requests

# Configuration
WEBSTORE_URL = "https://update.greasyfork.org/scripts/514909/OGLight.user.js"
EXPECTED_SHA256 = "371795e1a20f04040c00fc9568b92fe536960aa115a49d406f3ae60a6405b432"
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
    print("  [+] Patch 1/19: Script name changed")

    # Patch 2: Replace @match with universal pattern
    text = text.replace(
        '// @match           https://*.ogame.gameforge.com/game/*\n',
        '// @match           *://*/bots/*/browser/html/*?page=*\n',
        1
    )
    print("  [+] Patch 2/19: @match simplified to universal pattern")

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
    print("  [+] Patch 3/19: Auto-update URLs removed")

    # Patch 4: Inject environment variables with error handling
    userscript_injection = r'''// ==/UserScript==

	const urlMatch = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href);
	if(!urlMatch) { console.error('[OGLight Ninja] Invalid URL - expected format: browser/html/sXXX-xx'); throw new Error('Invalid OGame Ninja URL format'); }
	const universeNum = urlMatch[1];
	const lang = urlMatch[2];
	const UNIVERSE = "s" + universeNum + "-" + lang;
	const PROTOCOL = window.location.protocol;
	const HOST = window.location.host;
	const PLAYER_ID = document.querySelector("meta[name=ogame-player-id]").content;
	const localStoragePrefix = UNIVERSE + "-" + PLAYER_ID + "-";
'''
    text = text.replace('// ==/UserScript==', userscript_injection, 1)
    print("  [+] Patch 4/19: Environment variables injected (with error handling)")

    # Patch 5: Add UNIVERSE prefix to Team Key (shared per universe, not per player)
    # This allows all accounts in the same universe to share the same Team Key
    count_get = text.count("localStorage.getItem('ogl-ptreTK')")
    count_set = text.count("localStorage.setItem('ogl-ptreTK',")
    text = text.replace(
        "localStorage.getItem('ogl-ptreTK')",
        "localStorage.getItem(UNIVERSE+'-ogl-ptreTK')"
    )
    text = text.replace(
        "localStorage.setItem('ogl-ptreTK',",
        "localStorage.setItem(UNIVERSE+'-ogl-ptreTK',"
    )
    print(f"  [+] Patch 5/19: Team Key prefixed with UNIVERSE ({count_get} get + {count_set} set)")

    # Patch 6: Replace Server ID retrieval
    text = text.replace(
        "this.server.id = window.location.host.replace(/\\D/g,'');",
        "this.server.id=document.querySelector('head meta[name=\"ogame-universe\"]').getAttribute('content').replace(/\\D/g,'');",
        1
    )
    print("  [+] Patch 6/19: Server ID via meta tag")

    # Patch 7: Replace Lang retrieval
    text = text.replace(
        'this.account.lang = /oglocale=([a-z]+);/.exec(document.cookie)[1];',
        'this.account.lang=lang;',
        1
    )
    print("  [+] Patch 7/19: Lang via variable")

    # Patch 8: Replace all crypto.randomUUID() occurrences
    # 8a: Replace array initialization pattern (1 occurrence)
    uuid_replacement = r'''let uuid = ['xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
}), 0];'''
    text = text.replace('let uuid = [crypto.randomUUID(), 0];', uuid_replacement, 1)

    # 8b: Replace item.uid assignment pattern (no limit - catches all occurrences)
    uid_polyfill = r"""'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) { var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8); return v.toString(16); })"""
    count_uid = text.count('item.uid = crypto.randomUUID();')
    text = text.replace('item.uid = crypto.randomUUID();', f'item.uid = {uid_polyfill};')
    print(f"  [+] Patch 8/19: crypto.randomUUID() replaced (1 array + {count_uid} item.uid)")

    # Patch 9: Fix playerData.xml URL
    text = text.replace(
        'url:`https://${window.location.host}/api/playerData.xml?id=${player.uid}`,',
        'url:`${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/playerData.xml?id=${player.uid}`,',
        1
    )
    print("  [+] Patch 9/19: playerData.xml URL fixed")

    # Patch 10: Fix serverData.xml URL
    text = text.replace(
        'url:`https://${window.location.host}/api/serverData.xml`,',
        'url:`${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/serverData.xml`,',
        1
    )
    print("  [+] Patch 10/19: serverData.xml URL fixed")

    # Patch 11: Fix players.xml URL (API endpoint)
    text = text.replace(
        'return fetch(`https://${window.location.host}/api/players.xml`,',
        'return fetch(`${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/players.xml`,',
        1
    )
    print("  [+] Patch 11/19: players.xml URL fixed")

    # Patch 12: Fix player link (using PROTOCOL/HOST for consistency)
    text = text.replace(
        '${player.name} <a href="https://${window.location.host}/game/index.php?page=highscore',
        '${player.name} <a href="${PROTOCOL}//${HOST}${window.location.pathname}?page=highscore',
        1
    )
    print("  [+] Patch 12/19: Player link fixed")

    # Patch 13: Fix message URL (using PROTOCOL/HOST for consistency)
    text = text.replace(
        'href:`https://${window.location.host}/game/index.php?page=componentOnly&component=messagedetails&messageId=${message.id}`',
        'href:`${PROTOCOL}//${HOST}${window.location.pathname}?page=componentOnly&component=messagedetails&messageId=${message.id}`',
        1
    )
    print("  [+] Patch 13/19: Message URL fixed")

    # Patch 14: Convert game URLs to Ninja format (no limit - catches all occurrences)
    count = text.count('https://${window.location.host}/game/index.php')
    text = text.replace(
        'https://${window.location.host}/game/index.php',
        '${PROTOCOL}//${HOST}${window.location.pathname}'
    )
    print(f"  [+] Patch 14/19: Game URLs converted to Ninja format ({count} occurrences)")

    # Patch 15: ADAPT multi-session logic for OGame Ninja (not remove - just adapt!)
    # Extract old_block directly from text (no external file needed)
    start_marker = '// get the account ID in cookies'
    end_marker = "const accountID = cookieAccounts[cookieAccounts.length-1].replace(/\\D/g, '');"

    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker, start_idx)

    if start_idx == -1 or end_idx == -1:
        print("  [!] Patch 15/19: FAILED - Could not find multi-session block!")
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
        print("  [+] Patch 15/19: Multi-session logic ADAPTED for OGame Ninja (keeps validation)")
    else:
        print("  [!] Patch 15/19: FAILED - Old text not found!")
        sys.exit(1)

    # Patch 16: Fix DBName to use UNIVERSE variable instead of window.location.host
    text = text.replace(
        "this.DBName = `${accountID}-${window.location.host.split('.')[0]}`;",
        "this.DBName = `${accountID}-${UNIVERSE}`;",
        1
    )
    print("  [+] Patch 16/19: DBName uses UNIVERSE variable")

    # Patch 17: Fix French keyboard detection (AZERTY layout)
    text = text.replace(
        "galaxyUp: window.location.host.split(/[-.]/)[1] == 'fr' ? 'z' : 'w',",
        "galaxyUp: lang == 'fr' ? 'z' : 'w',",
        1
    )
    text = text.replace(
        "galaxyLeft: window.location.host.split(/[-.]/)[1] == 'fr' ? 'q' : 'a',",
        "galaxyLeft: lang == 'fr' ? 'q' : 'a',",
        1
    )
    print("  [+] Patch 17/19: French keyboard detection fixed")

    # Patch 18: Fix legacy DB migration for OGame Ninja
    # Uses meta tag ogame-universe instead of window.location.host
    text = text.replace(
        '''        // fix beta old DB
        if(!GM_getValue(this.DBName) && GM_getValue(window.location.host))
        {
            GM_setValue(this.DBName, GM_getValue(window.location.host));
            GM_deleteValue(window.location.host);
            window.location.reload();
        }''',
        '''        // fix beta old DB - ADAPTED for OGame Ninja
        const oldHost = document.querySelector('meta[name="ogame-universe"]').getAttribute('content');
        if(!GM_getValue(this.DBName) && GM_getValue(oldHost))
        {
            GM_setValue(this.DBName, GM_getValue(oldHost));
            GM_deleteValue(oldHost);
            window.location.reload();
        }''',
        1
    )
    print("  [+] Patch 18/19: Legacy DB migration fixed for Ninja")

    # Patch 19: Prefix remaining localStorage keys with UNIVERSE
    # These keys were global and caused conflicts in multi-account scenarios
    localStorage_keys = ['ogl-redirect', 'ogl_minipics', 'ogl_menulayout', 'ogl_colorblind', 'ogl_sidepanelleft']
    total_replacements = 0
    for key in localStorage_keys:
        count_get = text.count(f"localStorage.getItem('{key}')")
        count_set = text.count(f"localStorage.setItem('{key}',")
        text = text.replace(f"localStorage.getItem('{key}')", f"localStorage.getItem(UNIVERSE+'-{key}')")
        text = text.replace(f"localStorage.setItem('{key}',", f"localStorage.setItem(UNIVERSE+'-{key}',")
        total_replacements += count_get + count_set
        if count_get + count_set > 0:
            print(f"    - {key}: {count_get} get + {count_set} set")
    print(f"  [+] Patch 19/19: Remaining localStorage keys prefixed ({total_replacements} occurrences)")

    print("[+] All 19 patches applied successfully!\n")

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
    print("OGLight Patcher - OGame Ninja Edition v2.8")
    print("Supported OGLight version: 5.3.3 (19 patches)")
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
    print("=" * 60)

if __name__ == "__main__":
    main()
