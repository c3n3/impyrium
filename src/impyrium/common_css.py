
MAIN_COLOR = "#1E1E21"
ACCENT_COLOR = "#404052"
MAIN_TEXT_COLOR = "#EDEAFF"
FOCUS_MAIN_COLOR = "#385B66"
FOCUS_ACCENT_COLOR = "#567F8D"
FOCUS_TEXT_COLOR = "#F5E5C9"
MAIN_STYLE = f"""
QWidget {{ background-color: {MAIN_COLOR}; color: {MAIN_TEXT_COLOR} }}
"""
TAB_STYLE = f"""
QTabBar::tab:selected {{background-color: {ACCENT_COLOR}; }}
QTabBar::tab {{background-color: {MAIN_COLOR}; }}
QTabWidget>QWidget>QWidget{{ background: gray; }}
QTabWidget::pane {{ border-top: 2px solid {ACCENT_COLOR}; }}
"""
