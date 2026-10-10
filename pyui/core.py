"""pyui core: element tree, state, and HTML renderer.

1. COMPONENTS : plain functions that return an Element tree (tag + props + children).
2. RENDERER   : walks the tree and produces an HTML string.
3. STATE      : an object that remembers when it was changed.
4. EVENTS     : on_click handlers get an id during render; the browser sends that id
               back on click, and we look the handler up and call it.
"""
from html import escape

VOID_TAGS = {"br", "hr", "img", "input", "meta", "link"}


class Element:
    """One node of the UI tree: a tag, its props (attributes), and its children."""
    def __init__(self, tag, props=None, children=None):
        self.tag = tag
        self.props = props or {}
        self.children = children or []


def _flatten(items):
    for item in items:
        if isinstance(item, (list, tuple)):
            yield from _flatten(item)
        elif item is None or item is False:
            continue                      # lets you write `cond and element`
        else:
            yield item


def el(tag, *children, **props):
    """Create an Element. Example: el("div", "hello", class_="box")"""
    return Element(tag, props, list(_flatten(children)))


def _make(tag):
    def factory(*children, **props):
        return el(tag, *children, **props)
    factory.__name__ = tag
    return factory


div, span, h1, h2, h3, p = map(_make, ["div", "span", "h1", "h2", "h3", "p"])
button, ul, li, section = map(_make, ["button", "ul", "li", "section"])
header, footer, strong, br = map(_make, ["header", "footer", "strong", "br"])


class State:
    """Holds app data. Setting any attribute marks the state as changed."""
    def __init__(self, **initial):
        object.__setattr__(self, "_data", dict(initial))
        object.__setattr__(self, "dirty", False)

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self._data[name] = value
        object.__setattr__(self, "dirty", True)


class _Renderer:
    def __init__(self):
        self.handlers = {}   # event id -> function(state)
        self._count = 0

    def _attrs(self, props):
        out = []
        for key, val in props.items():
            if key == "on_click":
                self._count += 1
                event_id = f"e{self._count}"      # deterministic: same tree -> same ids
                self.handlers[event_id] = val
                out.append(f' type="submit" name="evt" value="{event_id}"')
                continue
            name = key.rstrip("_").replace("_", "-")   # class_ -> class, data_x -> data-x
            if val is True:
                out.append(f" {name}")
            elif val is False or val is None:
                continue
            else:
                out.append(f' {name}="{escape(str(val), quote=True)}"')
        return "".join(out)

    def render(self, node):
        if isinstance(node, Element):
            attrs = self._attrs(node.props)
            if node.tag in VOID_TAGS:
                return f"<{node.tag}{attrs}>"
            inner = "".join(self.render(c) for c in node.children)
            return f"<{node.tag}{attrs}>{inner}</{node.tag}>"
        return escape(str(node))                   # text is always escaped (no XSS)


def render_body(view, state):
    """Run the view on the current state -> (html string, event handlers)."""
    r = _Renderer()
    html = r.render(view(state))
    return html, r.handlers


def render_page(body, title="PyUI App", css=""):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title><style>{css}</style></head><body>'
            f'<form method="post" action="/">{body}</form></body></html>')
