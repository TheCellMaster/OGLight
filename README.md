# OGLight Patcher for OGame Ninja

**Python adaptation of the original Go patcher** - Converts [OGLight](https://github.com/TheCellMaster/OGLight) userscript to work with [OGame Ninja](https://github.com/ogame-ninja)

## Overview

This project is a **Python port** of the [original Go-based patcher](https://github.com/ogame-ninja/extension-patcher) used to adapt browser extensions for OGame Ninja. The patcher automatically downloads the latest OGLight userscript and applies 14 patches to make it compatible with OGame Ninja's architecture.

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

### This Patcher (Python v2.1)
```python
#!/usr/bin/env python3
"""
OGLight Patcher - Adapta o OGLight para OGame Ninja
Versao: 2.1 - Atualizado para OGLight 5.3.2 + BUGFIXES
"""

# Self-contained, standalone implementation
# Downloads, validates SHA256, applies 14 patches, generates output
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

1. **Bugfix #1 - Session Validation Adapted** (Patch 13)
   - **Original Issue**: OGLight validates sessions using `prsess_` cookies (Gameforge method)
   - **Problem**: OGame Ninja doesn't use those cookies → forced logout
   - **Solution**: ADAPTED (not removed) validation logic to use meta tags while keeping security checks

2. **Bugfix #2 - URL Validation** (Patch 14)
   - **Original Issue**: Regex extraction could crash on invalid URLs
   - **Problem**: `null[1]` access caused JavaScript error
   - **Solution**: Added pre-validation before accessing regex groups

3. **Enhanced Logging**
   - Go version: Silent operation via framework
   - Python version: Detailed progress output for each patch

4. **SHA256 Flexibility**
   - Go version: Hardcoded old OGLight hash
   - Python version: Updated to OGLight 5.3.2 hash

---

## The 14 Patches

All patches from the original Go code were preserved and improved:

| # | Patch | Go Implementation | Python Implementation |
|---|-------|-------------------|----------------------|
| 1 | Script Name | `replN()` call | `str.replace()` with count=1 |
| 2 | @match URLs | Template replacement | Multi-line string injection |
| 3 | Environment Vars | Heredoc injection | Raw string with tab preservation |
| 4 | localStorage Prefix | 3x `replN()` | 3x `replace()` (2 getItem, 1 setItem) |
| 5 | Server ID Source | `window.location.host` → meta tag | `window.location.host` → meta tag |
| 6 | Language Source | Cookie → variable | Cookie → variable |
| 7 | UUID Generation | `crypto.randomUUID()` → polyfill | `crypto.randomUUID()` → polyfill |
| 8 | playerData.xml URL | Hardcoded → dynamic | Hardcoded → dynamic with `?id=` param |
| 9 | serverData.xml URL | Hardcoded → dynamic | Hardcoded → dynamic |
| 10 | Player Link URL | Hardcoded → `pathname` | Hardcoded → `pathname` |
| 11 | Message URL | Hardcoded → `pathname` | Hardcoded → `pathname` |
| 12 | Generic URLs | 25 replacements | 30 replacements |
| 13 | **BUGFIX** Session Validation | Not in original | **NEW** - Adapts session logic (keeps validation) |
| 14 | **BUGFIX** URL Validation | Not in original | **NEW** - Prevents crashes |

### Patch Details

#### Patch 1: Script Rename
```javascript
// Before
@name         OGLight

// After
@name         OGLight Ninja
```

#### Patch 2: Add OGame Ninja URLs
```javascript
// Added
// @match        *127.0.0.1*/bots/*/browser/html/*?page=*
// @match        *.ogame.ninja/bots/*/browser/html/*?page=*
```

#### Patch 3: Environment Variables Injection
```javascript
// Injected after ==/UserScript==
const universeNum = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href)[1];
const lang = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href)[2];
const UNIVERSE = "s" + universeNum + "-" + lang;
const PROTOCOL = window.location.protocol;
const HOST = window.location.host;
const PLAYER_ID = document.querySelector("meta[name=ogame-player-id]").content;
const localStoragePrefix = UNIVERSE + "-" + PLAYER_ID + "-";
```

#### Patch 4: localStorage Isolation
```javascript
// Before
localStorage.getItem('ogl-ptreTK')
localStorage.setItem('ogl-ptreTK', ...)

// After
localStorage.getItem(localStoragePrefix+'ogl-ptreTK')
localStorage.setItem(localStoragePrefix+'ogl-ptreTK', ...)
```

#### Patches 5-6: Data Source Migration
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

#### Patch 7: UUID Polyfill
```javascript
// Before (not supported in older browsers)
let uuid = [crypto.randomUUID(), 0];

// After (manual UUID v4 generation)
let uuid = ['xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
}), 0];
```

#### Patches 8-12: URL Corrections
```javascript
// Dynamic API endpoints
url: `${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/playerData.xml?id=${player.uid}`
url: `${PROTOCOL}//${HOST}/api/s${universeNum}/${lang}/serverData.xml`

// Dynamic game URLs using pathname
href: `${window.location.protocol}//${window.location.host}${window.location.pathname}?page=...`

// Remove hardcoded domain (30 occurrences)
'https://${window.location.host}/game/index.php' → ''
```

#### Patch 13: BUGFIX - Adapt Session Validation Logic
**THE MOST CRITICAL FIX - Adapts (not removes) security logic**

```javascript
// BEFORE (Original OGLight - 30 lines using cookies)
// get the account ID in cookies
let cookieAccounts = document.cookie.match(/prsess\_([0-9]+)=/g);

// purge cookies to prevent session conflict
if(cookieAccounts?.length > 1) {
    const allCookies = document.cookie.split(';');
    for(let i = 0; i < allCookies.length; i++) {
        let cookie = allCookies[i].trim();
        const cookieName = cookie.split('=')[0];
        if(cookieName.startsWith('prsess_')) {
            document.cookie = cookieName + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
        }
    }
    cookieAccounts = document.cookie.match(/prsess\_([0-9]+)=/g);
}

// force relogin
if(!cookieAccounts) {  // ❌ Always TRUE on OGame Ninja → Forces logout!
    alert('You have been signed out due to a session conflict. Please log in again to continue.');
    window.location.href = "index.php?page=logout";
    return;
}

const accountID = cookieAccounts[cookieAccounts.length-1].replace(/\D/g, '');

// AFTER (Adapted for OGame Ninja - KEEPS validation logic!)
// get the account ID from meta tag (OGame Ninja adaptation)
const accountMeta = document.querySelector('head meta[name="ogame-player-id"]');

// validate session exists (adapted for OGame Ninja)
if(!accountMeta || !accountMeta.content) {
    console.error('[OGLight Ninja] No player ID found in meta tag - session may be invalid');
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

**Why adaptation (not removal) is correct:**
1. **Original intent preserved**: Still validates session before proceeding
2. **Method adapted**: Uses meta tags instead of `prsess_` cookies
3. **Security maintained**: Checks for missing/invalid player ID
4. **User feedback**: Shows appropriate error messages
5. **No forced logout**: Doesn't redirect to logout on OGame Ninja
6. **Philosophy**: Patcher adapts code, doesn't remove functionality

#### Patch 14: BUGFIX - URL Validation
```javascript
// BEFORE (CRASH RISK)
const universeNum = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href)[1];  // ❌ null[1] = crash!
const lang = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href)[2];

// AFTER (SAFE)
const urlMatch = /browser\/html\/s(\d+)-(\w+)/.exec(window.location.href);
if(!urlMatch) {
    console.error('[OGLight Ninja] URL invalida - esperado formato: browser/html/sXXX-xx');
    throw new Error('Invalid OGame Ninja URL format');
}
const universeNum = urlMatch[1];
const lang = urlMatch[2];
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
OGLight Patcher - OGame Ninja Edition v2.1
Supported OGLight version: 5.3.2 + BUGFIXES
============================================================

[*] Downloading file from: https://raw.githubusercontent.com/TheCellMaster/OGLight/main/OGLight.user.js
[+] Download completed!
[*] Expected SHA256: 75f877eb9d6435e9c9466b1bc9dfc0e768f1a5e37ae311b1770c999b317e748c
[*] Current SHA256:  75f877eb9d6435e9c9466b1bc9dfc0e768f1a5e37ae311b1770c999b317e748c
[+] SHA256 validated successfully!

[*] Applying patches...
  [+] Patch 1/14: Script name changed
  [+] Patch 2/14: @match URLs added
  [+] Patch 3/14: Environment variables injected
  [+] Patch 4/14: localStorage prefixed (3 occurrences)
  [+] Patch 5/14: Server ID via meta tag
  [+] Patch 6/14: Lang via variable
  [+] Patch 7/14: crypto.randomUUID() replaced
  [+] Patch 8/14: playerData.xml URL fixed
  [+] Patch 9/14: serverData.xml URL fixed
  [+] Patch 10/14: Player link fixed
  [+] Patch 11/14: Message URL fixed
  [+] Patch 12/14: Generic URLs removed (28 occurrences)
  [+] Patch 13/14: Multi-session logic ADAPTED for OGame Ninja (keeps validation)
  [+] Patch 14/14: Regex error handling (BUGFIX - prevents crash on invalid URLs)
[+] All 14 patches applied successfully!

[*] Saving file: OGLight_Ninja.user.js
[+] File saved successfully!

============================================================
Process completed successfully!
Generated file: OGLight_Ninja.user.js
Install the file in OGame Ninja browser/Tampermonkey
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
                                    14 str.replace() operations
                                    (includes 2 bugfix patches)
```

### Code Metrics

| Metric | Go Version | Python Version |
|--------|-----------|----------------|
| **Total Lines** | ~60 (+ framework) | 260 (standalone) |
| **Dependencies** | 1 external package | 1 standard library |
| **Patches Applied** | 13 | 14 (12 original + 2 bugfixes) |
| **Error Handling** | Panic on failure | Try/except blocks |
| **Logging** | Framework-managed | Custom print statements |
| **Testability** | Requires Go build | Direct Python execution |

---

## Version History

### v2.1 (Current - Python)
- 12 original Go patches adapted and improved
- **NEW**: Patch 13 - ADAPTS session validation logic for OGame Ninja (fixes logout bug while keeping security)
- **NEW**: Patch 14 - Adds URL validation (prevents crashes)
- Updated SHA256 for OGLight 5.3.2
- Enhanced logging and error messages
- Standalone Python implementation
- **Philosophy**: Adapts code (doesn't remove functionality)

### v1.0 (Original - Go)
- 13 patches for OGLight compatibility
- Framework-based implementation
- OGLight 5.x support
- Required Go compilation

---

## Why These Bugfixes Matter

### The Logout Bug (Patch 13)
**Symptom**: Users randomly logged out of OGame Ninja

**Root Cause**:
1. OGLight validates session using `prsess_` cookies (Gameforge method)
2. OGame Ninja doesn't use `prsess_` cookies (uses meta tags)
3. Cookie check returns `null` on OGame Ninja
4. Null check triggers → forced logout to "index.php?page=logout"

**Impact**: Made OGLight unusable on OGame Ninja - immediate logout on load

**Fix**: ADAPT session validation logic:
- ✅ Keep validation philosophy (check for valid session)
- ✅ Change method (meta tags instead of cookies)
- ✅ Maintain security checks (validate player ID exists and is valid)
- ✅ Preserve user feedback (error messages)
- ❌ Don't force logout on OGame Ninja (no redirect)

### The Crash Bug (Patch 14)
**Symptom**: Script crashes silently on certain URLs

**Root Cause**:
1. Regex `.exec()` returns `null` if no match
2. Code immediately accesses `[1]` without checking
3. `null[1]` → JavaScript TypeError
4. Script stops execution completely

**Impact**: OGLight fails to load on non-standard URLs

**Fix**: Store regex result, validate, then access groups

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
- **Python Port**: This repository

---

## Links

- [OGame Ninja](https://github.com/ogame-ninja)
- [OGLight Extension](https://github.com/TheCellMaster/OGLight)
- [Original Go Patcher](https://github.com/ogame-ninja/extension-patcher)
