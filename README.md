# StudyBuddy AI

#### Video Demo: [Paste your YouTube/screen demo link here]

--

## Description

**StudyBuddy: AngleAlchemy Edition** is a next-generation, web-based learning platform that transforms studying into an adventure! At its core are two interactive educational games:

- **AngleAlchemy**: A fantasy role-playing game where you explore the magical Realm of Academia, battling subject-themed monsters (like Grammar Ghouls and Math Monsters), completing quests, collecting coins and badges, and restoring lost knowledge. Each victory brings you closer to saving the Tree of Knowledge and unravelling the story of a world threatened by ignorance and a power-hungry villain.

- **Quiz Quest**: A fast-paced, grid-based RPG quiz mini-game. Move your avatar (e.g. a cat, dog, or rabbit) across a game board, encounter monsters, and answer adaptive curriculum questions to earn coins and rewards. Customize your character and challenge yourself for high scores!

**Beyond games, StudyBuddy offers a complete academic toolkit:**
- **Task Manager**: Add, complete, and track your study tasks with progress bars and streaks.
- **Flashcards**: Practice key concepts in all major subjects.
- **Focus Mode**: Listen to calming background music and block distractions.
- **Study Groups**: Join or create groups, chat, and share resources/events.
- **Video Tutorials**: Watch embedded educational videos for math, science, English, and more.
- **Mood Check-Ins**: Log your study mood and notes for self-reflection.
- **Badges & Leaderboards**: Earn achievements and see your rank among top learners.
- **Accessibility**: Adjustable font size, high-contrast mode, and text-to-speech support.

**Everything is tied together in a beautiful, modern dashboard that makes learning engaging, collaborative, and fun. Inspired by games like Prodigy Math and best practices from Google Fonts Knowledge, StudyBuddy is perfect for students, teachers, and lifelong learners.**

---

## Table of Contents

- [Overview](#overview)
- [Story & World](#story--world)
- [Features](#features)
- [Gameplay & User Flow](#gameplay--user-flow)
- [Screenshots](#screenshots)
- [Installation & Setup](#installation--setup)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Customization & Expansion](#customization--expansion)
- [Tech Stack](#tech-stack)
- [Credits & Assets](#credits--assets)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

**StudyBuddy: AngleAlchemy Edition** is an all-in-one, web-based learning platform that makes studying fun and immersive through RPG-inspired gameplay and collaborative tools.

At its heart are two games:

- **AngleAlchemy**: A curriculum-aligned fantasy MMORPG where players battle monsters, solve subject-specific challenges, and embark on a quest to save the magical Realm of Academia.
- **Quiz Quest**: A fast, arcade-style RPG quiz game where users navigate a grid world, defeat monsters, and earn coins by answering questions.

The app also features a dashboard organizing all your study activities, flashcards, focus music, group chat, video tutorials, and more.

---

## Story & World

**The Great Knowledge Heist:**
A mysterious force has stolen the Realm's Knowledge Crystals, threatening to erase all wisdom from the land. The Tree of Knowledge is wilting, and monsters roam, feeding on forgotten facts. The prophecy speaks of a chosen hero – you! – destined to restore balance by defeating monsters, collecting crystals, and rebuilding the City of Scholars.

### Fantasy World Elements

- **Grammar Ghoul Forest**: Face grammar monsters and punctuation puzzles.
- **Math Mountain**: Battle math monsters on snowy peaks.
- **Science Swamp**: Solve bubbling science riddles.
- **History Hall**: Undo the work of the History Eraser.
- **City of Scholars**: Meet sages, accept quests, and shop for upgrades.
- **Special Monsters**: Spellbound Scribe (writing skills), Code Crawler (coding/logic), Mythic Mangler (myth & folklore).

### RPG Elements

- **Quests & Plot:** Restore Knowledge Crystals, defeat the villain, and unlock the secrets of the Tree of Knowledge.
- **Leveling:** Earn XP, collect coins, badges, and special items.
- **Power-Ups:** Brain Boost, Time Freeze, Knowledge Shield, and more.

---

## Features

- **Modern Dashboard:**
  - Glassmorphism design with mascot, logo, and a sidebar for easy navigation
  - Personalized greeting, motivational study tip, and quick access to all features

- **Onboarding & Personalization:**
  - Splash screen and interactive onboarding quiz tailor the dashboard and recommendations to each user

- **Study Plan & Progress:**
  - Animated progress bar, streak tracking, and daily/weekly goals
  - Smart study plan based on user quiz results and activity

- **Flashcards:**
  - 15+ subjects (math, science, English, business, computer science, languages, art, music, history, etc.)
  - Each subject has 15+ questions; questions and explanations are shown for incorrect answers
  - Random question per attempt, instant feedback, and "move on" flow

- **Group Chat & Events:**
  - Sidebar shows all joined groups with big icons and avatars
  - Group chat with file/image upload and video call button (Jitsi Meet integration)
  - Pinned messages/resources and group event calendar with agenda/chronological view

- **Mood Check-ins & AI Insights:**
  - Daily check-in form, mood streaks, and sidebar summary
  - AI-powered insights and suggestions based on tasks, mood, and habits

- **Rewards, Badges, and Leaderboard:**
  - Earn badges for task streaks, focus sessions, and quiz scores
  - See your rank and scores on the leaderboard

- **AngleAlchemy Game:**
  - Explore a fantasy world map
  - Battle subject-aligned monsters with curriculum questions
  - Collect coins, badges, and special items
  - Story-driven quests and hidden locations
  - Adaptive difficulty as you progress

- **Quiz Quest Game:**
  - Move a customizable avatar on a grid
  - Face themed monsters and answer quick quiz questions
  - Earn coins and unlock avatar customizations

- **Focus Mode:**
- Choose from calming, royalty-free music or upload your own MP3 tracks to `static/music/`.
- Set a session timer (Pomodoro or custom length).
- Track your total focus time and session streaks.
- Earn badges for hitting focus milestones.
- All music is available in-app—no extra setup required!

- **Accessibility:**
  - Large font, high-contrast, and text-to-speech support

- **Profile & Avatar:**
  - Upload a custom avatar and view your progress and achievements

---

## Gameplay & User Flow

1. **Login/Register:**
   New users create an account; returning users log in.

2. **Dashboard:**
   Access all features via sidebar or horizontal launcher. See progress, streaks, events, and quick links to games.

3. **AngleAlchemy:**
   - Select a location on the world map
   - Battle monsters by answering multiple-choice questions
   - Earn coins, badges, and progress the story
   - Use power-ups and collect special items

4. **Quiz Quest:**
   - Move your avatar with arrow keys or buttons
   - Encounter monsters, answer questions, and earn coins

5. **Study Tools:**
   - Add/check off tasks, review flashcards, join groups, and watch tutorials

6. **Profile & Achievements:**
   - See badges, coins, check-ins, and customize your avatar
---

## **How It Works**

1. **Register** with a username and password.
2. **Onboard:** See a splash screen and take a quick quiz to personalize your dashboard.
3. **Dashboard:**
    - See your mascot, navigation icons, study plan, progress, badges, and more.
    - The left sidebar gives you instant access to all features and groups.
4. **Study & Collaborate:**
    - Practice with flashcards and quizzes across 15+ subjects.
    - Join or create study groups, chat, share files, and schedule events.
    - Listen to focus music (choose from curated or user-uploaded tracks).
5. **Check In and Grow:**
    - Track your mood, streaks, and unlock badges.
    - Get daily AI insights and career suggestions.
6. **Accessibility:**
    - Toggle high-contrast, large font, or text-to-speech at any time.

---

## Code Structure

- `app.py` — Flask backend, all routes and logic
- `studybuddy.db` — SQLite database for users, tasks, groups, posts, events, music, etc.
- `static/` — All CSS, mascot/logo, images, and uploaded music
- `templates/` — All HTML templates (dashboard, onboarding, chat, quiz, flashcards, profile, etc.)
- `requirements.txt` — Flask, Flask-Session, cs50

---

## How to Run the App

1. Install requirements:
pip install -r requirements.txt

2. Create and migrate the database (see schema in README or run `sqlite3 studybuddy.db` and paste the CREATE TABLE statements).
3. Run Flask:
flask run

4. Visit the provided URL and explore!

---

## How It Works

1. **Login/Register:**
   Users create an account or log in. User progress (tasks, coins, badges, mood check-ins, etc.) is stored per account.

2. **Dashboard:**
   After logging in, users land on a dashboard featuring:
   - Easy access to all tools and games (AngleAlchemy, Quiz Quest, Focus Mode, Flashcards, Groups, Tutorials)
   - Progress bars, study streaks, badges, and motivational images

3. **AngleAlchemy Game:**
   - Users enter a fantasy world map and choose a location.
   - Each location features themed monsters (e.g., Grammar Ghoul, Math Monster) and subject-aligned quiz battles.
   - Correct answers let users defeat monsters, earn coins and badges, and advance the story.

4. **Quiz Quest:**
   - A quick-play RPG grid game; users move their avatar, encounter monsters, and answer questions to earn coins.

5. **Focus Mode:**
   - Choose music, set a timer, and minimize distractions.
   - Tracks focus sessions for stats and streaks.

6. **Study Tools:**
   - Add and complete tasks, practice flashcards, join groups, participate in events, and watch tutorials.

7. **Profile:**
   - View and update personal info, see badges, and track achievements.

---

## Code Structure

- **app.py**: All Flask routes, session management, business logic, and in-memory data for the games.
- **templates/**: Jinja2 HTML templates for dashboard, games, flashcards, profile, etc.
- **static/**: CSS styles, images (mascot, logo, motivational art), music (for Focus Mode), and user uploads.
    - `static/music/`: MP3 study tracks for Focus Mode.
- **studybuddy.db**: SQLite database for persistent storage (users, tasks, groups, events, check-ins, etc.).
- **requirements.txt**: Python dependencies.
- **README.md**: Project documentation.

**Key routes:**
- `/` - Dashboard
- `/anglealchemy`, `/anglealchemy/battle` - Main RPG game
- `/quizquest` - Quick-play RPG quiz game
- `/focus`, `/flashcards`, `/groups`, `/videos`, `/profile` - Core tools

---

## Design Choices

- **Glassmorphism & Soft Colors:**
  - Uses blues, beiges, and gentle dropshadows for a calming, inviting feel.

- **Animated Mascot:**
  - Mascot is always present, offering encouragement and feedback.

- **Sidebar Navigation:**
  - All main features are always one click away, with big friendly icons.

- **Quiz/Flashcards:**
  - Subjects are easily switchable, random questions keep practice fresh.
  - Explanations shown for wrong answers to support learning.

- **Focus Mode:**
  - Playlist-like music selection, Pomodoro timer, and upload support.

- **Accessibility:**
  - All features are keyboard-accessible; easy toggles for vision support.

- **AI Insights:**
  - Dashboard uses task completion, mood, and preferences to suggest breaks or next steps.

- **Gamification:**
  Transforms learning into an RPG experience, motivating students through story, progress, and rewards.

- **Modularity:**
  Each feature (games, focus mode, flashcards, etc.) is a self-contained route and template, ensuring maintainability and future expansion.

- **Accessibility:**
  Supports large font, high-contrast mode, and text-to-speech for inclusivity.

- **Open Assets:**
  Uses royalty-free music, open-source icons, and SVG/PNG art for legal clarity and easy customization.

- **Performance:**
  Loads only necessary resources for each page. Music is stored locally to avoid streaming delays.

- **Responsive UI:**
  Designed with Bootstrap and custom CSS for usability on both desktop and mobile.

---

## Known Issues

- Multiplayer is single-session only (no real-time play/chat yet).
- Some game features (e.g., pets, inventory, advanced quests) are not fully implemented.
- Question difficulty adapts by location but is not yet fully personalized.
- Mobile gameplay is best on larger screens; some UI elements may require adjustment.
- Accessibility features (text-to-speech, high contrast) may not be perfect on all pages.
- If you upload large audio files, Focus Mode may take longer to load.
- Progress is stored in the session and database; if you clear cookies, your session state (badges, coins in AngleAlchemy) may reset.

---

## Future Work

- Add real-time multiplayer (see each other on the map, chat, and co-op battles) using Flask-SocketIO or Firebase.
- Expand AngleAlchemy with more monsters, worlds, and story arcs.
- Add a pet and inventory system, with cosmetic and power-up items.
- Implement teacher/parent dashboards for progress tracking and reporting.
- Add more accessibility options (screen reader optimization, keyboard-only controls).
- Integrate more curriculum-aligned content and adaptive learning algorithms.
- Deploy to cloud (Heroku, Render, etc.) for global classroom access.

---

## Credits & Assets

- Music: [Bensound.com](https://www.bensound.com/), [Mixkit](https://mixkit.co/), [Pixabay Music](https://pixabay.com/music/)
- Icons: [Twemoji](https://twemoji.twitter.com/) and Unicode emojis
- Game Art: [Kenney.nl](https://kenney.nl/assets) and custom SVG/PNG
- Tutorials: YouTube educational channels (see in-app links)
- UI/UX Inspiration: [Prodigy Math](https://www.prodigygame.com/), [Material Design](https://material.io/)

---

## Acknowledgements

- Built for Harvard CS50 by Lindsay Scott
- Thanks to the CS50 team and open-source community for feedback and support!

---

Created by Lindsay Scott X: My edX username is Brains4days.

 | [Lithonia,Georgia]

Video Demo: https://youtu.be/f4yEk2inKkw

---
