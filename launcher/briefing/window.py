"""Shows rendered HTML in a small native window.

Opens immediately with a loading state, then fills in once build_html()
returns — so the window doesn't sit invisible while data is still being
fetched. Since the window is frameless (no OS title bar), a close button
is exposed to the page via pywebview's JS API instead.

pip install pywebview
"""
from __future__ import annotations

from typing import Callable

import webview

_LOADING_HTML = """
<html><head><meta charset="utf-8"><style>
  body { background: #1e1e2e; color: #8888a0; font-family: 'Segoe UI', sans-serif;
         display: flex; align-items: center; justify-content: center;
         height: 100vh; margin: 0; font-size: 14px; }
</style></head><body>Loading your briefing…</body></html>
"""


class _WindowApi:
    """Exposed to the page as `pywebview.api.*` — lets the HTML's close
    button actually close the (frameless, X-less) window.
    """

    def __init__(self) -> None:
        self._window: webview.Window | None = None

    def bind(self, window: webview.Window) -> None:
        self._window = window

    def close(self) -> None:
        if self._window is not None:
            self._window.destroy()


def show(build_html: Callable[[], str], width: int = 480, height: int = 640) -> None:
    api = _WindowApi()
    window = webview.create_window(
        title="Morning Briefing",
        html=_LOADING_HTML,
        width=width,
        height=height,
        frameless=True,
        on_top=True,
        easy_drag=True,
        js_api=api,
    )
    api.bind(window)

    def _load_content() -> None:
        # Runs in a background thread once the GUI loop has started, so the
        # window is already visible while build_html() does its network I/O.
        html = build_html()
        window.load_html(html)

    webview.start(_load_content)