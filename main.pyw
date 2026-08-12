from browser import open_tabs
from apps import open_teams, open_portfolio_dashboard
from config import WORK_TABS

def main() -> None:
    #open_tabs(WORK_TABS)
    open_teams()
    open_portfolio_dashboard()

if __name__ == "__main__":
    main()