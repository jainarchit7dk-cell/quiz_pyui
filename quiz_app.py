"""Quiz app built ONLY with the pyui framework.  Run:  python quiz_app.py"""
from pyui import App, div, h1, h2, p, button, span, strong, section

QUESTIONS = [
    {"q": "Which language is used to build this app's UI framework?",
     "options": ["JavaScript", "Python", "CSS", "SQL"], "answer": 1},
    {"q": "What does HTTP status 404 mean?",
     "options": ["Server error", "Forbidden", "Not found", "OK"], "answer": 2},
    {"q": "Which data structure works as Last-In, First-Out (LIFO)?",
     "options": ["Queue", "Stack", "Heap", "Graph"], "answer": 1},
    {"q": "What does HTML stand for?",
     "options": ["HyperText Markup Language", "High Transfer Machine Language",
                 "HyperTool Multi Language", "Home Text Markup Level"], "answer": 0},
    {"q": "Which of these is NOT a programming paradigm?",
     "options": ["Functional", "Object-oriented", "Procedural", "Tabular"], "answer": 3},
]
LETTERS = "ABCD"

# ---------- STATE ----------
def initial_state():
    return dict(screen="start", index=0, selected=None, score=0, results=[])

# ---------- EVENT HANDLERS (each changes state; UI then re-renders) ----------
def start(s):
    s.screen, s.index, s.selected, s.score, s.results = "quiz", 0, None, 0, []

def choose(i):
    def handler(s):
        if s.selected is None:                      # ignore double answers
            correct = i == QUESTIONS[s.index]["answer"]
            s.selected = i
            s.results = s.results + [correct]       # new list -> state marked changed
            if correct:
                s.score += 1
    return handler

def next_question(s):
    if s.index + 1 < len(QUESTIONS):
        s.index, s.selected = s.index + 1, None
    else:
        s.screen = "result"

# ---------- COMPONENTS (functions returning element trees) ----------
def Dots(results, current):
    """One dot per question: green = right, red = wrong, ringed = current."""
    dots = []
    for i in range(len(QUESTIONS)):
        cls = "dot"
        if i < len(results):
            cls += " ok" if results[i] else " bad"
        elif i == current:
            cls += " now"
        dots.append(span(class_=cls))
    return div(dots, class_="dots")

def Option(text, i, selected, correct):
    cls, mark = "opt", ""
    if selected is not None:
        if i == correct:
            cls, mark = cls + " right", "✓"
        elif i == selected:
            cls, mark = cls + " wrong", "✕"
    return button(span(LETTERS[i], class_="letter"), span(text, class_="txt"),
                  span(mark, class_="mark"),
                  class_=cls, on_click=choose(i), disabled=selected is not None)

def Chip(text):
    return span(text, class_="chip")

def StartScreen(s):
    return section(
        div("🧠", class_="logo"),
        h1("Quick Quiz"),
        p("Test your tech knowledge. Pick the best answer and see instantly if you got it right.",
          class_="sub"),
        div(Chip(f"{len(QUESTIONS)} questions"), Chip("Instant feedback"), Chip("No timer"),
            class_="chips"),
        button("Start Quiz  →", class_="primary", on_click=start),
        class_="center")

def QuizScreen(s):
    q = QUESTIONS[s.index]
    answered = s.selected is not None
    ok = answered and s.selected == q["answer"]
    return section(
        div(Chip(f"Question {s.index + 1} of {len(QUESTIONS)}"),
            Chip(f"⭐ {s.score}"), class_="meta"),
        Dots(s.results, s.index),
        h2(q["q"]),
        div([Option(t, i, s.selected, q["answer"]) for i, t in enumerate(q["options"])],
            class_="options"),
        answered and div("🎉 Correct!" if ok else "😅 Not quite — the right answer is highlighted.",
                         class_="feedback good" if ok else "feedback bad"),
        answered and button("Next question  →" if s.index + 1 < len(QUESTIONS) else "See my result  →",
                            class_="primary", on_click=next_question))

def ResultScreen(s):
    total = len(QUESTIONS)
    pct = round(s.score / total * 100)
    title, msg = (("Perfect score!", "Flawless. You nailed every question. 🏆") if s.score == total else
                  ("Great job!", "Solid result — you know your stuff. 👍") if s.score >= total / 2 else
                  ("Keep going!", "Practice makes perfect. Try again! 💪"))
    return section(
        div(div(strong(f"{pct}%"), span(f"{s.score} / {total} correct"), class_="ring-in"),
            class_="ring", style=f"--p:{pct}"),
        h1(title),
        p(msg, class_="sub"),
        Dots(s.results, -1),
        button("↻  Play again", class_="primary", on_click=start),
        class_="center")

def view(s):
    screen = {"start": StartScreen, "quiz": QuizScreen, "result": ResultScreen}[s.screen]
    return div(screen(s), class_="card")

CSS = """
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:18px;color:#1e1b4b;
font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
background:linear-gradient(120deg,#4f46e5,#9333ea,#ec4899,#4f46e5);background-size:300% 300%;
animation:bg 14s ease infinite}
@keyframes bg{0%{background-position:0 50%}50%{background-position:100% 50%}100%{background-position:0 50%}}
form{width:100%;display:grid;place-items:center}
.card{width:100%;max-width:560px;padding:34px 30px;border-radius:26px;background:rgba(255,255,255,.95);
box-shadow:0 30px 70px rgba(30,10,80,.35),0 0 0 1px rgba(255,255,255,.6) inset}
.center{text-align:center}
.logo{font-size:56px;width:96px;height:96px;margin:0 auto 14px;display:grid;place-items:center;
border-radius:28px;background:linear-gradient(135deg,#eef2ff,#fae8ff);box-shadow:0 10px 24px rgba(99,102,241,.25)}
h1{margin:0 0 8px;font-size:34px;letter-spacing:-.5px;
background:linear-gradient(90deg,#4f46e5,#c026d3);-webkit-background-clip:text;background-clip:text;color:transparent}
h2{margin:18px 0 18px;font-size:22px;line-height:1.35}
.sub{color:#6b7280;margin:0 0 20px;line-height:1.5}
.chips,.meta{display:flex;gap:8px;flex-wrap:wrap}.chips{justify-content:center;margin-bottom:26px}
.meta{justify-content:space-between}
.chip{background:#eef2ff;color:#4338ca;font-size:13px;font-weight:600;padding:6px 12px;border-radius:99px}
.dots{display:flex;gap:8px;justify-content:center;margin:16px 0 4px}
.dot{width:12px;height:12px;border-radius:50%;background:#e5e7eb;transition:.3s}
.dot.now{background:#fff;box-shadow:0 0 0 3px #6366f1}
.dot.ok{background:#22c55e}.dot.bad{background:#ef4444}
.options{display:grid;gap:11px;margin-bottom:16px}
button{font:inherit;cursor:pointer;border:0}
.opt{display:flex;align-items:center;gap:14px;text-align:left;padding:12px 14px;border-radius:16px;
background:#fff;border:2px solid #e5e7eb;color:inherit;transition:transform .15s,border-color .15s,box-shadow .15s}
.opt:hover:not(:disabled){transform:translateY(-2px);border-color:#818cf8;box-shadow:0 8px 20px rgba(99,102,241,.2)}
.opt:disabled{cursor:default}
.letter{flex:none;width:34px;height:34px;display:grid;place-items:center;border-radius:10px;
background:#eef2ff;color:#4f46e5;font-weight:700}
.txt{flex:1}.mark{font-weight:800;font-size:18px}
.opt.right{background:#f0fdf4;border-color:#22c55e;animation:pop .35s}
.opt.right .letter{background:#22c55e;color:#fff}.opt.right .mark{color:#16a34a}
.opt.wrong{background:#fef2f2;border-color:#ef4444;animation:shake .35s}
.opt.wrong .letter{background:#ef4444;color:#fff}.opt.wrong .mark{color:#dc2626}
@keyframes pop{50%{transform:scale(1.03)}}
@keyframes shake{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
.feedback{padding:11px 14px;border-radius:12px;font-weight:600;margin-bottom:14px}
.feedback.good{background:#dcfce7;color:#166534}.feedback.bad{background:#fee2e2;color:#991b1b}
.primary{width:100%;padding:14px;border-radius:16px;color:#fff;font-weight:700;font-size:16px;
background:linear-gradient(90deg,#4f46e5,#9333ea);box-shadow:0 10px 24px rgba(99,102,241,.4);transition:.15s}
.primary:hover{transform:translateY(-2px);box-shadow:0 14px 30px rgba(99,102,241,.5)}
.ring{--p:0;width:170px;height:170px;margin:0 auto 18px;border-radius:50%;display:grid;place-items:center;
background:conic-gradient(#6366f1 calc(var(--p)*1%),#e5e7eb 0);animation:pop .6s}
.ring-in{width:138px;height:138px;border-radius:50%;background:#fff;display:flex;flex-direction:column;
align-items:center;justify-content:center}
.ring-in strong{font-size:38px;color:#4f46e5}.ring-in span{font-size:13px;color:#6b7280}
.result .dots{margin-bottom:22px}
section.center .dots{margin-bottom:22px}
"""

app = App(view, initial_state, title="Quick Quiz", css=CSS)

if __name__ == "__main__":
    app.run()
