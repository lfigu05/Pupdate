# Pupdate 🐶

*your very own pup that grows when you study/complete a task every day!*

Built solo at ShellHacks 2026.

## 🐾 Why I Built It
I built Pupdate because I know what it's like to cram last minute and how overwhelming that can be. I crammed for my Operating Systems quiz in one day, and I learned that how I studied wasn't the problem. The problem was when. Pupdate takes the weight off your shoulders by splitting big deadlines into small daily tasks. To keep you motivated, the pup grows every day you show up, whether it's by completing a study task or an everyday habit.

## 🦴 Features
- ✅ Habits & daily check-ins
- 🎓 Pup grows and has new accessory each time (puppy → bandana → graduation cap)
- 💤 Sleepy mode with no guilt
- 📚 Gemini study plans
- 📝 To-do and Completed tabs (with undo)
- 🔒 Accounts with private data
- 🎨 Hand-drawn art
    - Pup art in Sketchbook
    - Icons in Notability: home, plan, logout, done, delete, undo, add

## 🐾 Tech Stack
- Python, Django, SQLite
- Google Gemini API
- HTML, CSS, JavaScript
- Art and icons hand-drawn in Sketchbook/Notability

## 🦴 Running it Locally
```bash
git clone https://github.com/lfigu05/Pupdate.git
cd Pupdate
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file next to `manage.py` with your Gemini API key:
```
GEMINI_API_KEY=your-key-here
```

Then set up the database and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## 🤖 How I used AI

### In the app (Gemini):
- The Gemini API turns a deadline into daily study steps
- Pupdate asks Gemini for JSON, then validates each step (bad dates or steps past deadline are thrown out)
- Retries with backoff handle moments when Gemini is overloaded
- NO CHATBOT: The user fills out a form and the output becomes checklist items
### While building (Claude):
- Helped write and explain the Django views, templates, and CSS. Concepts were explained as I went.
- **What I did:** The idea and design, the database models, all the art, the product decisions, and testing and debugging

## What's Next
- Daily reminders with today's study step
- Canvas sync, so study plans are created from real due dates
- Upload lecture PDFs so Gemini can plan from your actual course material


