import os
import random
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "static", "uploads")
Session(app)
db = SQL("sqlite:///studybuddy.db")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


STUDY_TIPS = [
   "Try the Pomodoro technique: 25 minutes on, 5 minutes off.",
   "Review your notes right after class for better retention.",
   "Don't forget to take a stretch break every hour!",
   "Explain a concept out loud as if teaching a friend.",
   "Keep your study space organized for better focus."
]


MINDFULNESS_TIPS = [
   "Take three deep breaths and notice how your body feels.",
   "Try a 2-minute body scan, focusing on relaxing your muscles.",
   "Step away from your desk for 5 minutes and stretch.",
   "Write down one thing you are grateful for.",
   "Close your eyes and listen to calming music for a few minutes.",
   "Try a short guided meditation on YouTube or a mindfulness app."
]


def get_career_suggestion(completed_tasks, preferences):
   if preferences and preferences.get("prefers_quizzes"):
       return "You might enjoy teaching, education, or edtech careers!"
   if preferences and preferences.get("visual"):
       return "Design, architecture, or visual arts could be a great fit for you."
   if completed_tasks > 10:
       return "Your discipline suggests you'd be a great project manager!"
   return "Explore your interests with StudyBuddy AI Career Explorer!"


def ai_insights(tasks, checkins):
   if tasks and sum(1 for t in tasks if not t["completed"]) > 3:
       return "You have several unfinished tasks. Consider focusing on your top priority first, or try a Pomodoro session!"
   if checkins and any(int(c["mood"]) < 5 for c in checkins):
       return "It looks like you're feeling stressed. Take a short break, try a mindfulness exercise, or reach out to a mentor."
   if tasks and any("review" in t["description"].lower() for t in tasks):
       return "Reviewing previous material boosts your long-term memory!"
   if tasks and any("coding" in t["description"].lower() for t in tasks):
       return 'Need help with coding? <a href="https://www.youtube.com/watch?v=rfscVS0vtbw" target="_blank">Watch this Python tutorial</a>.'
   return "You're on track! Consider reviewing flashcards or watching a recommended tutorial."


@app.route("/")
def dashboard():
   if not session.get("user_id"):
       return redirect("/login")
   if not session.get("welcomed"):
       session["welcomed"] = True
       return render_template("welcome.html", username=session.get("username"))
   user_id = session["user_id"]
   user_groups = db.execute("""
       SELECT study_groups.* FROM study_groups
       JOIN group_members ON study_groups.id = group_members.group_id
       WHERE group_members.user_id = ?
   """, user_id)
   tasks = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date", user_id)
   checkins = db.execute("SELECT mood, note, created_at FROM checkins WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", user_id)
   tip = random.choice(STUDY_TIPS)
   preferences = db.execute("SELECT * FROM preferences WHERE user_id = ?", user_id)
   needs_survey = len(preferences) == 0
   completed_count = db.execute("SELECT COUNT(*) AS count FROM tasks WHERE user_id = ? AND completed = 1", user_id)[0]["count"]
   checkin_count = db.execute("SELECT COUNT(*) AS count FROM checkins WHERE user_id = ?", user_id)[0]["count"]
   focus_stats = db.execute(
       "SELECT COUNT(*) AS sessions, SUM(duration) AS total_time FROM focus_sessions WHERE user_id = ?", user_id
   )[0] if db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='focus_sessions'") else {}
   badges = []
   if completed_count >= 5:
       badges.append("🎓 5 Tasks Completed")
   if completed_count >= 10:
       badges.append("🏅 10 Tasks Completed")
   if focus_stats and (focus_stats.get("sessions") or 0) >= 10:
       badges.append("🕒 10 Focus Sessions")
   if focus_stats and (focus_stats.get("total_time") or 0) >= 3600:
       badges.append("⏳ 1 Hour Focused")
   if checkin_count >= 3:
       badges.append("🧘 3 Mood Check-Ins")
   if checkin_count >= 7:
       badges.append("🏆 7 Check-Ins: Mindfulness Pro")
   leaderboard = db.execute("""
       SELECT users.username, COUNT(tasks.id) as completed
       FROM users
       LEFT JOIN tasks ON users.id = tasks.user_id AND tasks.completed = 1
       GROUP BY users.id
       ORDER BY completed DESC, users.username ASC
       LIMIT 5
   """)
   career_tip = get_career_suggestion(completed_count, preferences[0] if preferences else {})
   insight = ai_insights(tasks, checkins)
   events = db.execute("""
       SELECT events.* FROM events
       JOIN group_members ON events.group_id = group_members.group_id
       WHERE group_members.user_id = ? AND datetime(events.event_datetime) >= datetime('now')
       ORDER BY events.event_datetime
       LIMIT 5
   """, user_id)
   streak = 0
   progress_percent = int(100 * completed_count / max(1, len(tasks)))
   return render_template("dashboard.html",
       tasks=tasks,
       checkins=checkins,
       tip=tip,
       needs_survey=needs_survey,
       preferences=preferences[0] if preferences else None,
       badges=badges,
       leaderboard=leaderboard,
       user_groups=user_groups,
       focus_stats=focus_stats,
       career_tip=career_tip,
       insight=insight,
       events=events,
       streak=streak,
       progress_percent=progress_percent
   )


@app.route("/clear_welcome")
def clear_welcome():
   session["welcomed"] = False
   return ("", 204)


@app.route("/onboarding_quiz", methods=["GET", "POST"])
def onboarding_quiz():
   if not session.get("user_id"):
       return redirect("/login")
   if request.method == "GET":
       return render_template("onboarding_quiz.html")
   user_id = session["user_id"]
   goal = request.form.get("goal")
   flashcards = int(bool(request.form.get("flashcards")))
   reading = int(bool(request.form.get("reading")))
   practice = int(bool(request.form.get("practice")))
   videos = int(bool(request.form.get("videos")))
   subject = request.form.get("subject")
   db.execute(
       "INSERT OR REPLACE INTO preferences (user_id, goal, flashcards, reading, practice, videos, subject) VALUES (?, ?, ?, ?, ?, ?, ?)",
       user_id, goal, flashcards, reading, practice, videos, subject
   )
   flash("Personalization complete! Your dashboard is ready.")
   return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
   if request.method == "GET":
       return render_template("register.html")
   username = request.form.get("username")
   password = request.form.get("password")
   confirmation = request.form.get("confirmation")
   if not username:
       return apology("must provide username")
   if not password:
       return apology("must provide password")
   if not confirmation:
       return apology("must confirm password")
   if password != confirmation:
       return apology("passwords do not match")
   hash_pw = generate_password_hash(password)
   try:
       user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)
   except Exception:
       return apology("username already exists")
   session["user_id"] = user_id
   session["username"] = username
   session["welcomed"] = False
   return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
   session.clear()
   if request.method == "GET":
       return render_template("login.html")
   username = request.form.get("username")
   password = request.form.get("password")
   if not username or not password:
       return apology("must provide username and password")
   user = db.execute("SELECT * FROM users WHERE username = ?", username)
   if not user or not check_password_hash(user[0]["hash"], password):
       return apology("invalid username and/or password")
   session["user_id"] = user[0]["id"]
   session["username"] = username
   session["welcomed"] = False
   return redirect("/")


@app.route("/logout")
def logout():
   session.clear()
   return redirect("/login")


@app.route("/profile", methods=["GET", "POST"])
def profile():
   if not session.get("user_id"):
       return redirect("/login")
   user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
   if request.method == "POST":
       file = request.files.get("avatar")
       if file and file.filename:
           filename = secure_filename(file.filename)
           filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
           file.save(filepath)
           avatar_url = f"/static/uploads/{filename}"
           db.execute("UPDATE users SET avatar_url = ? WHERE id = ?", avatar_url, session["user_id"])
           flash("Avatar updated!")
           return redirect("/profile")
   return render_template("profile.html", user=user)


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
   if not session.get("user_id"):
       return redirect("/login")
   if request.method == "GET":
       return render_template("checkin.html")
   mood = request.form.get("mood")
   note = request.form.get("note")
   if not mood or not mood.isdigit() or int(mood) < 1 or int(mood) > 10:
       return apology("please provide a mood value between 1 and 10")
   user_id = session["user_id"]
   db.execute(
       "INSERT INTO checkins (user_id, mood, note) VALUES (?, ?, ?)",
       user_id, int(mood), note
   )
   flash("Check-in submitted! Keep taking care of yourself! 😊")
   return redirect("/")


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
   if not session.get("user_id"):
       return redirect("/login")
   if request.method == "GET":
       return render_template("add_task.html")
   description = request.form.get("description")
   due_date = request.form.get("due_date")
   if not description:
       return apology("must provide a task description")
   user_id = session["user_id"]
   db.execute(
       "INSERT INTO tasks (user_id, description, due_date) VALUES (?, ?, ?)",
       user_id, description, due_date if due_date else None
   )
   flash("Task added!")
   return redirect("/")


@app.route("/complete_task", methods=["POST"])
def complete_task():
   if not session.get("user_id"):
       return redirect("/login")
   task_id = request.form.get("task_id")
   db.execute(
       "UPDATE tasks SET completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
       task_id, session["user_id"]
   )
   flash("Task marked as complete! 🎉")
   return redirect("/")


@app.route("/focus")
def focus():
   if not session.get("user_id"):
       return redirect("/login")
   tracks = [
       {"title": "Angels By My Side", "url": url_for('static', filename='music/bensound-angelsbymyside.mp3')},
       {"title": "Long Night", "url": url_for('static', filename='music/bensound-longnight.mp3')},
       {"title": "Melancholy Lull ", "url": url_for('static', filename='music/bensound-melancholylull.mp3')},
       {"title": "Moonlight Drive ", "url": url_for('static', filename='music/bensound-moonlightdrive.mp3')},
       {"title": "Classical Guitar", "url": url_for('static', filename='music/nesrality-classical-guitar-estudio-7-by-francisco-tarrega-1852-1909-120795.mp3')},
       {"title": "Sun and His Daughter – Mixkit", "url": url_for('static', filename='music/mixkit-sun-and-his-daughter-580.mp3')},
   ]
   selected_track = request.args.get("track") or tracks[0]["url"]
   return render_template("focus.html", playlist=tracks, selected_track=selected_track)


@app.route("/upload_music", methods=["POST"])
def upload_music():
   if not session.get("user_id"):
       return redirect("/login")
   mood = request.form.get("mood") or "general"
   file = request.files.get("music")
   if file and file.filename:
       filename = secure_filename(file.filename)
       filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
       file.save(filepath)
       url = f"/static/uploads/{filename}"
       db.execute("INSERT INTO music_tracks (user_id, filename, url, mood) VALUES (?, ?, ?, ?)",
                  session["user_id"], filename, url, mood)
       flash("Music uploaded! Ready to focus?")
   return redirect("/focus")


@app.route("/focus_session", methods=["POST"])
def focus_session():
   if not session.get("user_id"):
       return "", 401
   user_id = session["user_id"]
   duration = int(request.form.get("duration", 0))
   db.execute(
       "INSERT INTO focus_sessions (user_id, start_time, end_time, duration) VALUES (?, datetime('now', '-? seconds'), datetime('now'), ?)",
       user_id, duration, duration
   )
   return ("", 204)


@app.route("/music")
def music():
   music_folder = os.path.join(app.static_folder, "music")
   tracks = [f for f in os.listdir(music_folder) if f.lower().endswith(".mp3")]
   return render_template("music.html", tracks=tracks)


@app.route("/accessibility")
def accessibility():
   return render_template("accessibility.html")


@app.route("/flashcards", methods=["GET", "POST"])
def flashcards():
   if not session.get("user_id"):
       return redirect("/login")
   sets = {
       "math": [
       {"question": "What is the formula for quadratic equation?", "answer": "x = (-b ± sqrt(b^2 - 4ac)) / 2a", "explanation": "The quadratic formula solves ax^2+bx+c=0."},
       {"question": "Solve: 2x + 5 = 11", "answer": "3", "explanation": "2x = 6 → x = 3."},
       {"question": "What is the value of x in x^2 + 4x + 4 = 0?", "answer": "-2", "explanation": "(x+2)^2=0 → x=-2."},
       {"question": "What is the Pythagorean theorem?", "answer": "a^2 + b^2 = c^2", "explanation": "Relates lengths of sides in a right triangle."},
       {"question": "Solve for y: y - 3 = 7", "answer": "10", "explanation": "Add 3 to both sides: y=10."},
       {"question": "What is the derivative of x^2?", "answer": "2x", "explanation": "Power rule: d/dx x^n = nx^{n-1}."},
       {"question": "What is 5! (5 factorial)?", "answer": "120", "explanation": "5! = 5×4×3×2×1 = 120."},
       {"question": "Solve the equation: x + 2 = 9", "answer": "7", "explanation": "Subtract 2: x=7."},
       {"question": "What is the formula for the area of a circle?", "answer": "πr^2", "explanation": "Area = pi × radius squared."},
       {"question": "What is the slope-intercept form of a line?", "answer": "y = mx + b", "explanation": "m is slope, b is y-intercept."},
       {"question": "Solve: 3x - 2 = 14", "answer": "16/3", "explanation": "3x=16 → x=16/3."},
       {"question": "What is the value of x in 2^x = 8?", "answer": "3", "explanation": "2^3 = 8."},
       {"question": "What is the sum of interior angles in a triangle?", "answer": "180", "explanation": "All triangles' angles sum to 180 degrees."},
       {"question": "Solve: x/2 + 3 = 7", "answer": "8", "explanation": "x/2=4 → x=8."},
       {"question": "What is the formula for compound interest?", "answer": "A = P(1 + r/n)^{nt}", "explanation": "Compound interest formula, where P=principal, r=rate, n=times/year, t=years."}
   ],
   "science": [
       {"question": "What is photosynthesis?", "answer": "Process plants use to make food", "explanation": "Plants convert sunlight, CO2, and water into glucose and oxygen."},
       {"question": "Define mitosis.", "answer": "Cell division into two identical cells", "explanation": "Mitosis produces two genetically identical daughter cells."},
       {"question": "What is the largest planet in our solar system?", "answer": "Jupiter", "explanation": "Jupiter is the biggest planet."},
       {"question": "What is the process of respiration?", "answer": "Releasing energy from food", "explanation": "Cells convert glucose and oxygen into energy."},
       {"question": "What is Newton's first law of motion?", "answer": "Objects in motion stay in motion", "explanation": "Unless acted upon by an external force."},
       {"question": "What is the periodic symbol for gold?", "answer": "Au", "explanation": "'Au' is gold's symbol."},
       {"question": "What is DNA?", "answer": "Deoxyribonucleic acid", "explanation": "Molecule carrying genetic instructions."},
       {"question": "What is the water cycle?", "answer": "Movement of water on Earth", "explanation": "Includes evaporation, condensation, precipitation."},
       {"question": "What is the theory of relativity?", "answer": "Einstein's theory of space and time", "explanation": "Explains gravity and motion at high speeds."},
       {"question": "What is the process of evaporation?", "answer": "Liquid turning into gas", "explanation": "Water becomes vapor."},
       {"question": "What is the structure of an atom?", "answer": "Protons, neutrons, electrons", "explanation": "Nucleus contains protons/neutrons, electrons orbit."},
       {"question": "What is biodiversity?", "answer": "Variety of life", "explanation": "Diversity of organisms in an ecosystem."},
       {"question": "What is climate change?", "answer": "Long-term change in Earth's climate", "explanation": "Due to natural and human causes."},
       {"question": "What is the function of the heart?", "answer": "Pumps blood", "explanation": "Circulates oxygen and nutrients."},
       {"question": "What is the difference between a hypothesis and a theory?", "answer": "Hypothesis is a testable idea; theory is well-tested explanation", "explanation": "Hypotheses are tested, theories are confirmed by evidence."}
   ],
   "history": [
       {"question": "Who was Albert Einstein?", "answer": "A physicist", "explanation": "He developed the theory of relativity."},
       {"question": "What was the Treaty of Versailles?", "answer": "Ended World War I", "explanation": "Signed in 1919, imposed penalties on Germany."},
       {"question": "What year did World War I start?", "answer": "1914", "explanation": "WWI began in 1914."},
       {"question": "Who was Cleopatra?", "answer": "Queen of Egypt", "explanation": "Last active ruler of the Ptolemaic Kingdom."},
       {"question": "What was the Renaissance?", "answer": "Period of cultural rebirth", "explanation": "Spanned the 14th–17th centuries in Europe."},
       {"question": "What was the Industrial Revolution?", "answer": "Era of rapid industrial growth", "explanation": "18th–19th centuries, transition to new manufacturing."},
       {"question": "Who was Martin Luther King Jr.?", "answer": "Civil rights leader", "explanation": "Led the movement for racial equality in the US."},
       {"question": "What was the American Revolution?", "answer": "War for American independence", "explanation": "1775–1783, US colonies broke from Britain."},
       {"question": "What was the significance of the Magna Carta?", "answer": "Limited king's power", "explanation": "Signed in 1215, established rule of law."},
       {"question": "Who was Napoleon Bonaparte?", "answer": "French military leader", "explanation": "Became Emperor of France."},
       {"question": "What was the Cold War?", "answer": "US-Soviet political tension", "explanation": "Lasted from 1947–1991."},
       {"question": "What was the Berlin Wall?", "answer": "Barrier dividing Berlin", "explanation": "Symbol of Cold War, fell in 1989."},
       {"question": "Who was Rosa Parks?", "answer": "Civil rights activist", "explanation": "Refused to give up seat on a bus in 1955."},
       {"question": "What was the Great Depression?", "answer": "Severe global economic downturn", "explanation": "Began in 1929."},
       {"question": "What was the impact of the printing press?", "answer": "Spread information quickly", "explanation": "Revolutionized communication and education."}
   ],
   "english": [
       {"question": "What is a metaphor?", "answer": "A comparison without using 'like' or 'as'", "explanation": "A metaphor directly compares two things."},
       {"question": "Summarize Chapter 1 of To Kill a Mockingbird.", "answer": "Scout introduces her family and Maycomb.", "explanation": "The chapter sets up the main characters and setting."},
       {"question": "Who is the author of Pride and Prejudice?", "answer": "Jane Austen", "explanation": "Famous English novelist."},
       {"question": "What is alliteration?", "answer": "Repetition of initial consonant sounds", "explanation": "E.g., 'She sells seashells…'."},
       {"question": "What is the theme of Romeo and Juliet?", "answer": "Love and conflict", "explanation": "Explores love, fate, and family rivalry."},
       {"question": "Who is the protagonist in The Great Gatsby?", "answer": "Jay Gatsby", "explanation": "The title character."},
       {"question": "What is a simile?", "answer": "A comparison using 'like' or 'as'", "explanation": "E.g., 'as brave as a lion'."},
       {"question": "What is the difference between a novel and a short story?", "answer": "A novel is longer; short story is brief", "explanation": "Novels have more developed plots and characters."},
       {"question": "Who is Shakespeare?", "answer": "English playwright and poet", "explanation": "Famous for plays like Hamlet and Romeo and Juliet."},
       {"question": "What is the plot of Hamlet?", "answer": "Prince Hamlet seeks revenge for his father's death.", "explanation": "A tragedy involving betrayal and madness."},
       {"question": "What is personification?", "answer": "Giving human traits to non-humans", "explanation": "E.g., 'The wind whispered'."},
       {"question": "What is the setting of The Hunger Games?", "answer": "Dystopian future in Panem", "explanation": "A country divided into districts."},
       {"question": "Who is the author of The Catcher in the Rye?", "answer": "J.D. Salinger", "explanation": "Written in 1951."},
       {"question": "What is a plot twist?", "answer": "Unexpected development in a story", "explanation": "Surprises the reader."},
       {"question": "What is the difference between poetry and prose?", "answer": "Poetry uses verse; prose is ordinary writing", "explanation": "Poetry often has rhythm and rhyme."}
   ],
   "languages": [
       {"question": "What is the translation of 'hello' in Spanish?", "answer": "Hola", "explanation": "Hola means hello in Spanish."},
       {"question": "Conjugate 'hablar' in Spanish.", "answer": "Hablo, hablas, habla, hablamos, habláis, hablan", "explanation": "Present tense forms of 'to speak'."},
       {"question": "What is the difference between ser and estar in Spanish?", "answer": "Ser is for permanent; estar is for temporary", "explanation": "Ser: identity, Estar: condition/location."},
       {"question": "What is the French word for 'book'?", "answer": "Livre", "explanation": "Livre means book in French."},
       {"question": "What is the German word for 'car'?", "answer": "Auto", "explanation": "'Auto' is car in German."},
       {"question": "What is the Italian word for 'food'?", "answer": "Cibo", "explanation": "'Cibo' means food in Italian."},
       {"question": "Conjugate 'être' in French.", "answer": "Suis, es, est, sommes, êtes, sont", "explanation": "Present tense of 'to be'."},
       {"question": "What is the Spanish word for 'water'?", "answer": "Agua", "explanation": "'Agua' means water in Spanish."},
       {"question": "What is the difference between le and la in French?", "answer": "Le is masculine; la is feminine", "explanation": "French articles for nouns."},
       {"question": "What is the German word for 'house'?", "answer": "Haus", "explanation": "'Haus' means house in German."},
       {"question": "What is the Italian word for 'friend'?", "answer": "Amico (male), Amica (female)", "explanation": "Gendered nouns in Italian."},
       {"question": "Conjugate 'parler' in French.", "answer": "Parle, parles, parle, parlons, parlez, parlent", "explanation": "Present tense of 'to speak'."},
       {"question": "What is the Spanish word for 'school'?", "answer": "Escuela", "explanation": "'Escuela' means school in Spanish."},
       {"question": "What is the French word for 'city'?", "answer": "Ville", "explanation": "'Ville' means city in French."},
       {"question": "What is the German word for 'food'?", "answer": "Essen", "explanation": "'Essen' means food in German."},
   ],
   "business": [
       {"question": "What is SWOT analysis?", "answer": "Strengths, Weaknesses, Opportunities, Threats", "explanation": "It's a framework for analyzing a business."},
       {"question": "Define ROI.", "answer": "Return on Investment", "explanation": "Measures profitability of an investment."},
       {"question": "What is a business plan?", "answer": "Document outlining a company's goals", "explanation": "Includes strategy, marketing, and financials."},
       {"question": "What is marketing?", "answer": "Promoting and selling products", "explanation": "Includes advertising and market research."},
       {"question": "What is a target audience?", "answer": "Intended group for a product", "explanation": "The people a business aims to reach."},
       {"question": "What is branding?", "answer": "Creating a unique identity", "explanation": "Includes logo, name, and reputation."},
       {"question": "What is a startup?", "answer": "Newly established business", "explanation": "Often focused on innovation and growth."},
       {"question": "What is entrepreneurship?", "answer": "Starting and managing a business", "explanation": "Entrepreneurs take financial risks."},
       {"question": "What is a pitch?", "answer": "Presentation to attract investors", "explanation": "Explains the business idea and value."},
       {"question": "What is a business model?", "answer": "Plan for making profit", "explanation": "Describes how a company creates value."},
       {"question": "What is financial forecasting?", "answer": "Predicting future revenues and expenses", "explanation": "Used for planning and budgeting."},
       {"question": "What is a balance sheet?", "answer": "Financial statement showing assets, liabilities, equity", "explanation": "Snapshot of a company's finances."},
       {"question": "What is a mission statement?", "answer": "Company's purpose and values", "explanation": "Guides strategy and decision making."},
       {"question": "What is corporate social responsibility?", "answer": "Company's commitment to ethical behavior", "explanation": "Includes environmental and social initiatives."},
       {"question": "What is a competitive advantage?", "answer": "Unique edge over competitors", "explanation": "Helps a company succeed in the market."}
   ],
"computer_science": [
       {"question": "What is recursion?", "answer": "A function calling itself", "explanation": "Recursion is when a function solves a problem by calling itself."},
       {"question": "Write a simple loop in Python.", "answer": "for i in range(5): print(i)", "explanation": "A for loop repeats code multiple times."},
       {"question": "What is a data structure?", "answer": "A way of organizing data", "explanation": "Examples include lists, stacks, and queues."},
       {"question": "What is an algorithm?", "answer": "A set of instructions to solve a problem", "explanation": "Algorithms are step-by-step procedures."},
       {"question": "What is object-oriented programming?", "answer": "Programming using objects and classes", "explanation": "OOP organizes code into reusable objects."},
       {"question": "What is a variable?", "answer": "A named storage for data", "explanation": "Variables store values in programs."},
       {"question": "What is a loop?", "answer": "Repeats code multiple times", "explanation": "Loops automate repetitive tasks."},
       {"question": "What is conditional logic?", "answer": "Making decisions using if/else", "explanation": "Runs code depending on conditions."},
       {"question": "What is a function?", "answer": "Reusable block of code", "explanation": "Functions take inputs and return outputs."},
       {"question": "What is debugging?", "answer": "Finding and fixing errors", "explanation": "Debugging helps correct code mistakes."},
       {"question": "What is a stack?", "answer": "LIFO data structure", "explanation": "Last-In, First-Out: like a stack of plates."},
       {"question": "What is a queue?", "answer": "FIFO data structure", "explanation": "First-In, First-Out: like a line at a store."},
       {"question": "What is a binary search?", "answer": "Efficient search in sorted data", "explanation": "Divides data in half each time."},
       {"question": "What is a hash table?", "answer": "Key-value storage for fast lookup", "explanation": "Uses a hash function to index data."},
       {"question": "What is a linked list?", "answer": "Sequence of nodes with pointers", "explanation": "Each node points to the next."}
   ],
   "art": [
       {"question": "Who is Leonardo da Vinci?", "answer": "An Italian artist/inventor", "explanation": "Leonardo was a Renaissance painter and inventor."},
       {"question": "Describe Impressionism.", "answer": "Art style with visible brushstrokes and light", "explanation": "Focuses on light and color, not detail."},
       {"question": "What is a still life?", "answer": "Artwork of inanimate objects", "explanation": "Such as fruit or flowers."},
       {"question": "Who is Vincent van Gogh?", "answer": "Dutch Post-Impressionist painter", "explanation": "Known for 'Starry Night'."},
       {"question": "What is abstract art?", "answer": "Art that doesn't represent reality", "explanation": "Uses shapes, colors, forms for effect."},
       {"question": "What is a portrait?", "answer": "Artwork depicting a person", "explanation": "Shows the likeness of a subject."},
       {"question": "Who is Pablo Picasso?", "answer": "Spanish painter and sculptor", "explanation": "Founder of Cubism."},
       {"question": "What is surrealism?", "answer": "Art movement showing dreamlike scenes", "explanation": "Combines reality with imagination."},
       {"question": "What is a landscape?", "answer": "Artwork depicting scenery", "explanation": "Shows outdoor natural scenes."},
       {"question": "Who is Monet?", "answer": "French Impressionist painter", "explanation": "Famous for water lily paintings."},
       {"question": "What is a sculpture?", "answer": "Three-dimensional artwork", "explanation": "Made by shaping materials like stone or metal."},
       {"question": "What is modern art?", "answer": "Art from the late 19th century onwards", "explanation": "Breaks traditional forms and ideas."},
       {"question": "Who is Frida Kahlo?", "answer": "Mexican painter", "explanation": "Known for self-portraits and bold colors."},
       {"question": "What is a collage?", "answer": "Art made by assembling different materials", "explanation": "Combines paper, photos, fabric, etc."},
       {"question": "What is a watercolor?", "answer": "Painting with water-based pigments", "explanation": "Uses water to dilute colors."}
   ],
   "music": [
       {"question": "What is a chord progression?", "answer": "A series of chords", "explanation": "Chord progressions are sequences of chords in music."},
       {"question": "Who is Mozart?", "answer": "A classical composer", "explanation": "Wolfgang Amadeus Mozart wrote symphonies and operas."},
       {"question": "What is harmony?", "answer": "Combination of simultaneous notes", "explanation": "Creates chords and supports melody."},
       {"question": "What is rhythm?", "answer": "Pattern of sounds and silences", "explanation": "Gives music its timing and beat."},
       {"question": "What is a scale?", "answer": "Series of musical notes in order", "explanation": "E.g., C major scale: C D E F G A B."},
       {"question": "Who is Beethoven?", "answer": "A German composer and pianist", "explanation": "Known for symphonies and sonatas."},
       {"question": "What is jazz?", "answer": "Music genre with improvisation", "explanation": "Originated in African-American communities."},
       {"question": "What is rock music?", "answer": "Popular music genre with electric guitars", "explanation": "Began in the 1950s."},
       {"question": "What is a symphony?", "answer": "Extended musical composition for orchestra", "explanation": "Usually in four movements."},
       {"question": "Who is Jimi Hendrix?", "answer": "Rock guitarist and singer", "explanation": "Revolutionized electric guitar playing."},
       {"question": "What is melody?", "answer": "Sequence of musical notes", "explanation": "The tune you hum or sing."},
       {"question": "What is a tempo?", "answer": "Speed of music", "explanation": "Measured in beats per minute (BPM)."},
       {"question": "What is a genre?", "answer": "Category of music", "explanation": "E.g., rock, pop, classical."},
       {"question": "Who is Taylor Swift?", "answer": "American singer-songwriter", "explanation": "Known for storytelling in her music."},
       {"question": "What is a music staff?", "answer": "Set of five lines for notation", "explanation": "Notes are placed on the staff."}
   ],
   "physical_education": [
       {"question": "What is a proper squat form?", "answer": "Back straight, knees over toes, hips back", "explanation": "Proper squats protect your knees and back."},
       {"question": "What is a warm-up exercise?", "answer": "Activity that prepares body for exercise", "explanation": "Increases blood flow and reduces injury risk."},
       {"question": "What is a cool-down exercise?", "answer": "Activity after exercise to relax muscles", "explanation": "Helps heart rate and breathing return to normal."},
       {"question": "What is cardio?", "answer": "Exercise increasing heart rate", "explanation": "Examples: running, cycling, swimming."},
       {"question": "What is strength training?", "answer": "Exercise to build muscle", "explanation": "Uses weights or resistance bands."},
       {"question": "What is flexibility?", "answer": "Ability to move joints freely", "explanation": "Helps prevent injury and maintain mobility."},
       {"question": "What is a healthy BMI?", "answer": "Body Mass Index between 18.5 and 24.9", "explanation": "BMI measures body fat based on height and weight."},
       {"question": "What is hydration?", "answer": "Maintaining fluid balance in the body", "explanation": "Drinking enough water is essential for health."},
       {"question": "What is a serving size?", "answer": "Recommended amount of food to eat", "explanation": "Used for nutrition labels and healthy eating."},
       {"question": "What is a macronutrient?", "answer": "Nutrients needed in large amounts", "explanation": "Carbohydrates, proteins, fats."},
       {"question": "What is a micronutrient?", "answer": "Nutrients needed in small amounts", "explanation": "Vitamins and minerals."},
       {"question": "What is a fitness goal?", "answer": "Target related to physical health", "explanation": "Examples: run a mile, lift weights, lose weight."},
       {"question": "What is a workout routine?", "answer": "Planned schedule of exercises", "explanation": "Helps achieve fitness goals."},
       {"question": "What is a rest day?", "answer": "Day with no intense exercise", "explanation": "Allows body to recover and prevent injury."},
       {"question": "What is a sports injury?", "answer": "Physical damage during exercise or sports", "explanation": "Examples: sprains, strains, fractures."}
   ],
   "psychology": [
       {"question": "What is cognitive bias?", "answer": "Systematic error in thinking", "explanation": "Cognitive biases affect judgment and decision making."},
       {"question": "Define self-actualization.", "answer": "Realizing one's full potential", "explanation": "Top level of Maslow's hierarchy of needs."},
       {"question": "What is anxiety?", "answer": "Feeling of worry or unease", "explanation": "Can be a normal or disordered response."},
       {"question": "What is depression?", "answer": "Persistent sadness and loss of interest", "explanation": "A mental health disorder."},
       {"question": "What is a growth mindset?", "answer": "Belief abilities can be developed", "explanation": "Opposite of a fixed mindset."},
       {"question": "What is emotional intelligence?", "answer": "Ability to recognize and manage emotions", "explanation": "Includes self-awareness and empathy."},
       {"question": "What is a coping mechanism?", "answer": "Strategy to manage stress", "explanation": "Examples: exercise, talking to friends."},
       {"question": "What is a mental health disorder?", "answer": "Condition affecting mood, thinking, behavior", "explanation": "Examples: anxiety, depression, schizophrenia."},
       {"question": "What is a personality trait?", "answer": "Characteristic way of thinking or behaving", "explanation": "Examples: openness, conscientiousness."},
       {"question": "What is a psychological theory?", "answer": "Explanation of mental processes", "explanation": "Backed by research and evidence."},
       {"question": "What is a research method?", "answer": "Way to collect and analyze data", "explanation": "Examples: experiments, surveys, observations."},
       {"question": "What is a statistical analysis?", "answer": "Process of examining data with statistics", "explanation": "Used to find patterns and draw conclusions."},
       {"question": "What is a psychological assessment?", "answer": "Evaluation of mental health", "explanation": "Can include interviews and standardized tests."},
       {"question": "What is a therapy approach?", "answer": "Method used in psychological treatment", "explanation": "Examples: cognitive-behavioral therapy, psychoanalysis."},
       {"question": "What is a mental health resource?", "answer": "Support for mental wellness", "explanation": "Examples: counseling, hotlines, support groups."}
   ],
   "sociology": [
       {"question": "What is social stratification?", "answer": "Ranking of people in society", "explanation": "Division into layers based on status."},
       {"question": "Define cultural capital.", "answer": "Non-financial assets that promote social mobility", "explanation": "Includes education, style, language."},
       {"question": "What is a social norm?", "answer": "Expected behavior in a society", "explanation": "Unwritten rules that guide actions."},
       {"question": "What is a social institution?", "answer": "Organized system that meets society's needs", "explanation": "Examples: family, education, religion."},
       {"question": "What is a social movement?", "answer": "Organized effort for social change", "explanation": "Examples: civil rights, environmentalism."},
       {"question": "What is a cultural trend?", "answer": "Pattern of change in culture", "explanation": "Widespread adoption of behavior or ideas."},
       {"question": "What is a social identity?", "answer": "Sense of self based on group membership", "explanation": "Examples: nationality, religion, gender."},
       {"question": "What is a power dynamic?", "answer": "Relationship of power between people/groups", "explanation": "Influences behavior and access to resources."},
       {"question": "What is a social network?", "answer": "Web of social relationships", "explanation": "Connections between individuals/groups."},
       {"question": "What is a demographic?", "answer": "Statistical characteristic of a population", "explanation": "Examples: age, gender, income."},
       {"question": "What is a social issue?", "answer": "Problem that affects many people", "explanation": "Examples: poverty, inequality, discrimination."},
       {"question": "What is a policy analysis?", "answer": "Evaluation of public policies", "explanation": "Assesses effectiveness and impact."},
       {"question": "What is a research design?", "answer": "Plan for conducting research", "explanation": "Determines how data will be collected and analyzed."},
       {"question": "What is a statistical concept?", "answer": "Idea related to data analysis", "explanation": "Examples: mean, median, standard deviation."},
       {"question": "What is a sociological theory?", "answer": "Framework for understanding society", "explanation": "Examples: functionalism, conflict theory, symbolic interactionism."}
   ],
   "philosophy": [
       {"question": "Who is Plato?", "answer": "A Greek philosopher", "explanation": "Plato was a student of Socrates and teacher of Aristotle."},
       {"question": "What is existentialism?", "answer": "Philosophy about individual meaning and freedom", "explanation": "Focuses on choice, responsibility, and authenticity."},
       {"question": "What is a philosophical argument?", "answer": "Reasoned set of claims supporting a conclusion", "explanation": "Uses logic and evidence."},
       {"question": "What is ethics?", "answer": "Study of right and wrong", "explanation": "Explores moral principles and values."},
       {"question": "What is morality?", "answer": "System of values and principles", "explanation": "Distinguishes right from wrong behavior."},
       {"question": "What is a logical fallacy?", "answer": "Error in reasoning", "explanation": "Weakens arguments and conclusions."},
       {"question": "What is a thought experiment?", "answer": "Imaginative scenario to explore ideas", "explanation": "Famous example: Schrödinger's cat."},
       {"question": "Who is Kant?", "answer": "German philosopher", "explanation": "Immanuel Kant is known for deontological ethics."},
       {"question": "What is a philosophical concept?", "answer": "Abstract idea in philosophy", "explanation": "Examples: justice, truth, beauty."},
       {"question": "What is a worldview?", "answer": "Overall perspective on life and the world", "explanation": "Influences beliefs and actions."},
       {"question": "What is a philosophical question?", "answer": "Question about fundamental nature of reality", "explanation": "Examples: What is knowledge? What is existence?"},
       {"question": "What is a philosophical theory?", "answer": "Systematic explanation of philosophical topics", "explanation": "Examples: utilitarianism, dualism."},
       {"question": "What is a philosophical movement?", "answer": "Group of related philosophical ideas", "explanation": "Examples: empiricism, pragmatism."},
       {"question": "Who is Nietzsche?", "answer": "German philosopher", "explanation": "Friedrich Nietzsche wrote about existentialism and the will to power."},
       {"question": "What is a philosophical critique?", "answer": "Evaluation of philosophical ideas or arguments", "explanation": "Analyzes strengths and weaknesses."}
   ],
       "biology": [
       {"question": "What is photosynthesis?", "answer": "Process plants use to make food", "explanation": "Plants convert sunlight, CO2, and water into glucose and oxygen."},
       {"question": "Define DNA.", "answer": "Deoxyribonucleic acid", "explanation": "DNA carries genetic information in cells."},
       {"question": "What is a cell?", "answer": "Basic unit of life", "explanation": "All living things are made of cells."},
       {"question": "What is a species?", "answer": "Group of similar organisms that can breed", "explanation": "Members of a species produce fertile offspring."},
       {"question": "What is an ecosystem?", "answer": "Community of living and nonliving things", "explanation": "Organisms interact with each other and their environment."},
       {"question": "What is a food chain?", "answer": "Series of organisms each dependent on the next as a food source", "explanation": "Shows how energy moves through an ecosystem."},
       {"question": "What is a symbiotic relationship?", "answer": "Close relationship between two species", "explanation": "Can be mutualism, commensalism, or parasitism."},
       {"question": "What is adaptation?", "answer": "Trait that improves survival", "explanation": "Helps organisms fit their environment."},
       {"question": "What is natural selection?", "answer": "Process where better-adapted organisms survive and reproduce", "explanation": "Key mechanism of evolution."},
       {"question": "What is a genetic disorder?", "answer": "Disease caused by abnormal genes", "explanation": "Examples: cystic fibrosis, sickle cell anemia."},
       {"question": "What is a virus?", "answer": "Nonliving infectious agent", "explanation": "Needs a host cell to reproduce."},
       {"question": "What is a bacteria?", "answer": "Single-celled microorganism", "explanation": "Can be helpful or harmful."},
       {"question": "What is a fungus?", "answer": "Organism like molds, yeasts, mushrooms", "explanation": "Absorbs nutrients from environment."},
       {"question": "What is a plant?", "answer": "Multicellular organism that does photosynthesis", "explanation": "Includes trees, grasses, flowers."},
       {"question": "What is an animal?", "answer": "Multicellular, eukaryotic organism that can move", "explanation": "Includes mammals, birds, fish, insects, and more."}
   ],
   "geography": [
       {"question": "What is a map scale?", "answer": "Ratio of map distance to real distance", "explanation": "Shows how much the real world has been reduced."},
       {"question": "What is a geographical feature?", "answer": "Natural or artificial object on Earth's surface", "explanation": "Examples: mountains, rivers, buildings."},
       {"question": "What is a climate zone?", "answer": "Region with similar weather patterns", "explanation": "Examples: tropical, temperate, polar."},
       {"question": "What is a natural resource?", "answer": "Material found in nature used by humans", "explanation": "Examples: water, wood, minerals."},
       {"question": "What is a population density?", "answer": "Number of people per unit area", "explanation": "Usually measured as people per square kilometer."},
       {"question": "What is an urban area?", "answer": "City or town with dense population", "explanation": "Opposite of rural areas."},
       {"question": "What is a rural area?", "answer": "Countryside with low population density", "explanation": "Often used for farming or nature."},
       {"question": "What is a country?", "answer": "A nation with its own government and borders", "explanation": "Examples: Brazil, Canada, Japan."},
       {"question": "What is a continent?", "answer": "Large continuous mass of land", "explanation": "There are seven continents on Earth."},
       {"question": "What is a mountain range?", "answer": "Group of connected mountains", "explanation": "Examples: the Andes, the Himalayas."},
       {"question": "What is a river?", "answer": "Large natural stream of water", "explanation": "Flows toward an ocean, sea, or lake."},
       {"question": "What is a desert?", "answer": "Arid region with little rainfall", "explanation": "Examples: Sahara, Gobi, Atacama."},
       {"question": "What is a forest?", "answer": "Large area covered by trees", "explanation": "Examples: Amazon Rainforest, Taiga."},
       {"question": "What is a tundra?", "answer": "Cold, treeless region", "explanation": "Found in Arctic and high mountain areas."},
       {"question": "What is a geographical coordinate?", "answer": "A point's latitude and longitude", "explanation": "Used to locate places on a map."}
   ]


   }
   category = request.args.get("set") or request.form.get("set") or "math"
   questions = sets[category]
   qidx = random.randint(0, len(questions)-1)
   question = questions[qidx]
   explanation = question.get("explanation", "")
   feedback = None
   correct = None
   user_answer = ""
   show_next = False


   if request.method == "POST" and request.form.get("answer") is not None:
       user_answer = request.form.get("answer").strip()
       real_answer = question["answer"]
       if user_answer.lower() == real_answer.lower():
           feedback = "Correct! 🎉"
           correct = True
           show_next = True
       else:
           feedback = f"Incorrect. <b>Explanation:</b> {explanation}"
           correct = False
           show_next = False


   return render_template("flashcards.html",
       sets=sets.keys(),
       chosen=category,
       question=question,
       feedback=feedback,
       correct=correct,
       user_answer=user_answer,
       show_next=show_next
   )


@app.route("/quizquest")
def quizquest():
   return render_template("quiz_quest.html")


@app.route("/videos")
def videos():
   tutorial_videos = [
       {
           "title": "Algebra Basics",
           "subject": "math",
           "embed": "https://www.youtube.com/embed/NybHckSEQBI",
           "desc": "A simple intro to algebra."
       },
       {
           "title": "Introduction to Cells",
           "subject": "science",
           "embed": "https://www.youtube.com/embed/8IlzKri08kk",
           "desc": "Cells explained by Amoeba Sisters."
       },
       {
           "title": "The American Revolution",
           "subject": "history",
           "embed": "https://www.youtube.com/embed/gzALIXcY4pg",
           "desc": "History: American Revolution."
       },
       {
           "title": "Essay Writing Tips",
           "subject": "english",
           "embed": "https://www.youtube.com/embed/UuOWNNvupik",
           "desc": "Essay writing tips."
       }
   ]
   return render_template("videos.html", videos=tutorial_videos)


# --- AngleAlchemy Game Data ---
LOCATIONS = [
   {"name": "Grammar Ghoul Forest", "monster": "Grammar Ghoul", "icon": "👻", "subject": "english"},
   {"name": "Math Mountain", "monster": "Math Monster", "icon": "👾", "subject": "math"},
   {"name": "Science Swamp", "monster": "Evil Scientist", "icon": "🧪", "subject": "science"},
   {"name": "History Hall", "monster": "History Eraser", "icon": "👹", "subject": "history"},
   {"name": "City of Scholars", "monster": "Spellbound Scribe", "icon": "🧙", "subject": "english"},
]


QUESTIONS = {
"english": [
    {"q": "What is a simile?", "a": ["A comparison using 'like' or 'as'", "A metaphor", "A noun"], "correct": "A comparison using 'like' or 'as'"},
    {"q": "Which is a noun?", "a": ["Run", "Apple", "Quickly"], "correct": "Apple"},
    {"q": "Who wrote 'Romeo and Juliet'?", "a": ["Dickens", "Shakespeare", "Austen"], "correct": "Shakespeare"},
    {"q": "What is the plural of 'child'?", "a": ["Childs", "Childes", "Children"], "correct": "Children"},
    {"q": "Which is a synonym for 'happy'?", "a": ["Sad", "Joyful", "Angry"], "correct": "Joyful"},
    ],
   "math": [
    {"q": "What is 8 x 6?", "a": ["42", "48", "54"], "correct": "48"},
    {"q": "What is the value of pi (to 2 decimals)?", "a": ["3.12", "3.14", "3.16"], "correct": "3.14"},
    {"q": "Solve for x: 2x + 4 = 10", "a": ["2", "3", "4"], "correct": "3"},
    {"q": "What is the square root of 81?", "a": ["7", "8", "9"], "correct": "9"},
    {"q": "What is the area of a circle with radius 3?", "a": ["9π", "6π", "3π"], "correct": "9π"},
    {"q": "What is 15% of 60?", "a": ["6", "9", "12"], "correct": "9"},
    ],
"science": [
    {"q": "What is photosynthesis?", "a": ["Making food using sunlight", "Cell division", "Breathing"], "correct": "Making food using sunlight"},
    {"q": "Define mitosis.", "a": ["Cell division", "Energy production", "Protein synthesis"], "correct": "Cell division"},
    {"q": "What is the largest planet in our solar system?", "a": ["Jupiter", "Saturn", "Earth"], "correct": "Jupiter"},
    {"q": "What is Newton's first law?", "a": ["Objects in motion stay in motion", "Force = mass x acceleration", "Action = reaction"], "correct": "Objects in motion stay in motion"},
    {"q": "What is the chemical symbol for gold?", "a": ["Au", "Ag", "Fe"], "correct": "Au"},
    {"q": "H2O is the chemical formula for?", "a": ["Hydrogen", "Oxygen", "Water"], "correct": "Water"},
    {"q": "What is the center of an atom called?", "a": ["Nucleus", "Electron", "Proton"], "correct": "Nucleus"},
    {"q": "What is DNA?", "a": ["Genetic material", "A protein", "A sugar"], "correct": "Genetic material"},
    {"q": "Which is NOT a state of matter?", "a": ["Solid", "Liquid", "Light"], "correct": "Light"},
    {"q": "Which organ pumps blood?", "a": ["Heart", "Lung", "Kidney"], "correct": "Heart"},
    {"q": "What organelle is the powerhouse of the cell?", "a": ["Nucleus", "Mitochondria", "Chloroplast"], "correct": "Mitochondria"},
    {"q": "Which planet is called the Red Planet?", "a": ["Mars", "Venus", "Jupiter"], "correct": "Mars"},
    {"q": "The process of liquid water becoming vapor is called?", "a": ["Condensation", "Evaporation", "Freezing"], "correct": "Evaporation"},
    {"q": "Which of these is a renewable energy source?", "a": ["Coal", "Solar", "Oil"], "correct": "Solar"},
    {"q": "What is biodiversity?", "a": ["Variety of life", "Food chain", "One species"], "correct": "Variety of life"}
],

"history": [
    {"q": "Who was the first US President?", "a": ["Lincoln", "Washington", "Jefferson"], "correct": "Washington"},
    {"q": "In what year did WW2 end?", "a": ["1945", "1939", "1918"], "correct": "1945"},
    {"q": "What was the Treaty of Versailles?", "a": ["Ended WWI", "Started WWII", "Created NATO"], "correct": "Ended WWI"},
    {"q": "Who was Cleopatra?", "a": ["Queen of Egypt", "Roman Emperor", "Greek Philosopher"], "correct": "Queen of Egypt"},
    {"q": "What was the Renaissance?", "a": ["Cultural rebirth", "A war", "A disease"], "correct": "Cultural rebirth"},
    {"q": "Who was Martin Luther King Jr.?", "a": ["Civil rights leader", "US President", "Inventor"], "correct": "Civil rights leader"},
    {"q": "What year did World War I start?", "a": ["1900", "1914", "1939"], "correct": "1914"},
    {"q": "What was the Industrial Revolution?", "a": ["Era of machines", "Civil war", "Discovery of America"], "correct": "Era of machines"},
    {"q": "What was the Magna Carta?", "a": ["Limited king's power", "Declaration of Independence", "Bill of Rights"], "correct": "Limited king's power"},
    {"q": "Who was Napoleon Bonaparte?", "a": ["French leader", "German king", "Russian czar"], "correct": "French leader"},
    {"q": "What was the Cold War?", "a": ["US vs Soviet tension", "Civil war", "World War"], "correct": "US vs Soviet tension"},
    {"q": "What was the Berlin Wall?", "a": ["Divided Berlin", "River", "Palace"], "correct": "Divided Berlin"},
    {"q": "Who was Rosa Parks?", "a": ["Civil rights activist", "Queen", "Scientist"], "correct": "Civil rights activist"},
    {"q": "What was the Great Depression?", "a": ["Economic downturn", "Natural disaster", "War"], "correct": "Economic downturn"},
    {"q": "What was the impact of the printing press?", "a": ["Spread information", "Invented TV", "Started a war"], "correct": "Spread information"}
    ],
}


@app.route("/anglealchemy")
def anglealchemy():
   if not session.get("user_id"):
       return redirect("/login")
   coins = session.get("aa_coins", 0)
   badges = session.get("aa_badges", [])
   story = session.get("aa_story", [])
   return render_template("anglealchemy_map.html", locations=LOCATIONS, coins=coins, badges=badges, story=story)


@app.route("/anglealchemy/battle", methods=["GET", "POST"])
def anglealchemy_battle():
   if not session.get("user_id"):
       return redirect("/login")
   location_name = request.args.get("location")
   location = next((loc for loc in LOCATIONS if loc["name"] == location_name), None)
   if not location:
       return redirect(url_for('anglealchemy'))
   qlist = QUESTIONS[location["subject"]]
   question = random.choice(qlist)

   if request.method == "POST":
       selected = request.form.get("answer")
       correct = request.form.get("correct")
       coins = session.get("aa_coins", 0)
       badges = session.get("aa_badges", [])
       story = session.get("aa_story", [])
       message = ""
       if selected == correct:
           message = f"🎉 Correct! You defeated the {location['monster']} and earned a coin."
           coins += 1
           if location["monster"] not in badges:
               badges.append(location["monster"])
           story.append(f"Defeated {location['monster']} at {location['name']}!")
       else:
           message = f"😢 Incorrect. The correct answer was '{correct}'."
       session["aa_coins"] = coins
       session["aa_badges"] = badges
       session["aa_story"] = story
       return render_template("anglealchemy_battle.html", location=location,
                              question=question, answered=True, message=message, coins=coins, badges=badges)
   return render_template("anglealchemy_battle.html", location=location, question=question, answered=False)


@app.route("/anglealchemy/reset")
def anglealchemy_reset():
   session["aa_coins"] = 0
   session["aa_badges"] = []
   session["aa_story"] = []
   return redirect(url_for('anglealchemy'))


@app.route("/groups")
def groups():
   if not session.get("user_id"):
       return redirect("/login")
   user_id = session["user_id"]
   all_groups = db.execute("SELECT * FROM study_groups")
   user_groups = db.execute("""
       SELECT study_groups.* FROM study_groups
       JOIN group_members ON study_groups.id = group_members.group_id
       WHERE group_members.user_id = ?
   """, user_id)
   return render_template("groups.html", all_groups=all_groups, user_groups=user_groups)


@app.route("/create_group", methods=["GET", "POST"])
def create_group():
   if not session.get("user_id"):
       return redirect("/login")
   if request.method == "GET":
       return render_template("create_group.html")
   name = request.form.get("name")
   description = request.form.get("description")
   if not name:
       return apology("must provide a group name")
   group_id = db.execute(
       "INSERT INTO study_groups (name, description) VALUES (?, ?)", name, description
   )
   db.execute(
       "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", group_id, session["user_id"]
   )
   flash("Group created and joined!")
   return redirect("/groups")


@app.route("/join_group", methods=["POST"])
def join_group():
   if not session.get("user_id"):
       return redirect("/login")
   group_id = request.form.get("group_id")
   if not group_id:
       return apology("must select a group")
   try:
       db.execute(
           "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", group_id, session["user_id"]
       )
   except Exception:
       flash("You already joined this group!")
   else:
       flash("Joined group!")
   return redirect("/groups")


@app.route("/group/<int:group_id>", methods=["GET", "POST"])
def group(group_id):
   if not session.get("user_id"):
       return redirect("/login")
   user_id = session["user_id"]
   is_member = db.execute(
       "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?", group_id, user_id
   )
   if not is_member:
       flash("Join the group to participate!")
       return redirect("/groups")
   group = db.execute("SELECT * FROM study_groups WHERE id = ?", group_id)
   if not group:
       return apology("Group not found.")


   # Handle new chat message and file upload
   if request.method == "POST":
       if "content" in request.form or "media" in request.files:
           content = request.form.get("content")
           file = request.files.get("media")
           media_url = None
           if file and file.filename:
               filename = secure_filename(file.filename)
               filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
               file.save(filepath)
               media_url = f"/static/uploads/{filename}"
           if content or media_url:
               db.execute(
                   "INSERT INTO group_posts (group_id, user_id, content, media_url) VALUES (?, ?, ?, ?)",
                   group_id, user_id, content or "", media_url
               )
               flash("Message posted!")
               return redirect(f"/group/{group_id}")
       elif "event_title" in request.form:
           title = request.form.get("event_title")
           event_datetime = request.form.get("event_datetime")
           description = request.form.get("event_description")
           if title and event_datetime:
               db.execute(
                   "INSERT INTO events (group_id, title, event_datetime, description) VALUES (?, ?, ?, ?)",
                   group_id, title, event_datetime, description
               )
               flash("Event created!")
               return redirect(f"/group/{group_id}")


   messages = db.execute("""
       SELECT group_posts.content, group_posts.media_url, group_posts.created_at, users.username
       FROM group_posts
       JOIN users ON group_posts.user_id = users.id
       WHERE group_posts.group_id = ?
       ORDER BY group_posts.created_at DESC
   """, group_id)
   group_events = db.execute("SELECT * FROM events WHERE group_id = ? ORDER BY event_datetime", group_id)
   user_groups = db.execute("""
       SELECT study_groups.* FROM study_groups
       JOIN group_members ON study_groups.id = group_members.group_id
       WHERE group_members.user_id = ?
   """, user_id)
   return render_template(
       "group.html",
       user_groups=user_groups,
       active_group=group[0],
       messages=messages,
       group_events=group_events
   )


def apology(message):
   return render_template("apology.html", message=message)



if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
# Ensure static files are served correctly
@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    return send_from_directory('static', filename)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
