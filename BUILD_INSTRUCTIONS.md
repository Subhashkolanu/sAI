# Building the sAI Windows Installer

This document outlines the step-by-step instructions to compile and package the official **sAI Windows Installer** (`sAI-Setup-v1.0.0.exe`) for Windows 10 and Windows 11 (64-bit).

---

## 1. Prerequisites

### Tools Required
- **Python 3.11+ 64-bit** (e.g. Python 3.14 64-bit)
- **PyInstaller 6.x** (`pip install pyinstaller`)
- **Inno Setup 6.x** (Install via `winget install --id JRSoftware.InnoSetup -e`)
- **Git for Windows**
- **PowerShell 5.1+**

### Environment Setup
Open PowerShell and navigate to the repository:

```powershell
cd D:\EXTRAS\Projects\sAI
$env:PYTHONPATH="D:\EXTRAS\Projects\sAI;D:\EXTRAS\Projects\sAI\venv\Lib\site-packages"
```

---

## 2. Generate Application Icon

The installer and executable use the multi-resolution icon generated from `Logo.png`:

```powershell
python -c "
from PIL import Image
from pathlib import Path
img = Image.open('Logo.png')
img.save('assets/icon.ico', format='ICO', sizes=[(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)])
"
```

---

## 3. Step 1: PyInstaller Standalone Bundle (`--onedir`)

Build the standalone application directory using `sAI.spec`:

```powershell
python -m PyInstaller --clean --noconfirm sAI.spec
```

- **Output:** `dist\sAI\`
- **Contents:** `sAI.exe`, embedded Python runtime, core dependencies, CustomTkinter theme/font assets, and application modules.
- **Excluded:** User data, `.env`, local models, Ollama binary, and heavy unneeded scientific libraries.

---

## 4. Step 2: Inno Setup Installer (`.exe`)

Compile the installer script using `ISCC.exe`:

```powershell
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" installer.iss
```

*(Or `& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss` if installed system-wide).*

- **Output:** `dist_installer\sAI-Setup-v1.0.0.exe`
- **Installation Directory:** `%LOCALAPPDATA%\Programs\sAI`
- **Privileges:** `PrivilegesRequired=lowest` (No administrator elevation required)
- **User Data Storage:** `%LOCALAPPDATA%\sAI\data` (Persisted during upgrade and uninstallation)

---

## 5. Verification Checklist

Run all automated quality and regression tests:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q backend frontend tests run.py main.py
python -m pip check
git diff --check
```
