from browser import open_tabs
from apps import open_teams
from config import WORK_TABS

def main() -> None:
    open_tabs(WORK_TABS)
    open_teams()

if __name__ == "__main__":
    main()