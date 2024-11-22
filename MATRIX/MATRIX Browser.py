import sys
from datetime import datetime
from PyQt5.QtCore import Qt, QUrl, QTimer, QPropertyAnimation, QRect, QSize, QEasingCurve, QTime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QTabWidget,
    QLabel, QWidget, QListWidget, QShortcut, QPushButton, QFrame, QDialog, QTimeEdit
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QKeySequence, QIcon, QFont, QPalette, QColor
from PyQt5.QtMultimedia import QSound

class ClockWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.use_24hr = True
        self.alarms = []
        try:
            with open('matrix_alarms.txt', 'r') as f:
                for line in f:
                    time = QTime.fromString(line.strip(), "HH:mm")
                    if time.isValid():
                        self.alarms.append(time)
        except FileNotFoundError:
            pass
            
        self.setStyleSheet("""
            QLabel {
                color: #00ff00;
                background-color: #001100;
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Courier New';
                font-size: 14px;
            }
            QLabel:hover {
                background-color: #002200;
            }
        """)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Left-click: Toggle 12/24 hour format\nRight-click: Set alarm")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.use_24hr = not self.use_24hr
            self.update_time()
        elif event.button() == Qt.RightButton:
            self.show_alarm_dialog()

    def show_alarm_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set Alarm")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #001100;
                color: #00ff00;
            }
            QTimeEdit {
                background-color: #002200;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
            }
            QPushButton {
                background-color: #003300;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                margin: 5px;
            }
            QLabel {
                color: #00ff00;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime.currentTime())
        set_button = QPushButton("Set Alarm")
        layout.addWidget(QLabel("Set alarm time:"))
        layout.addWidget(time_edit)
        layout.addWidget(set_button)
        dialog.setLayout(layout)
        
        def set_alarm():
            alarm_time = time_edit.time()
            self.alarms.append(alarm_time)
            with open('matrix_alarms.txt', 'a') as f:
                f.write(f"{alarm_time.toString('HH:mm')}\n")
            dialog.accept()
            self.parent().parent().show_notification(f"Alarm set for {alarm_time.toString('hh:mm')}")
        
        set_button.clicked.connect(set_alarm)
        dialog.exec_()

    def update_time(self):
        current_time = QTime.currentTime()
        
        # Check alarms
        for alarm_time in self.alarms[:]:
            if (current_time.hour() == alarm_time.hour() and 
                current_time.minute() == alarm_time.minute() and 
                current_time.second() == 0):
                QApplication.beep()
                self.parent().parent().show_notification("⏰ Alarm!")
                self.alarms.remove(alarm_time)
                with open('matrix_alarms.txt', 'w') as f:
                    for a in self.alarms:
                        f.write(f"{a.toString('HH:mm')}\n")
        
        if self.use_24hr:
            time_str = current_time.toString("HH:mm:ss")
        else:
            time_str = current_time.toString("hh:mm:ss AP")
        self.setText(time_str)

class AnimatedTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #00ff00;
                background: #000000;
            }
            QTabBar::tab {
                background: #001100;
                color: #00ff00;
                padding: 8px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #003300;
            }
        """)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(150)

    def setCurrentIndex(self, index):
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.7)
        self.fade_animation.start()
        super().setCurrentIndex(index)
        QTimer.singleShot(100, self.fade_back)

    def fade_back(self):
        self.fade_animation.setStartValue(0.7)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

class MatrixBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Matrix Browser')
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables first
        self.bookmark_list = None
        self.bookmarks = []
        self.sidebar_visible = False
        
        # Load bookmarks before UI initialization
        try:
            with open('matrix_bookmarks.txt', 'r') as f:
                self.bookmarks = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.bookmarks = [
                "https://www.google.com",
                "https://www.wikipedia.org",
                "https://www.github.com"
            ]
            with open('matrix_bookmarks.txt', 'w') as f:
                for bookmark in self.bookmarks:
                    f.write(f"{bookmark}\n")
        
        self.setup_styling()
        self.init_ui()
        self.setup_animations()
        self.show_welcome_message()
        self.show()

    def setup_styling(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #000000;
                color: #00ff00;
                font-family: 'Courier New';
            }
            QLineEdit, QListWidget {
                border: 1px solid #00ff00;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #001100;
                border: 1px solid #00ff00;
                border-radius: 3px;
                padding: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #002200;
            }
            QPushButton:pressed {
                background-color: #003300;
            }
            QLabel {
                color: #00ff00;
            }
        """)

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Top container
        self.top_container = QWidget()
        self.top_layout = QVBoxLayout(self.top_container)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Clock and controls
        self.controls_layout = QHBoxLayout()
        self.clock = ClockWidget()
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.clock)
        self.top_layout.addLayout(self.controls_layout)
        
        # Navigation
        self.nav_bar = self.create_nav_bar()
        self.top_layout.addLayout(self.nav_bar)
        self.main_layout.addWidget(self.top_container)
        
        # Content area
        self.content_layout = QHBoxLayout()
        self.main_layout.addLayout(self.content_layout)
        
        # Initialize bookmark list before sidebar setup
        self.bookmark_list = QListWidget()
        self.update_bookmarks()
        
        # Sidebar
        self.setup_sidebar()
        
        # Tabs
        self.tab_widget = AnimatedTabWidget(self)
        self.content_layout.addWidget(self.tab_widget)
        self.new_tab("https://www.google.com")
        
        # Command Bar
        self.setup_command_bar()
        
        # Shortcuts
        self.setup_shortcuts()

    def update_bookmarks(self):
        if self.bookmark_list:
            self.bookmark_list.clear()
            for bookmark in self.bookmarks:
                self.bookmark_list.addItem(bookmark)

    def create_nav_bar(self):
        nav_layout = QHBoxLayout()
        nav_buttons = {
            "←": self.navigate_back,
            "→": self.navigate_forward,
            "↻": self.reload_page,
            "⌂": lambda: self.navigate_to_url("https://www.google.com")
        }

        for text, func in nav_buttons.items():
            btn = QPushButton(text)
            btn.setFixedSize(QSize(30, 30))
            btn.clicked.connect(func)
            nav_layout.addWidget(btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search terms...")
        self.url_bar.returnPressed.connect(lambda: self.navigate_to_url())
        nav_layout.addWidget(self.url_bar)
        return nav_layout

    def setup_sidebar(self):
        self.sidebar = QWidget(self)
        self.sidebar.setFixedWidth(150)
        sidebar_layout = QVBoxLayout(self.sidebar)
        
        header = QLabel("⭐ Bookmarks")
        header.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(header)
        
        self.bookmark_list.itemClicked.connect(self.load_bookmark)
        sidebar_layout.addWidget(self.bookmark_list)
        
        self.content_layout.insertWidget(0, self.sidebar)
        self.sidebar.setGeometry(-150, 0, 150, self.height())

    def setup_animations(self):
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"geometry")
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.sidebar_animation.setDuration(300)

        self.command_bar_animation = QPropertyAnimation(self.command_bar, b"geometry")
        self.command_bar_animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.command_bar_animation.setDuration(300)

    def setup_command_bar(self):
        self.command_bar = QLineEdit(self)
        self.command_bar.setPlaceholderText("Type a command... (Alt+C to toggle)")
        self.command_bar.returnPressed.connect(self.execute_command)
        self.command_bar.setGeometry(0, self.height(), self.width(), 30)

    def setup_shortcuts(self):
        shortcuts = {
            "Alt+S": self.toggle_sidebar,
            "Alt+C": self.toggle_command_bar,
            "Ctrl+T": lambda: self.new_tab("https://www.google.com"),
            "Ctrl+W": self.close_current_tab,
            "Ctrl+R": self.reload_page,
            "Ctrl+B": lambda: self.add_bookmark(self.current_tab_url()),
            "Ctrl+H": self.toggle_history
        }

        for key, func in shortcuts.items():
            QShortcut(QKeySequence(key), self).activated.connect(func)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_animation.setEndValue(QRect(-150, 0, 150, self.height()))
        else:
            self.sidebar_animation.setEndValue(QRect(0, 0, 150, self.height()))
        self.sidebar_animation.start()
        self.sidebar_visible = not self.sidebar_visible

    def toggle_command_bar(self):
        if self.command_bar.isVisible():
            self.command_bar_animation.setEndValue(QRect(0, self.height(), self.width(), 30))
        else:
            self.command_bar_animation.setEndValue(QRect(0, self.height() - 30, self.width(), 30))
        self.command_bar.setVisible(not self.command_bar.isVisible())
        self.command_bar_animation.start()

    def new_tab(self, url):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        index = self.tab_widget.addTab(browser, "New Tab")
        self.tab_widget.setCurrentIndex(index)
        browser.urlChanged.connect(lambda qurl, browser=browser: 
            self.update_tab_title(browser))
        browser.urlChanged.connect(lambda qurl:
            self.url_bar.setText(qurl.toString()))

    def update_tab_title(self, browser):
        index = self.tab_widget.indexOf(browser)
        if index > -1:
            title = browser.page().title()
            self.tab_widget.setTabText(index, title[:15] + "..." if len(title) > 15 else title)

    def current_tab(self):
        return self.tab_widget.currentWidget()

    def navigate_back(self):
        if self.current_tab():
            self.current_tab().back()

    def navigate_forward(self):
        if self.current_tab():
            self.current_tab().forward()

    def reload_page(self):
        if self.current_tab():
            self.current_tab().reload()

    def navigate_to_url(self, url=None):
        if url is None:
            url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        if self.current_tab():
            self.current_tab().setUrl(QUrl(url))
            
    def add_bookmark(self, url):
        if url and url not in self.bookmarks:
            self.bookmarks.append(url)
            self.update_bookmarks()
            with open('matrix_bookmarks.txt', 'w') as f:
                for bookmark in self.bookmarks:
                    f.write(f"{bookmark}\n")
            self.show_notification(f"Bookmark added: {url}")

    def load_bookmark(self, item):
        url = item.text()
        self.navigate_to_url(url)

    def show_notification(self, message, duration=3000):
        notification = QLabel(message, self)
        notification.setStyleSheet("""
            QLabel {
                background-color: #003300;
                color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        notification.setAlignment(Qt.AlignCenter)
        notification.setFixedHeight(50)
        self.main_layout.addWidget(notification)
        QTimer.singleShot(duration, lambda: self.remove_notification(notification))

    def remove_notification(self, widget):
        self.main_layout.removeWidget(widget)
        widget.deleteLater()

    def show_welcome_message(self):
        self.show_notification("Welcome to Matrix Browser! Press Alt+C for commands.")

    def toggle_history(self):
        self.show_notification("History feature coming soon!")

    def execute_command(self):
        command = self.command_bar.text().strip().lower()
        commands = {
            "bookmark": lambda: self.add_bookmark(self.current_tab_url()),
            "reload": self.reload_page,
            "newtab": lambda: self.new_tab("https://www.google.com"),
            "closetab": self.close_current_tab,
            "togglesidebar": self.toggle_sidebar,
            "help": lambda: self.show_notification(
                "Commands: bookmark, reload, newtab, closetab, togglesidebar, help"
            )
        }
        
        if command in commands:
            commands[command]()
        else:
            self.show_notification(f"Unknown command: {command}")
        self.command_bar.clear()

    def close_current_tab(self):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(self.tab_widget.currentIndex())
        else:
            self.show_notification("Cannot close last tab!")

    def current_tab_url(self):
        if self.current_tab():
            return self.current_tab().url().toString()
        return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    browser = MatrixBrowser()
    sys.exit(app.exec_())