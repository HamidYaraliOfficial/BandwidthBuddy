import sys
import psutil
import time
import sqlite3
from datetime import datetime
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTableWidget, QTableWidgetItem, QPushButton, QComboBox, 
                             QTabWidget, QMenuBar, QMenu, QDialog, QFormLayout, QLineEdit, 
                             QSpinBox, QMessageBox, QToolBar, QDateEdit, QCheckBox, QLabel)
from PyQt6.QtCore import Qt, QTimer, QCoreApplication, QLocale, QTranslator, QDate
from PyQt6.QtGui import QAction, QActionGroup, QColor, QPalette, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import numpy as np
import qdarkstyle
from qdarkstyle import load_stylesheet
import os
from matplotlib.dates import DateFormatter

# Database setup
def init_db():
    conn = sqlite3.connect("bandwidth_buddy.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bandwidth_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT,
            download_bytes INTEGER,
            upload_bytes INTEGER,
            timestamp DATETIME
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_limits (
            app_name TEXT PRIMARY KEY,
            max_download_kbps INTEGER,
            max_upload_kbps INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Translator for multi-language support
class Translator:
    def __init__(self):
        self.translators = {
            "en": QTranslator(),
            "fa": QTranslator(),
            "zh": QTranslator()
        }

    def load_language(self, app, language):
        if language == "fa":
            app.installTranslator(self.translators["fa"])
            QLocale.setDefault(QLocale(QLocale.Language.Persian))
        elif language == "zh":
            app.installTranslator(self.translators["zh"])
            QLocale.setDefault(QLocale(QLocale.Language.Chinese))
        else:
            app.installTranslator(self.translators["en"])
            QLocale.setDefault(QLocale(QLocale.Language.English))

# Theme manager
class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.themes = {
            "Windows 11": None,
            "Dark": None,
            "Light": None,
            "Red": None,
            "Blue": None
        }
        self.current_theme = "Windows 11"

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        if theme_name == "Dark":
            self.app.setStyleSheet(load_stylesheet())
        elif theme_name == "Light":
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            self.app.setStyleSheet("")
            self.app.setPalette(palette)
        elif theme_name == "Red":
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 235, 235))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(139, 0, 0))
            palette.setColor(QPalette.ColorRole.Button, QColor(255, 100, 100))
            self.app.setStyleSheet("QPushButton { background-color: #FF4040; color: white; }")
            self.app.setPalette(palette)
        elif theme_name == "Blue":
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(235, 235, 255))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 139))
            palette.setColor(QPalette.ColorRole.Button, QColor(100, 100, 255))
            self.app.setStyleSheet("QPushButton { background-color: #4040FF; color: white; }")
            self.app.setPalette(palette)
        else:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            self.app.setStyleSheet("")
            self.app.setPalette(palette)

# BandwidthBuddy Main Window
class BandwidthBuddy(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("BandwidthBuddy")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(QIcon("BandwidthBuddy.jpg"))
        self.theme_manager = ThemeManager(app)
        self.translator = Translator()
        self.init_db()
        self.init_ui()
        self.init_monitoring()
        self.previous_net_io = {}
        self.plot_data = {"times": [], "downloads": {}, "uploads": {}}

    def init_db(self):
        init_db()

    def init_ui(self):
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Tabs
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Real-time Monitoring Tab
        self.monitor_tab = QWidget()
        self.monitor_layout = QVBoxLayout(self.monitor_tab)
        self.tabs.addTab(self.monitor_tab, self.tr("Real-time Monitoring"))

        # Table for real-time data
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            self.tr("Application"),
            self.tr("Download (KB/s)"),
            self.tr("Upload (KB/s)"),
            self.tr("Total Download (MB)"),
            self.tr("Total Upload (MB)"),
            self.tr("Status")
        ])
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.monitor_layout.addWidget(self.table)

        # Plot controls
        self.plot_controls = QHBoxLayout()
        self.monitor_layout.addLayout(self.plot_controls)

        self.plot_type = QComboBox()
        self.plot_type.addItems([self.tr("Bar"), self.tr("Line"), self.tr("Pie"), self.tr("Area")])
        self.plot_type.currentIndexChanged.connect(self.update_plot)
        self.plot_controls.addWidget(QLabel(self.tr("Plot Type:")))
        self.plot_controls.addWidget(self.plot_type)

        self.time_range = QComboBox()
        self.time_range.addItems([self.tr("Last 10s"), self.tr("Last 1m"), self.tr("Last 5m"), self.tr("Last 1h")])
        self.time_range.currentIndexChanged.connect(self.update_plot)
        self.plot_controls.addWidget(QLabel(self.tr("Time Range:")))
        self.plot_controls.addWidget(self.time_range)

        # Plot for real-time data
        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        self.monitor_layout.addWidget(self.canvas)

        # Controls
        self.controls_layout = QHBoxLayout()
        self.monitor_layout.addLayout(self.controls_layout)

        self.view_mode = QComboBox()
        self.view_mode.addItems([self.tr("All Apps"), self.tr("Individual Apps")])
        self.view_mode.currentIndexChanged.connect(self.update_view)
        self.controls_layout.addWidget(QLabel(self.tr("View Mode:")))
        self.controls_layout.addWidget(self.view_mode)

        self.app_selector = QComboBox()
        self.app_selector.addItem(self.tr("Select App"))
        self.controls_layout.addWidget(QLabel(self.tr("Application:")))
        self.controls_layout.addWidget(self.app_selector)

        self.limit_button = QPushButton(self.tr("Set Bandwidth Limit"))
        self.limit_button.clicked.connect(self.open_limit_dialog)
        self.controls_layout.addWidget(self.limit_button)

        self.refresh_button = QPushButton(self.tr("Refresh"))
        self.refresh_button.clicked.connect(self.update_ui)
        self.controls_layout.addWidget(self.refresh_button)

        # History Tab
        self.history_tab = QWidget()
        self.history_layout = QVBoxLayout(self.history_tab)
        self.tabs.addTab(self.history_tab, self.tr("History"))

        self.history_controls = QHBoxLayout()
        self.history_layout.addLayout(self.history_controls)

        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.dateChanged.connect(self.update_history_table)
        self.history_controls.addWidget(QLabel(self.tr("From:")))
        self.history_controls.addWidget(self.date_from)

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.update_history_table)
        self.history_controls.addWidget(QLabel(self.tr("To:")))
        self.history_controls.addWidget(self.date_to)

        self.history_app_filter = QComboBox()
        self.history_app_filter.addItem(self.tr("All Apps"))
        self.history_app_filter.currentIndexChanged.connect(self.update_history_table)
        self.history_controls.addWidget(QLabel(self.tr("Filter App:")))
        self.history_controls.addWidget(self.history_app_filter)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            self.tr("Application"),
            self.tr("Date"),
            self.tr("Download (MB)"),
            self.tr("Upload (MB)"),
            self.tr("Duration (s)"),
            self.tr("Avg Speed (KB/s)")
        ])
        self.history_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_layout.addWidget(self.history_table)

        self.history_plot_button = QPushButton(self.tr("Show History Plot"))
        self.history_plot_button.clicked.connect(self.show_history_plot)
        self.history_layout.addWidget(self.history_plot_button)

        # Menu Bar
        self.init_menu_bar()

        # Timer for updating UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)

        # Apply default theme
        self.theme_manager.apply_theme("Windows 11")

    def init_menu_bar(self):
        menu_bar = self.menuBar()
        
        # Language Menu
        language_menu = menu_bar.addMenu(self.tr("Language"))
        lang_group = QActionGroup(self)
        
        en_action = QAction(self.tr("English"), self)
        en_action.setCheckable(True)
        en_action.setChecked(True)
        en_action.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(en_action)
        lang_group.addAction(en_action)

        fa_action = QAction(self.tr("Persian"), self)
        fa_action.setCheckable(True)
        fa_action.triggered.connect(lambda: self.change_language("fa"))
        language_menu.addAction(fa_action)
        lang_group.addAction(fa_action)

        zh_action = QAction(self.tr("Chinese"), self)
        zh_action.setCheckable(True)
        zh_action.triggered.connect(lambda: self.change_language("zh"))
        language_menu.addAction(zh_action)
        lang_group.addAction(zh_action)

        # Theme Menu
        theme_menu = menu_bar.addMenu(self.tr("Theme"))
        theme_group = QActionGroup(self)
        
        for theme in self.theme_manager.themes:
            action = QAction(theme, self)
            action.setCheckable(True)
            if theme == "Windows 11":
                action.setChecked(True)
            action.triggered.connect(lambda checked, t=theme: self.theme_manager.apply_theme(t))
            theme_menu.addAction(action)
            theme_group.addAction(action)

        # File Menu
        file_menu = menu_bar.addMenu(self.tr("File"))
        export_action = QAction(self.tr("Export Report"), self)
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)

        exit_action = QAction(self.tr("Exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menu_bar.addMenu(self.tr("View"))
        toggle_table = QAction(self.tr("Show/Hide Table"), self)
        toggle_table.setCheckable(True)
        toggle_table.setChecked(True)
        toggle_table.triggered.connect(lambda: self.table.setVisible(toggle_table.isChecked()))
        view_menu.addAction(toggle_table)

        toggle_plot = QAction(self.tr("Show/Hide Plot"), self)
        toggle_plot.setCheckable(True)
        toggle_plot.setChecked(True)
        toggle_plot.triggered.connect(lambda: self.canvas.setVisible(toggle_plot.isChecked()))
        view_menu.addAction(toggle_plot)

        # Toolbar actions
        export_action = QAction(QIcon("BandwidthBuddy.jpg"), self.tr("Export"), self)
        export_action.triggered.connect(self.export_report)
        self.toolbar.addAction(export_action)

        refresh_action = QAction(QIcon("BandwidthBuddy.jpg"), self.tr("Refresh"), self)
        refresh_action.triggered.connect(self.update_ui)
        self.toolbar.addAction(refresh_action)

    def change_language(self, lang):
        self.translator.load_language(self.app, lang)
        self.update_ui_texts()
        self.set_direction(lang)

    def set_direction(self, lang):
        if lang == "fa":
            self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def update_ui_texts(self):
        self.setWindowTitle(self.tr("BandwidthBuddy"))
        self.tabs.setTabText(0, self.tr("Real-time Monitoring"))
        self.tabs.setTabText(1, self.tr("History"))
        self.table.setHorizontalHeaderLabels([
            self.tr("Application"),
            self.tr("Download (KB/s)"),
            self.tr("Upload (KB/s)"),
            self.tr("Total Download (MB)"),
            self.tr("Total Upload (MB)"),
            self.tr("Status")
        ])
        self.history_table.setHorizontalHeaderLabels([
            self.tr("Application"),
            self.tr("Date"),
            self.tr("Download (MB)"),
            self.tr("Upload (MB)"),
            self.tr("Duration (s)"),
            self.tr("Avg Speed (KB/s)")
        ])
        self.view_mode.clear()
        self.view_mode.addItems([self.tr("All Apps"), self.tr("Individual Apps")])
        self.plot_type.clear()
        self.plot_type.addItems([self.tr("Bar"), self.tr("Line"), self.tr("Pie"), self.tr("Area")])
        self.time_range.clear()
        self.time_range.addItems([self.tr("Last 10s"), self.tr("Last 1m"), self.tr("Last 5m"), self.tr("Last 1h")])
        self.limit_button.setText(self.tr("Set Bandwidth Limit"))
        self.refresh_button.setText(self.tr("Refresh"))
        self.history_plot_button.setText(self.tr("Show History Plot"))
        self.history_app_filter.clear()
        self.history_app_filter.addItem(self.tr("All Apps"))
        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT app_name FROM bandwidth_usage")
        apps = [row[0] for row in cursor.fetchall()]
        self.history_app_filter.addItems(apps)
        conn.close()

    def init_monitoring(self):
        self.monitor_thread = threading.Thread(target=self.monitor_bandwidth, daemon=True)
        self.monitor_thread.start()

    def monitor_bandwidth(self):
        while True:
            current_net_io = {}
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    net_io = psutil.net_io_counters(pernic=True)
                    for interface in net_io:
                        download = net_io[interface].bytes_recv
                        upload = net_io[interface].bytes_sent
                        app_name = proc.info['name']
                        if app_name not in current_net_io:
                            current_net_io[app_name] = {"download": 0, "upload": 0}
                        current_net_io[app_name]["download"] += download
                        current_net_io[app_name]["upload"] += upload

                        conn = sqlite3.connect("bandwidth_buddy.db")
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO bandwidth_usage (app_name, download_bytes, upload_bytes, timestamp) VALUES (?, ?, ?, ?)",
                            (app_name, download, upload, datetime.now())
                        )
                        conn.commit()
                        conn.close()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self.update_previous_net_io(current_net_io)
            time.sleep(1)

    def update_previous_net_io(self, current_net_io):
        self.previous_net_io = current_net_io
        timestamp = datetime.now()
        self.plot_data["times"].append(timestamp)
        for app, data in current_net_io.items():
            if app not in self.plot_data["downloads"]:
                self.plot_data["downloads"][app] = []
                self.plot_data["uploads"][app] = []
            self.plot_data["downloads"][app].append(data["download"] / 1024 / 1024)
            self.plot_data["uploads"][app].append(data["upload"] / 1024 / 1024)
        if len(self.plot_data["times"]) > 3600:
            self.plot_data["times"] = self.plot_data["times"][-3600:]
            for app in self.plot_data["downloads"]:
                self.plot_data["downloads"][app] = self.plot_data["downloads"][app][-3600:]
                self.plot_data["uploads"][app] = self.plot_data["uploads"][app][-3600:]

    def update_ui(self):
        self.update_table()
        self.update_plot()
        self.update_app_selector()
        self.update_history_table()

    def update_view(self):
        self.update_table()
        self.update_plot()

    def update_table(self):
        self.table.setRowCount(0)
        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        
        if self.view_mode.currentText() == self.tr("All Apps"):
            cursor.execute("""
                SELECT app_name, 
                       SUM(download_bytes) / 1024 / 1024 as total_download,
                       SUM(upload_bytes) / 1024 / 1024 as total_upload,
                       (SELECT max_download_kbps FROM app_limits WHERE app_limits.app_name = bandwidth_usage.app_name) as dl_limit,
                       (SELECT max_upload_kbps FROM app_limits WHERE app_limits.app_name = bandwidth_usage.app_name) as ul_limit
                FROM bandwidth_usage
                GROUP BY app_name
            """)
            results = cursor.fetchall()
            self.table.setRowCount(len(results))
            for row, (app_name, total_download, total_upload, dl_limit, ul_limit) in enumerate(results):
                self.table.setItem(row, 0, QTableWidgetItem(app_name))
                self.table.setItem(row, 1, QTableWidgetItem(f"{total_download:.2f}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{total_upload:.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{total_download:.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(f"{total_upload:.2f}"))
                status = self.tr("Unlimited")
                if dl_limit or ul_limit:
                    status = f"{self.tr('Limited')} ({dl_limit or '∞'} kbps ↓, {ul_limit or '∞'} kbps ↑)"
                self.table.setItem(row, 5, QTableWidgetItem(status))
        else:
            selected_app = self.app_selector.currentText()
            if selected_app and selected_app != self.tr("Select App"):
                cursor.execute("""
                    SELECT app_name, download_bytes / 1024 / 1024 as download, 
                           upload_bytes / 1024 / 1024 as upload,
                           (SELECT max_download_kbps FROM app_limits WHERE app_limits.app_name = bandwidth_usage.app_name) as dl_limit,
                           (SELECT max_upload_kbps FROM app_limits WHERE app_limits.app_name = bandwidth_usage.app_name) as ul_limit
                    FROM bandwidth_usage
                    WHERE app_name = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (selected_app,))
                result = cursor.fetchone()
                if result:
                    self.table.setRowCount(1)
                    self.table.setItem(0, 0, QTableWidgetItem(result[0]))
                    self.table.setItem(0, 1, QTableWidgetItem(f"{result[1]:.2f}"))
                    self.table.setItem(0, 2, QTableWidgetItem(f"{result[2]:.2f}"))
                    self.table.setItem(0, 3, QTableWidgetItem(f"{result[1]:.2f}"))
                    self.table.setItem(0, 4, QTableWidgetItem(f"{result[2]:.2f}"))
                    status = self.tr("Unlimited")
                    if result[3] or result[4]:
                        status = f"{self.tr('Limited')} ({result[3] or '∞'} kbps ↓, {result[4] or '∞'} kbps ↑)"
                    self.table.setItem(0, 5, QTableWidgetItem(status))
        
        self.table.resizeColumnsToContents()
        conn.close()

    def update_plot(self):
        self.ax.clear()
        time_range = self.time_range.currentText()
        seconds = {"Last 10s": 10, "Last 1m": 60, "Last 5m": 300, "Last 1h": 3600}
        limit = seconds.get(time_range, 10)
        start_time = datetime.now() - pd.Timedelta(seconds=limit)

        if self.view_mode.currentText() == self.tr("All Apps"):
            conn = sqlite3.connect("bandwidth_buddy.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT app_name, SUM(download_bytes) / 1024 / 1024 as total_download,
                       SUM(upload_bytes) / 1024 / 1024 as total_upload
                FROM bandwidth_usage
                WHERE timestamp >= ?
                GROUP BY app_name
            """, (start_time,))
            results = cursor.fetchall()
            conn.close()

            apps = [r[0] for r in results]
            downloads = [r[1] for r in results]
            uploads = [r[2] for r in results]

            if self.plot_type.currentText() == self.tr("Bar"):
                x = np.arange(len(apps))
                width = 0.35
                self.ax.bar(x - width/2, downloads, width, label=self.tr("Download (MB)"), color="#1f77b4")
                self.ax.bar(x + width/2, uploads, width, label=self.tr("Upload (MB)"), color="#ff7f0e")
                self.ax.set_xticks(x)
                self.ax.set_xticklabels(apps, rotation=45)
                self.ax.set_ylabel(self.tr("Data (MB)"))
                if downloads or uploads:
                    self.ax.legend()
            elif self.plot_type.currentText() == self.tr("Line"):
                for app in apps:
                    app_data = [(t, d, u) for t, d, u in zip(self.plot_data["times"], 
                                                              self.plot_data["downloads"].get(app, []),
                                                              self.plot_data["uploads"].get(app, []))
                                if t >= start_time]
                    if app_data:
                        times, dls, uls = zip(*app_data)
                        self.ax.plot(times, dls, label=f"{app} {self.tr('Download')}", marker='o')
                        self.ax.plot(times, uls, label=f"{app} {self.tr('Upload')}", marker='s')
                self.ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                self.ax.set_ylabel(self.tr("Data (MB)"))
                if apps:
                    self.ax.legend()
            elif self.plot_type.currentText() == self.tr("Pie"):
                if sum(downloads) > 0:
                    self.ax.pie(downloads, labels=apps, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired(np.arange(len(apps))))
                    self.ax.set_title(self.tr("Download Distribution"))
            elif self.plot_type.currentText() == self.tr("Area"):
                for app in apps:
                    app_data = [(t, d, u) for t, d, u in zip(self.plot_data["times"], 
                                                              self.plot_data["downloads"].get(app, []),
                                                              self.plot_data["uploads"].get(app, []))
                                if t >= start_time]
                    if app_data:
                        times, dls, uls = zip(*app_data)
                        self.ax.fill_between(times, dls, label=f"{app} {self.tr('Download')}", alpha=0.5)
                        self.ax.fill_between(times, uls, label=f"{app} {self.tr('Upload')}", alpha=0.5)
                self.ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                self.ax.set_ylabel(self.tr("Data (MB)"))
                if apps:
                    self.ax.legend()
        else:
            selected_app = self.app_selector.currentText()
            if selected_app and selected_app != self.tr("Select App"):
                conn = sqlite3.connect("bandwidth_buddy.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, download_bytes / 1024 / 1024 as download,
                           upload_bytes / 1024 / 1024 as upload
                    FROM bandwidth_usage
                    WHERE app_name = ? AND timestamp >= ?
                    ORDER BY timestamp
                """, (selected_app, start_time))
                results = cursor.fetchall()
                conn.close()

                times = [pd.to_datetime(r[0]) for r in results]
                downloads = [r[1] for r in results]
                uploads = [r[2] for r in results]

                if self.plot_type.currentText() == self.tr("Bar"):
                    x = np.arange(len(times))
                    width = 0.35
                    self.ax.bar(x - width/2, downloads, width, label=self.tr("Download (MB)"), color="#1f77b4")
                    self.ax.bar(x + width/2, uploads, width, label=self.tr("Upload (MB)"), color="#ff7f0e")
                    self.ax.set_xticks(x)
                    self.ax.set_xticklabels(times, rotation=45)
                    self.ax.set_ylabel(self.tr("Data (MB)"))
                    if downloads or uploads:
                        self.ax.legend()
                elif self.plot_type.currentText() == self.tr("Line"):
                    self.ax.plot(times, downloads, label=self.tr("Download (MB)"), marker='o', color="#1f77b4")
                    self.ax.plot(times, uploads, label=self.tr("Upload (MB)"), marker='s', color="#ff7f0e")
                    self.ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                    self.ax.set_ylabel(self.tr("Data (MB)"))
                    if times:
                        self.ax.legend()
                elif self.plot_type.currentText() == self.tr("Pie"):
                    total = sum(downloads) + sum(uploads)
                    if total > 0:
                        self.ax.pie([sum(downloads), sum(uploads)], labels=[self.tr("Download"), self.tr("Upload")],
                                   autopct='%1.1f%%', startangle=90, colors=["#1f77b4", "#ff7f0e"])
                        self.ax.set_title(f"{selected_app} {self.tr('Data Distribution')}")
                elif self.plot_type.currentText() == self.tr("Area"):
                    self.ax.fill_between(times, downloads, label=self.tr("Download (MB)"), alpha=0.5, color="#1f77b4")
                    self.ax.fill_between(times, uploads, label=self.tr("Upload (MB)"), alpha=0.5, color="#ff7f0e")
                    self.ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                    self.ax.set_ylabel(self.tr("Data (MB)"))
                    if times:
                        self.ax.legend()

        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.figure.tight_layout()
        self.canvas.draw()

    def update_app_selector(self):
        current_selection = self.app_selector.currentText()
        self.app_selector.clear()
        self.app_selector.addItem(self.tr("Select App"))
        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT app_name FROM bandwidth_usage")
        apps = [row[0] for row in cursor.fetchall()]
        self.app_selector.addItems(apps)
        self.history_app_filter.clear()
        self.history_app_filter.addItem(self.tr("All Apps"))
        self.history_app_filter.addItems(apps)
        if current_selection in apps:
            self.app_selector.setCurrentText(current_selection)
        conn.close()

    def update_history_table(self):
        self.history_table.setRowCount(0)
        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        app_filter = self.history_app_filter.currentText()

        query = """
            SELECT app_name, timestamp, 
                   SUM(download_bytes) / 1024 / 1024 as total_download,
                   SUM(upload_bytes) / 1024 / 1024 as total_upload,
                   (MAX(timestamp) - MIN(timestamp)) as duration
            FROM bandwidth_usage
            WHERE timestamp BETWEEN ? AND ?
        """
        params = [date_from, date_to]
        if app_filter != self.tr("All Apps"):
            query += " AND app_name = ?"
            params.append(app_filter)
        query += " GROUP BY app_name, strftime('%Y-%m-%d', timestamp)"

        cursor.execute(query, params)
        results = cursor.fetchall()
        self.history_table.setRowCount(len(results))
        for row, (app_name, timestamp, total_download, total_upload, duration) in enumerate(results):
            self.history_table.setItem(row, 0, QTableWidgetItem(app_name))
            self.history_table.setItem(row, 1, QTableWidgetItem(timestamp))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{total_download:.2f}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{total_upload:.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{duration if duration else 0:.2f}"))
            avg_speed = (total_download + total_upload) / (duration or 1) * 1024
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{avg_speed:.2f}"))
        
        self.history_table.resizeColumnsToContents()
        conn.close()

    def open_limit_dialog(self):
        dialog = LimitDialog(self)
        dialog.exec()

    def show_history_plot(self):
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        app_filter = self.history_app_filter.currentText()

        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        query = """
            SELECT app_name, timestamp, download_bytes / 1024 / 1024 as download,
                   upload_bytes / 1024 / 1024 as upload
            FROM bandwidth_usage
            WHERE timestamp BETWEEN ? AND ?
        """
        params = [date_from, date_to]
        if app_filter != self.tr("All Apps"):
            query += " AND app_name = ?"
            params.append(app_filter)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(results, columns=["app_name", "timestamp", "download", "upload"])
        plt.figure(figsize=(12, 6))
        for app in df["app_name"].unique():
            app_data = df[df["app_name"] == app]
            plt.plot(pd.to_datetime(app_data["timestamp"]), app_data["download"], 
                    label=f"{app} {self.tr('Download')}", marker='o')
            plt.plot(pd.to_datetime(app_data["timestamp"]), app_data["upload"], 
                    label=f"{app} {self.tr('Upload')}", marker='s')
        plt.xlabel(self.tr("Time"))
        plt.ylabel(self.tr("Data (MB)"))
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def export_report(self):
        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT app_name, timestamp, download_bytes / 1024 / 1024 as download,
                   upload_bytes / 1024 / 1024 as upload
            FROM bandwidth_usage
        """)
        results = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(results, columns=["Application", "Timestamp", "Download (MB)", "Upload (MB)"])
        filename = f"bandwidth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        QMessageBox.information(self, self.tr("Export"), self.tr(f"Report exported to {filename}"))

# Limit Dialog
class LimitDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(parent.tr("Set Bandwidth Limit"))
        self.setWindowIcon(QIcon("BandwidthBuddy.jpg"))
        self.layout = QFormLayout(self)

        self.app_selector = QComboBox()
        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT app_name FROM bandwidth_usage")
        apps = [row[0] for row in cursor.fetchall()]
        self.app_selector.addItems(apps)
        self.layout.addRow(parent.tr("Application:"), self.app_selector)

        self.download_limit = QSpinBox()
        self.download_limit.setRange(0, 100000)
        self.download_limit.setValue(1000)
        self.layout.addRow(parent.tr("Download Limit (kbps):"), self.download_limit)

        self.upload_limit = QSpinBox()
        self.upload_limit.setRange(0, 100000)
        self.upload_limit.setValue(1000)
        self.layout.addRow(parent.tr("Upload Limit (kbps):"), self.upload_limit)

        self.enable_limit = QCheckBox(parent.tr("Enable Limit"))
        self.enable_limit.setChecked(True)
        self.layout.addRow(self.enable_limit)

        self.apply_button = QPushButton(parent.tr("Apply"))
        self.apply_button.clicked.connect(self.apply_limit)
        self.layout.addWidget(self.apply_button)

    def apply_limit(self):
        app_name = self.app_selector.currentText()
        max_download = self.download_limit.value() if self.enable_limit.isChecked() else None
        max_upload = self.upload_limit.value() if self.enable_limit.isChecked() else None

        conn = sqlite3.connect("bandwidth_buddy.db")
        cursor = conn.cursor()
        if max_download is None and max_upload is None:
            cursor.execute("DELETE FROM app_limits WHERE app_name = ?", (app_name,))
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO app_limits (app_name, max_download_kbps, max_upload_kbps) VALUES (?, ?, ?)",
                (app_name, max_download, max_upload)
            )
        conn.commit()
        conn.close()

        print(f"Applying limit to {app_name}: {max_download or '∞'} kbps download, {max_upload or '∞'} kbps upload")
        self.accept()

# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("BandwidthBuddy.jpg"))
    window = BandwidthBuddy(app)
    window.show()
    sys.exit(app.exec())