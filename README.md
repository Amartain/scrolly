# Scrolly - A Productivity Hub

Welcome to Scrolly! 

Are you exhausted by traditional "productivity" apps that feel like a demanding boss? Are you tired of corporate jargon, endless dropdown menus, and apps that make you feel guilty for leaving things undone? 

Me too. That’s exactly why I built Scrolly. 

Scrolly isn't just a to-do list; it's a completely different mindset. It is a localized, gamified task manager heavily inspired by Wuxia/Xianxia aesthetics (think martial arts cultivation, scrolls, and inner peace). It is specifically engineered around psychology to protect your energy, bypass overwhelm, and actually make getting things done feel rewarding.

## The Psychology behind Scrolly

A lot of standard productivity features actually hurt our ability to get things done. Scrolly flips the script:

*   **Frictionless Brain Dumping:** Standard apps force you to click "Add Task," type a name, open a calendar, set a priority, and estimate time... for every single item. That click-fatigue destroys motivation. In Scrolly, you start with a blank text box. Just dump everything from your brain onto the screen at once. Organize it later. 
*   **The Power of Choice (No Auto-Adding):** Why doesn't Scrolly auto-fill your daily habits every morning? Because psychology shows that auto-generated lists feel like demands, and our brains naturally rebel against demands. In Scrolly, you have to actively choose to summon your daily habits (Foundational Arts) to your scroll. Making the conscious choice makes you much more committed to actually doing it!
*   **A New Vocabulary:** We are ditching the exhausting "hustle culture" language. You aren't doing "tasks"; you are conquering **Trials**. You aren't logging "hours"; you are expending **Essence**. Reframing the language reframes the experience.
*   **Positive Tracking Only:** There are no red overdue dates yelling at you. Scrolly’s analytics only track your victories. It’s all about dopamine and upward momentum. 
*   **Time Estimation as a Practice, Not a Pressure:** Estimating how long things take is a muscle you have to build. Scrolly includes a live focus timer to help you see the reality of your time blindness—but it's entirely **optional**. The total expected time isn't designed to stress you out; it's there to help you learn your own rhythm.

## How It Works

Scrolly separates your day into distinct, manageable phases so you never get overwhelmed.

1.  **Phase 1: Inscribe the Scroll (The Brain Dump)**
    Empty your mind into a single text box. No dates, no times, no priorities. Just get it out of your head. You can also peek at **The Horizon** (your future ideas) or your **Foundational Arts** (habits) and selectively summon them into today's journey.
2.  **Phase 2: Estimate the Journey**
    Now that everything is out of your head, you can quickly type in rough time estimates (e.g., `30m` or `1h`) and easily drag-and-drop your trials into the order you want to tackle them.
3.  **Phase 3: The Active Peak (Execution)**
    The main dashboard hides all the noise. It brings your **Conquered** trials to the top so you always see your wins, highlights a single **Immediate Trial** for you to focus on, and tucks the rest of your day neatly away. 
4.  **The Grand Archives**
    Every night at 4:00 AM, the system wipes the slate clean. Conquered tasks are permanently etched into your beautiful, scrollable Grand Archives, while untouched tasks fade away like fallen leaves. Every day is a fresh start!

## Visual Tour

`[Screenshot 1: The serene landing page showing the fogged UI and the 'Cultivate Your Focus' button]`
*The initial state demands nothing from you but a single click to begin.*

`[Screenshot 2: The Phase 1 Brain Dump interface, showing the text area and the Horizon/Foundational Arts menus on the side]`
*Frictionless entry: Dump your thoughts, or summon your chosen habits from the left.*

`[Screenshot 3: The Phase 2 Estimation interface showing the drag-and-drop handles and time inputs]`
*Organize the chaos: Quickly drag your trials into order and guess how much essence they will take.*

`[Screenshot 4: The main execution dashboard showing an active timer, the conquered list, and the analytics graphs]`
*The Active Scroll: Focus entirely on your immediate trial while watching your streak and graphs climb.*

`[Screenshot 5: The Grand Archives showing past days and completed tasks]`
*Your legacy: A stress-free record of all your past triumphs.*

## Installation & Setup (Alpha Version)

*Note: One-click downloadable executables for Windows (`.exe`) and Mac (`.app`) are currently in the works for non-technical users! For now, here is how to run the Alpha via Python.*

**Prerequisites:** You will need [Python 3.8+](https://www.python.org/downloads/) installed on your computer.

1. **Download the App:** Click the green "Code" button at the top of this repository and select "Download ZIP", then extract it to a folder on your computer.
2. **Open your Terminal (or Command Prompt):** Navigate to the folder where you extracted Scrolly.
3. **Install the single requirement:**
   ```bash
   pip install Flask
4. Run Scrolly:
```Bash
python app.py
```
5. Open your browser:
Go to http://localhost:5000 and start cultivating your focus! All your data is saved 100% locally and privately in a data folder right next to your app.

## What's Next? (Future Features)

Scrolly is an active, continuously developing pet project! I am building this because I genuinely use it every single day. Here is a sneak peek at what is currently brewing in the development forge:

    - Focus Timer Mode: A dedicated, distraction-free view for your current trial.

    - Visual Time Tracking: A visual timer comparing your expected time vs. your actual spent time to help master time blindness.

    - Pomodoro Integration: An optional Pomodoro cycle mode for those who need structured breaks!

    - One-Click Installers: Making it effortless for anyone to download and run without touching a terminal.
