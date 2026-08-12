import webbrowser


def open_tabs(urls: list[str]) -> None:
    for url in urls:
        webbrowser.open_new_tab(url)