# 📜Scrolly

A free, offline, neurodivergent-friendly task manager, themed as a cultivation sanctuary. 🏔️ You plan each day as a scroll, work one trial at a time, and a small cultivator climbs the mountain to meditate while your timer runs. 🧘

It runs on your own computer and opens in your browser. No account, no cloud: nothing leaves your machine. 🔒

## ✨ What it's like

- **🖋️ Plan the day as a ritual.** Write down everything on your mind, estimate how long each trial takes, mark the ones that truly matter as Heavenly Mandates, then seal the scroll.
- **🎯 One thing at a time.** The Immediate Trial sits in front of you; the rest waits quietly below.
- **🌙 Nothing punishes you.** No streaks, no "overdue", no red badges, no numbers that go down. Ordinary trials you didn't reach simply fade away at 4 AM. Heavenly Mandates are never lost; they return to the Horizon.
- **🧘 Seclusion, a focus room.** Three ways to focus: a single incense stick, Harmonious Cycles (pomodoro-style), or River Flow, which banks rest while you work. Closing the tab or sleeping the laptop loses no time. ⏳
- **📒 The Golden Core (optional).** A hand-estimated energy ledger for people who burn out by overcommitting. It reminds you that rest comes first. 🍂
- **📈 Momentum, not analytics.** Charts that only ever rise, and the Grand Archives of every past day. 🎋
- **🏮 Ceremonies.** Finishing a day plays a small scene. Sunset brings dusk, a poem and an optional chime. 🌅
- **💬 Discord Dispatch.** Your day as Discord markdown, ready to paste.
- **🎓 Learn by playing.** A short tour, "Knowledge of the Dao", teaches the app as you use it. 🧭
- **🤫 Secrets.** There are a few. You'll know them when you find them.

Two themes, Serene Peak and Hidden Pavilion, each with day and dusk palettes. Keyboard shortcuts for everything, reduced-motion support, and an OpenDyslexic reading font. 🎨

## 🚀 Download and run

No Python or anything else to install. Head to the latest [release](https://github.com/Amartain/scrolly/releases/latest) and download the zip for your computer. 📦

### 🪟 Windows (10 or 11)

1. Download `Scrolly-<version>-windows.zip`.
2. Right-click it → **Extract All…**, and put the `Scrolly` folder somewhere it can stay (Documents is fine). 📁
3. Open the folder and double-click **`Scrolly.exe`**. Tip: right-click it → **Send to → Desktop (create shortcut)** for next time. 🖱️
4. The first time, Windows may say **"Windows protected your PC"**: click **More info**, then **Run anyway**.

### 🍏 Mac (Apple Silicon: M1 or newer)

1. Download `Scrolly-<version>-macos-arm64.zip` and double-click it to unzip.
2. Drag **`Scrolly.app`** into your **Applications** folder.
3. Open it. The first time, macOS says it cannot check the app: click **Done**, then open **System Settings → Privacy & Security**, scroll down to the line about Scrolly and click **Open Anyway**.
4. If macOS still refuses, open **Terminal** and paste this line, then open Scrolly again:
   `xattr -dr com.apple.quarantine /Applications/Scrolly.app`

Older Intel Macs are not supported by the download yet; they can run Scrolly from source (see Develop below). 🧩

The warnings appear because the app is not code-signed (signing costs money; Scrolly is free). The source is all here to read. 🔍

### 🏯 Using it

Scrolly opens in your browser, and a small **Scrolly** window appears beside it. That window is the app:

- **Open Scrolly** brings the page back if you closed the tab.
- **Quit** (or closing the window) stops Scrolly. Your day is saved as you go; nothing is lost.
- Opening Scrolly while it already runs simply opens the page again.

### 🔄 Updating

Download the new zip and replace the old `Scrolly` folder (Windows) or `Scrolly.app` (Mac). Your data stays where it is (see below).

### 🗄️ Your data

Everything is stored in one file in `~/.scrolly/` (on Windows, `C:\Users\<you>\.scrolly\`). Updating Scrolly keeps it. **Settings → Data → Backup Scroll** saves everything as a zip of plain CSV files you can open in any spreadsheet, and **Restore Scroll** brings a backup back (it also reads the old prototype's JSON export).

## 💌 Feedback

Found a bug, or wish Scrolly did something? Use the links in **Settings → Feedback**, or open an [issue](https://github.com/Amartain/scrolly/issues). The most requested features get built first. 🛠️

## 🛠️ Develop

Needs Python 3.12+ and Node.js.

```
py -m pip install uv
uv sync
cd frontend && npm install && npx playwright install chromium && cd ..
uv run poe dev      # API + frontend with hot reload
uv run poe check    # linters, types, tests, end-to-end
```

The backend and all business rules are Python (FastAPI, SQLite); the frontend is Svelte and only displays data. 🐍

### 📦 Build the downloadable app yourself

```
uv run poe exe                          # builds dist/Scrolly-<version>-<system>.zip for this computer
uv run python scripts/smoke_exe.py      # starts the build once and checks it serves
```

PyInstaller builds only for the system it runs on: the Windows zip on Windows, the Mac zip on a Mac. The recipe is
`packaging/scrolly.spec`; the app icon is `packaging/scrolly-icon.svg` (see `scripts/build_icons.py`).

### 🏷️ Making a release

1. Set the new version in `pyproject.toml` (`version = "1.0.1"`) and `frontend/package.json`, and commit.
2. Tag it and push the tag:
   ```
   git tag v1.0.1
   git push origin main v1.0.1
   ```
3. GitHub Actions (`.github/workflows/release.yml`) builds the Windows and Mac zips, starts each once, and opens a
   **draft** release with the zips and the wheel attached. It takes about 10 minutes (the Actions tab shows it).
4. On the [Releases](https://github.com/Amartain/scrolly/releases) page, open the draft, check the notes and the
   files, and click **Publish release**.

To try the builds without a release, run the workflow by hand from the Actions tab (**release → Run workflow**);
the zips appear as artifacts on the run's page.

## ⚖️ Licence

AGPL-3.0 (see `LICENSE`). Fonts and other third-party parts are listed in `THIRD_PARTY_NOTICES.md`.
