# OGLight Patcher for OGame Ninja

**Python adaptation of the original Go patcher** - Converts [OGLight](https://github.com/TheCellMaster/OGLight) userscript to work with [OGame Ninja](https://github.com/ogame-ninja)

## Overview

This project is a **Python port** of the [original Go-based patcher](https://github.com/ogame-ninja/extension-patcher) used to adapt browser extensions for OGame Ninja. The patcher automatically downloads the latest OGLight userscript and applies 19 patches to make it compatible with OGame Ninja's architecture.

### Why Python?

The original `patcher.go` was part of the OGame Ninja ecosystem but required:
- Go runtime environment
- Compilation step
- External dependencies (`github.com/ogame-ninja/extension-patcher`)

This Python version offers:
- **Zero compilation** - run directly with Python 3
- **Minimal dependencies** - only `requests` library
- **Easier maintenance** - simple text-based patching logic
- **Cross-platform** - works on Windows, Linux, macOS
- **Standalone** - no external framework required

---

## Features

### Original Patcher (Go)
```go
package main

import (
    ep "github.com/ogame-ninja/extension-patcher"
)

func main() {
    const (
        webstoreURL    = "https://openuserjs.org/install/nullNaN/OGLight.user.js"
        oglight_sha256 = "978c7932426a23b2c69d7f4be32ea4e8e3abbb6a3ea84d7278381be6336f55c3"
    )

    files := []ep.FileAndProcessors{
        ep.NewFile("OGLight.user.js", processOGLight),
    }

    ep.MustNew(ep.Params{
        ExpectedSha256: oglight_sha256,
        WebstoreURL:    webstoreURL,
        Files:          files,
    }).Start()
}
```

### This Patcher (Python v2.8)
```python
#!/usr/bin/env python3
"""
OGLight Patcher - Adapts OGLight for OGame Ninja
Version: 2.8 - Updated for OGLight 5.3.3
"""

# Self-contained, standalone implementation
# Downloads, validates SHA256, applies 19 patches, generates output
```

---

## What Was Adapted

### Architecture Changes

| Component | Go Version | Python Version |
|-----------|-----------|----------------|
| **Framework** | `github.com/ogame-ninja/extension-patcher` | Standalone implementation |
| **Language** | Go 1.x+ | Python 3.6+ |
| **Dependencies** | External package | `requests` only |
| **Build Process** | `go build` → binary | Direct execution |
| **Error Handling** | `MustReplaceN()` panic | Exception handling |
| **File Download** | Framework-managed | `requests.get()` |
| **SHA256 Validation** | Framework-managed | `hashlib.sha256()` |
| **Patch Application** | `replN()` helper | `str.replace()` |

### Key Improvements Over Original

1. **Multi-Account Support** (Patches 5, 16, 19)
   - localStorage keys isolated per universe/player
   - Team Key shared per universe (not per player)
   - Prevents configuration conflicts between accounts

2. **Session Validation Adapted** (Patch 15)
   - **Original Issue**: OGLight validates sessions using `prsess_` cookies (Gameforge method)
   - **Problem**: OGame Ninja doesn't use those cookies → forced logout
   - **Solution**: ADAPTED (not removed) validation logic to use meta tags while keeping security checks

3. **URL Validation** (Patch 4)
   - **Original Issue**: Regex extraction could crash on invalid URLs
   - **Problem**: `null[1]` access caused JavaScript error
   - **Solution**: Added pre-validation before accessing regex groups

4. **Enhanced Logging**
   - Go version: Silent operation via framework
   - Python version: Detailed progress output for each patch

---

## The 19 Patches

All patches from the original Go code were preserved and improved:

| # | Patch | Description |
|---|-------|-------------|
| 1 | Script Name | Renamed to "OGLight Ninja (CellMaster's Patcher)" |
| 2 | @match URLs | Universal pattern for Ninja URL structure |
| 3 | Auto-update | Removed @downloadURL/@updateURL (prevents overwriting) |
| 4 | Environment Vars | Injected UNIVERSE, PROTOCOL, HOST, PLAYER_ID with error handling |
| 5 | Team Key (PTRE) | Prefixed with UNIVERSE (shared per universe, not per player) |
| 6 | Server ID Source | `window.location.host` → meta tag `ogame-universe` |
| 7 | Language Source | Cookie `oglocale` → extracted from URL |
| 8 | UUID Generation | `crypto.randomUUID()` → polyfill (1 array + N item.uid) |
| 9 | playerData.xml URL | Hardcoded → dynamic with `/api/sXXX/lang/` format |
| 10 | serverData.xml URL | Hardcoded → dynamic |
| 11 | players.xml URL | Hardcoded → dynamic |
| 12 | Player Link URL | Hardcoded → uses PROTOCOL/HOST/pathname |
| 13 | Message URL | Hardcoded → uses PROTOCOL/HOST/pathname |
| 14 | Generic Game URLs | Converted to Ninja format (all occurrences) |
| 15 | **Multi-session Logic** | Adapted for meta tags (keeps validation) |
| 16 | DBName | Uses UNIVERSE variable for proper isolation |
| 17 | French Keyboard | AZERTY detection uses `lang` variable |
| 18 | Legacy DB Migration | Adapted for OGame Ninja meta tags |
| 19 | localStorage Keys | Remaining keys prefixed with UNIVERSE |

### Patch Details

#### Patch 1: Script Rename
```javascript
// Before
@name         OGLight

// After
@name         OGLight Ninja (CellMaster's Patcher)
```

#### Patch 2: Universal @match Pattern
```javascript
// Before
// @match        https://*.ogame.gameforge.com/game/*

// After
// @match        *://*/bots/*/browser/html/*?page=*
```

#### Patch 3: Remove Auto-Update
```javascript
// Removed (prevents overwriting patched version)
// @downloadURL https://update.greasyfork.org/scripts/514909/OGLight.user.js
// @updateURL https://update.greasyfork.org/scripts/514909/OGLight.meta.js
```

#### Patch 4: Environment Variables Injection (with Error Handling)
```javascript
// Injected after ==/UserScript==
const urlMatch = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href);
if(!urlMatch) {
    console.error('[OGLight Ninja] Invalid URL - expected format: browser/html/sXXX-xx');
    throw new Error('Invalid OGame Ninja URL format');
}
const universeNum = urlMatch[1];
const lang = urlMatch[2];
const UNIVERSE = "s" + universeNum + "-" + lang;
const PROTOCOL = window.location.protocol;
const HOST = window.location.host;
const PLAYER_ID = document.querySelector("meta[name=ogame-player-id]").content;
const localStoragePrefix = UNIVERSE + "-" + PLAYER_ID + "-";
```

#### Patch 5: Team Key Storage (Per Universe)
```javascript
// Before (global - same key for all universes)
localStorage.getItem('ogl-ptreTK')
localStorage.setItem('ogl-ptreTK', ...)

// After (per universe - shared by all accounts in same universe)
localStorage.getItem(UNIVERSE+'-ogl-ptreTK')
localStorage.setItem(UNIVERSE+'-ogl-ptreTK', ...)
```

#### Patches 6-7: Data Source Migration
```javascript
// Server ID: URL Parsing → Meta Tag
// Before
this.server.id = window.location.host.replace(/\D/g,'');

// After
this.server.id = document.querySelector('head meta[name="ogame-universe"]').getAttribute('content').replace(/\D/g,'');

// Language: Cookie → Variable
// Before
this.account.lang = /oglocale=([a-z]+);/.exec(document.cookie)[1];

// After
this.account.lang = lang;
```

#### Patch 8: UUID Polyfill (All Occurrences)
```javascript
// Before (not supported in older browsers)
let uuid = [crypto.randomUUID(), 0];
item.uid = crypto.randomUUID();

// After (manual UUID v4 generation)
let uuid = ['xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
}), 0];
item.uid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
});
```

#### Patches 9-14: URL Corrections
```javascript
// Dynamic API endpoints
url: `${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/playerData.xml?id=${player.uid}`
url: `${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/serverData.xml`
url: `${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/players.xml`

// Dynamic game URLs using pathname
href: `${PROTOCOL}//${HOST}${window.location.pathname}?page=...`

// All game URLs converted to Ninja format
'https://${window.location.host}/game/index.php' → '${PROTOCOL}//${HOST}${window.location.pathname}'
```

#### Patch 15: Adapt Multi-Session Logic
**THE MOST CRITICAL FIX - Adapts (not removes) security logic**

```javascript
// BEFORE (Original OGLight - using cookies)
// get the account ID in cookies
let cookieAccounts = document.cookie.match(/prsess\_([0-9]+)=/g);

// purge cookies to prevent session conflict
if(cookieAccounts?.length > 1) {
    // ... cookie purge logic
}

// force relogin
if(!cookieAccounts) {  // Always TRUE on OGame Ninja → Forces logout!
    alert('You have been signed out...');
    window.location.href = "index.php?page=logout";
    return;
}

const accountID = cookieAccounts[cookieAccounts.length-1].replace(/\D/g, '');

// AFTER (Adapted for OGame Ninja - KEEPS validation logic!)
// get the account ID from meta tag (OGame Ninja adaptation)
const accountMeta = document.querySelector('head meta[name="ogame-player-id"]');

// validate session exists (adapted for OGame Ninja)
if(!accountMeta || !accountMeta.content) {
    console.error('[OGLight Ninja] No player ID found in meta tag');
    alert('Session error: Unable to retrieve player ID. Please refresh the page.');
    return;
}

const accountID = accountMeta.getAttribute('content').replace(/\D/g, '');

// additional validation
if(!accountID || accountID === '0') {
    console.error('[OGLight Ninja] Invalid player ID:', accountID);
    alert('Session error: Invalid player ID detected. Please refresh the page.');
    return;
}
```

#### Patch 16: DBName Isolation
```javascript
// Before (uses hostname which doesn't exist in Ninja)
this.DBName = `${accountID}-${window.location.host.split('.')[0]}`;

// After (uses UNIVERSE variable)
this.DBName = `${accountID}-${UNIVERSE}`;
```

#### Patch 17: French Keyboard Detection
```javascript
// Before (parses hostname)
galaxyUp: window.location.host.split(/[-.]/)[1] == 'fr' ? 'z' : 'w',
galaxyLeft: window.location.host.split(/[-.]/)[1] == 'fr' ? 'q' : 'a',

// After (uses lang variable)
galaxyUp: lang == 'fr' ? 'z' : 'w',
galaxyLeft: lang == 'fr' ? 'q' : 'a',
```

#### Patch 18: Legacy DB Migration
```javascript
// Before (uses window.location.host)
if(!GM_getValue(this.DBName) && GM_getValue(window.location.host)) {
    GM_setValue(this.DBName, GM_getValue(window.location.host));
    GM_deleteValue(window.location.host);
    window.location.reload();
}

// After (uses meta tag)
const oldHost = document.querySelector('meta[name="ogame-universe"]').getAttribute('content');
if(!GM_getValue(this.DBName) && GM_getValue(oldHost)) {
    GM_setValue(this.DBName, GM_getValue(oldHost));
    GM_deleteValue(oldHost);
    window.location.reload();
}
```

#### Patch 19: Full localStorage Isolation
```javascript
// Before (global keys - conflicts in multi-account)
localStorage.getItem('ogl-redirect')
localStorage.getItem('ogl_minipics')
localStorage.getItem('ogl_menulayout')
localStorage.getItem('ogl_colorblind')
localStorage.getItem('ogl_sidepanelleft')

// After (prefixed with UNIVERSE)
localStorage.getItem(UNIVERSE+'-ogl-redirect')
localStorage.getItem(UNIVERSE+'-ogl_minipics')
localStorage.getItem(UNIVERSE+'-ogl_menulayout')
localStorage.getItem(UNIVERSE+'-ogl_colorblind')
localStorage.getItem(UNIVERSE+'-ogl_sidepanelleft')
```

---

## Installation & Usage

### Requirements
```bash
pip install requests
```

### Running the Patcher
```bash
python patcher.py
```

### Output
```
============================================================
OGLight Patcher - OGame Ninja Edition v2.8
Supported OGLight version: 5.3.3 (19 patches)
============================================================

[*] Downloading file from: https://update.greasyfork.org/scripts/514909/OGLight.user.js
[+] Download completed!
[*] Expected SHA256: 371795e1a20f04040c00fc9568b92fe536960aa115a49d406f3ae60a6405b432
[*] Current SHA256:  371795e1a20f04040c00fc9568b92fe536960aa115a49d406f3ae60a6405b432
[+] SHA256 validated successfully!

[*] Applying patches...
  [+] Patch 1/19: Script name changed
  [+] Patch 2/19: @match simplified to universal pattern
  [+] Patch 3/19: Auto-update URLs removed
  [+] Patch 4/19: Environment variables injected (with error handling)
  [+] Patch 5/19: Team Key prefixed with UNIVERSE (2 get + 1 set)
  [+] Patch 6/19: Server ID via meta tag
  [+] Patch 7/19: Lang via variable
  [+] Patch 8/19: crypto.randomUUID() replaced (1 array + 2 item.uid)
  [+] Patch 9/19: playerData.xml URL fixed
  [+] Patch 10/19: serverData.xml URL fixed
  [+] Patch 11/19: players.xml URL fixed
  [+] Patch 12/19: Player link fixed
  [+] Patch 13/19: Message URL fixed
  [+] Patch 14/19: Game URLs converted to Ninja format (28 occurrences)
  [+] Patch 15/19: Multi-session logic ADAPTED for OGame Ninja (keeps validation)
  [+] Patch 16/19: DBName uses UNIVERSE variable
  [+] Patch 17/19: French keyboard detection fixed
  [+] Patch 18/19: Legacy DB migration fixed for Ninja
    - ogl-redirect: 1 get + 4 set
    - ogl_minipics: 1 get + 1 set
    - ogl_menulayout: 1 get + 2 set
    - ogl_colorblind: 1 get + 1 set
    - ogl_sidepanelleft: 1 get + 1 set
  [+] Patch 19/19: Remaining localStorage keys prefixed (14 occurrences)
[+] All 19 patches applied successfully!

[*] Saving file: OGLight_Ninja.user.js
[+] File saved successfully!

============================================================
Process completed successfully!
Generated file: OGLight_Ninja.user.js
============================================================
```

### Installing the Generated Script
1. Open OGame Ninja browser
2. Install Tampermonkey extension
3. Click "Create new script"
4. Paste contents of `OGLight_Ninja.user.js`
5. Save and refresh OGame Ninja page

---

## Technical Comparison

### Go Version Workflow
```
Download (framework) → Validate (framework) → Process (custom) → Save (framework)
                                                     ↓
                                              processOGLight()
                                                     ↓
                                         13 replN() function calls
```

### Python Version Workflow
```
Download (requests) → Validate (hashlib) → Process (custom) → Save (file I/O)
                                                  ↓
                                           apply_patches()
                                                  ↓
                                    19 str.replace() operations
                                    (includes multi-account patches)
```

### Code Metrics

| Metric | Go Version | Python Version |
|--------|-----------|----------------|
| **Total Lines** | ~60 (+ framework) | ~400 (standalone) |
| **Dependencies** | 1 external package | 1 standard library |
| **Patches Applied** | 13 | 19 |
| **Error Handling** | Panic on failure | Try/except blocks |
| **Logging** | Framework-managed | Custom print statements |
| **Testability** | Requires Go build | Direct Python execution |

---

## Version History

### v2.8 (Current - Python)
- Updated for OGLight 5.3.3
- SHA256 updated for new version
- Removed unnecessary replace() limits for future-proofing
- All patches verified compatible with 5.3.3 changes

### v2.7
- Full localStorage isolation for multi-account support
- Patch 12 & 13: Now use PROTOCOL/HOST variables (consistency fix)
- Patch 19: Added - Prefixes remaining localStorage keys with UNIVERSE

### v2.6
- Code optimization and bug fixes
- Patch 4: Error handling included directly
- Patch 8: Now converts ALL crypto.randomUUID() calls
- Patch 14: URLs now CONVERTED instead of REMOVED

### v2.5
- Team Key storage optimization
- Team Key now stored per UNIVERSE (shared by all accounts in same universe)

### v2.4
- DB Migration fix added for OGame Ninja

### v2.3
- French keyboard (AZERTY) detection fixed

### v2.2
- DBName uses UNIVERSE variable for proper isolation

### v2.1
- Regex error handling added (prevents crashes on invalid URLs)

### v2.0
- Multi-session logic adapted for OGame Ninja

### v1.0 (Python)
- Initial Python port with 14 patches
- Standalone implementation (no framework)
- Added multi-session adaptation (Patch 15)

### Original Go Patcher
- 13 patches for OGLight compatibility
- Framework-based implementation (`extension-patcher`)
- OGLight 5.x support
- Required Go compilation

---

## Why These Patches Matter

### The Logout Bug (Patch 15)
**Symptom**: Users randomly logged out of OGame Ninja

**Root Cause**:
1. OGLight validates session using `prsess_` cookies (Gameforge method)
2. OGame Ninja doesn't use `prsess_` cookies (uses meta tags)
3. Cookie check returns `null` on OGame Ninja
4. Null check triggers → forced logout to "index.php?page=logout"

**Impact**: Made OGLight unusable on OGame Ninja - immediate logout on load

**Fix**: ADAPT session validation logic:
- Keep validation philosophy (check for valid session)
- Change method (meta tags instead of cookies)
- Maintain security checks (validate player ID exists and is valid)
- Preserve user feedback (error messages)
- Don't force logout on OGame Ninja (no redirect)

### Multi-Account Conflicts (Patches 5, 16, 19)
**Symptom**: Settings from one account overwrite another

**Root Cause**:
1. localStorage keys were global (same key for all accounts)
2. Team Key was stored globally (needed to configure for each account)
3. DBName used hostname (doesn't exist in Ninja)

**Impact**: Multi-account users had constant configuration conflicts

**Fix**: Proper isolation:
- Team Key per universe (shared by accounts in same universe)
- localStorage keys prefixed with UNIVERSE+PLAYER_ID
- DBName uses UNIVERSE variable

---

## OGame Ninja vs Official Architecture

| Item | OGame Official | OGame Ninja |
|------|--------------|-------------|
| **URL** | `s123-pt.ogame.gameforge.com/game/index.php` | `127.0.0.1/bots/bot1/browser/html/s123-pt` |
| **API** | `/api/playerData.xml` | `/api/s123/pt/playerData.xml?id=...` |
| **Player ID** | Cookie `prsess_123456` | Meta tag `ogame-player-id` |
| **Server ID** | Hostname `s123-pt` | Meta tag `ogame-universe` |
| **Language** | Cookie `oglocale=pt` | Extracted from URL `/s123-pt` |

---

## Contributing

This is a functional port of the original Go patcher. If OGLight updates require new patches:

1. Update `EXPECTED_SHA256` to new file hash
2. Add new replacement logic to `apply_patches()`
3. Increment patch counter in print statements
4. Test thoroughly before committing

---

## License

This is a derivative work based on the [OGame Ninja extension-patcher](https://github.com/ogame-ninja/extension-patcher). Original Go code by OGame Ninja team.

---

## Credits

- **Original Patcher**: [ogame-ninja/extension-patcher](https://github.com/ogame-ninja/extension-patcher)
- **OGLight Extension**: [TheCellMaster/OGLight](https://github.com/TheCellMaster/OGLight)
- **OGame Ninja**: [ogame-ninja](https://github.com/ogame-ninja)
- **Python Port**: CellMaster

---

## Links

- [OGame Ninja](https://github.com/ogame-ninja)
- [OGLight Extension](https://greasyfork.org/scripts/514909-oglight)
- [Original Go Patcher](https://github.com/ogame-ninja/extension-patcher)
