**📜 Scrolly is out, and this time you don't need Python**

I've poured my soul into this build. I tried to write something eloquent about it, got as far as "life and... love", cringed, and handed the pen to an AI. So here we are.

**What it is:** a free, open-source task manager for brains that don't get along with normal to-do apps. It runs offline on your own computer: no account, no cloud, nothing leaves your machine. The old prototype needed Python and a terminal; this is a full rebuild you just double-click.

**What it's like:**
🌅 You plan the day like a ritual: brain-dump, estimate, seal the scroll.
💧 One task at a time. The rest waits quietly.
⛰️ Start a timer and a tiny cultivator climbs the mountain to meditate while you work.
🧘 Seclusion: a focus room with an incense timer, pomodoro-style cycles, or a flow mode that saves up rest as you work.
🪷 Important tasks are never lost. Ordinary ones just drift away at 4 AM. No guilt.
⚡ An optional energy tracker for those of us who overcommit and crash.
📋 Your day as Discord markdown, ready to post right here.

**What it won't do:** no streaks, no "overdue", no red badges, no numbers going down. You can't fail at it. You can only rest.

**And...** there are secrets. Some you find by doing, some you type. One waits on day 100. More are coming. 🤫

**Download (Windows & Mac):** <LINK>
It's unsigned (signing costs money, Scrolly is free), so the first launch shows a warning:
• Windows: "Windows protected your PC" → *More info* → *Run anyway*
• Mac: *System Settings → Privacy & Security* → *Open Anyway*

Tell me what you love, what broke, and what you wish it did: use the feedback links in Settings, or just reply here. I'll build what people ask for most (picture-in-picture timers are already on the list 👀).

Check out and :star: the project it would help this little unemployed fresh graduate a lot :sparkles:

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
