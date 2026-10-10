from pyui import State, render_body
import quiz_app as q

s = State(**q.initial_state())
html, h = render_body(q.view, s)
assert "Start Quiz" in html
h["e1"](s)                                   # click Start
html, h = render_body(q.view, s); assert "Question 1 / 5" in html
h["e2"](s)                                   # click option index 1 (correct)
assert s.score == 1 and s.dirty
html, h = render_body(q.view, s); assert "Correct!" in html
for _ in range(4):
    next_id = [k for k in h][-1]; h[next_id](s)
    html, h = render_body(q.view, s)
    if s.screen == "quiz": h["e1"](s); html, h = render_body(q.view, s)
print("OK, screen:", s.screen, "score:", s.score)
assert "<script" not in html and "<b>" not in render_body(lambda s: __import__("pyui").p("<b>x</b>"), s)[0]
print("escaping OK")
