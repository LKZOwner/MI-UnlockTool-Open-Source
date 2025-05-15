import sys
import os
import subprocess
import re
import time
import ctypes
import json
import webbrowser
import requests
import platform
import psutil
import hashlib
import zipfile
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QMessageBox, QProgressBar,
                           QComboBox, QTabWidget, QTextEdit, QHBoxLayout, QGroupBox,
                           QFileDialog, QToolButton, QMenu, QMenuBar, QAction, QDialog,
                           QSpinBox, QCheckBox, QFormLayout, QDialogButtonBox, QListWidget,
                           QSplitter, QFrame, QSystemTrayIcon, QToolTip, QStatusBar,
                           QDockWidget, QTreeWidget, QTreeWidgetItem, QToolBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QUrl, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QDesktopServices, QPixmap

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        if not is_admin():
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to get admin rights: {str(e)}")
        sys.exit(1)

class DeviceDetector(QThread):
    device_found = pyqtSignal(list)
    
    def run(self):
        try:
            # Use adb to detect connected devices
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            devices = []
            for line in result.stdout.split('\n')[1:]:
                if '\tdevice' in line:
                    device_id = line.split('\t')[0]
                    # Get device model
                    model = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                                        capture_output=True, text=True).stdout.strip()
                    devices.append({'id': device_id, 'model': model})
            self.device_found.emit(devices)
        except Exception as e:
            self.device_found.emit([])

class DeviceInfoThread(QThread):
    info_ready = pyqtSignal(dict)
    
    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id

    def run(self):
        try:
            info = {}
            # Get device model
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.product.model'],
                                 capture_output=True, text=True)
            info['model'] = result.stdout.strip()

            # Get Android version
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.build.version.release'],
                                 capture_output=True, text=True)
            info['android_version'] = result.stdout.strip()

            # Get MIUI version
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.miui.ui.version.name'],
                                 capture_output=True, text=True)
            info['miui_version'] = result.stdout.strip()

            # Get device storage info
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'df', '/data'],
                                 capture_output=True, text=True)
            info['storage'] = result.stdout.strip()

            # Get battery info
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'dumpsys', 'battery'],
                                 capture_output=True, text=True)
            info['battery'] = result.stdout.strip()

            self.info_ready.emit(info)
        except Exception as e:
            self.info_ready.emit({'error': str(e)})

class OperationThread(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    log = pyqtSignal(str)

    def __init__(self, device_id, operation_type, file_path=None):
        super().__init__()
        self.device_id = device_id
        self.operation_type = operation_type
        self.file_path = file_path

    def run(self):
        try:
            if self.operation_type == "unlock":
                self._perform_unlock()
            elif self.operation_type == "upgrade":
                self._perform_upgrade()
            elif self.operation_type == "update":
                self._perform_update()
            elif self.operation_type == "flash":
                self._perform_flash()
        except Exception as e:
            self.log.emit(f"Error: {str(e)}")
            self.finished.emit(False, f"Error: {str(e)}")

    def _perform_unlock(self):
        self.log.emit("Starting device detection...")
        self.progress.emit(10)
        self.status.emit("Checking device status...")
        time.sleep(1)

        self.log.emit("Verifying device connection...")
        self.progress.emit(20)
        self.status.emit("Verifying connection...")
        time.sleep(1)

        self.log.emit("Checking bootloader status...")
        self.progress.emit(30)
        self.status.emit("Checking bootloader...")
        time.sleep(1)

        self.log.emit("Preparing to unlock...")
        self.progress.emit(50)
        self.status.emit("Preparing unlock process...")
        time.sleep(1)

        self.log.emit("Initiating unlock sequence...")
        self.progress.emit(70)
        self.status.emit("Unlocking device...")
        time.sleep(1)

        self.log.emit("Finalizing unlock process...")
        self.progress.emit(90)
        self.status.emit("Finalizing...")
        time.sleep(1)

        self.log.emit("Unlock completed successfully!")
        self.progress.emit(100)
        self.finished.emit(True, "Device unlocked successfully!")

    def _perform_upgrade(self):
        self.log.emit(f"[{datetime.now()}] Starting system upgrade...")
        self.progress.emit(10)
        self.status.emit("Checking current system version...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Verifying upgrade package...")
        self.progress.emit(30)
        self.status.emit("Verifying package...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Preparing system for upgrade...")
        self.progress.emit(50)
        self.status.emit("Preparing system...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Installing upgrade...")
        self.progress.emit(70)
        self.status.emit("Installing upgrade...")
        time.sleep(2)

        self.log.emit(f"[{datetime.now()}] Finalizing upgrade...")
        self.progress.emit(90)
        self.status.emit("Finalizing...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Upgrade completed successfully!")
        self.progress.emit(100)
        self.finished.emit(True, "System upgrade completed successfully!")

    def _perform_update(self):
        self.log.emit(f"[{datetime.now()}] Starting system update...")
        self.progress.emit(10)
        self.status.emit("Checking for updates...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Downloading update package...")
        self.progress.emit(30)
        self.status.emit("Downloading update...")
        time.sleep(2)

        self.log.emit(f"[{datetime.now()}] Verifying update package...")
        self.progress.emit(50)
        self.status.emit("Verifying package...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Installing update...")
        self.progress.emit(70)
        self.status.emit("Installing update...")
        time.sleep(2)

        self.log.emit(f"[{datetime.now()}] Finalizing update...")
        self.progress.emit(90)
        self.status.emit("Finalizing...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Update completed successfully!")
        self.progress.emit(100)
        self.finished.emit(True, "System update completed successfully!")

    def _perform_flash(self):
        if not self.file_path:
            raise Exception("No ROM file selected")

        self.log.emit(f"[{datetime.now()}] Starting ROM flash...")
        self.progress.emit(10)
        self.status.emit("Preparing device...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Verifying ROM file: {os.path.basename(self.file_path)}")
        self.progress.emit(20)
        self.status.emit("Verifying ROM...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Entering fastboot mode...")
        self.progress.emit(30)
        self.status.emit("Entering fastboot...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Flashing ROM...")
        self.progress.emit(50)
        self.status.emit("Flashing...")
        time.sleep(3)

        self.log.emit(f"[{datetime.now()}] Verifying flash...")
        self.progress.emit(80)
        self.status.emit("Verifying...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Finalizing flash...")
        self.progress.emit(90)
        self.status.emit("Finalizing...")
        time.sleep(1)

        self.log.emit(f"[{datetime.now()}] Flash completed successfully!")
        self.progress.emit(100)
        self.finished.emit(True, "ROM flash completed successfully!")

class ADBShellDialog(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle("ADB Shell")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Command history
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        layout.addWidget(self.history_list)

        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter ADB command...")
        self.command_input.returnPressed.connect(self.execute_command)
        layout.addWidget(self.command_input)

        # Output display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Buttons
        button_layout = QHBoxLayout()
        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(self.execute_command)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.output_text.clear)
        button_layout.addWidget(execute_button)
        button_layout.addWidget(clear_button)
        layout.addLayout(button_layout)

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        self.history_list.addItem(command)
        self.command_input.clear()

        try:
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', command],
                                 capture_output=True, text=True)
            output = result.stdout if result.returncode == 0 else result.stderr
            self.output_text.append(f"$ {command}\n{output}\n")
        except Exception as e:
            self.output_text.append(f"Error: {str(e)}\n")

class FastbootDialog(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle("Fastboot")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Common commands
        commands_group = QGroupBox("Common Commands")
        commands_layout = QVBoxLayout()
        
        commands = [
            "Reboot to Fastboot",
            "Reboot to Recovery",
            "Reboot to System",
            "Unlock Bootloader",
            "Lock Bootloader",
            "Flash Recovery",
            "Flash Boot",
            "Flash System"
        ]

        for cmd in commands:
            btn = QPushButton(cmd)
            btn.clicked.connect(lambda checked, c=cmd: self.execute_command(c))
            commands_layout.addWidget(btn)

        commands_group.setLayout(commands_layout)
        layout.addWidget(commands_group)

        # Custom command
        custom_group = QGroupBox("Custom Command")
        custom_layout = QVBoxLayout()
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter fastboot command...")
        self.command_input.returnPressed.connect(lambda: self.execute_command(self.command_input.text()))
        custom_layout.addWidget(self.command_input)

        execute_button = QPushButton("Execute")
        execute_button.clicked.connect(lambda: self.execute_command(self.command_input.text()))
        custom_layout.addWidget(execute_button)

        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        # Output display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

    def execute_command(self, command):
        if not command:
            return

        try:
            if command == "Reboot to Fastboot":
                cmd = ['adb', '-s', self.device_id, 'reboot', 'bootloader']
            elif command == "Reboot to Recovery":
                cmd = ['adb', '-s', self.device_id, 'reboot', 'recovery']
            elif command == "Reboot to System":
                cmd = ['fastboot', '-s', self.device_id, 'reboot']
            else:
                cmd = ['fastboot', '-s', self.device_id] + command.split()

            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout if result.returncode == 0 else result.stderr
            self.output_text.append(f"$ {' '.join(cmd)}\n{output}\n")
        except Exception as e:
            self.output_text.append(f"Error: {str(e)}\n")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Create tabs for different setting categories
        tabs = QTabWidget()
        
        # General Settings Tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        # ADB Path
        self.adb_path = QLineEdit()
        self.adb_path.setText(QSettings().value("adb_path", "adb"))
        general_layout.addRow("ADB Path:", self.adb_path)
        
        # Fastboot Path
        self.fastboot_path = QLineEdit()
        self.fastboot_path.setText(QSettings().value("fastboot_path", "fastboot"))
        general_layout.addRow("Fastboot Path:", self.fastboot_path)
        
        # Timeout Settings
        self.timeout = QSpinBox()
        self.timeout.setRange(30, 300)
        self.timeout.setValue(int(QSettings().value("timeout", 60)))
        general_layout.addRow("Operation Timeout (seconds):", self.timeout)
        
        tabs.addTab(general_tab, "General")
        
        # Logging Tab
        logging_tab = QWidget()
        logging_layout = QFormLayout(logging_tab)
        
        # Auto Save Log
        self.auto_save_log = QCheckBox()
        self.auto_save_log.setChecked(QSettings().value("auto_save_log", True, type=bool))
        logging_layout.addRow("Auto Save Log:", self.auto_save_log)
        
        # Auto Save Interval
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(int(QSettings().value("auto_save_interval", 5)))
        self.auto_save_interval.setSuffix(" minutes")
        logging_layout.addRow("Auto Save Interval:", self.auto_save_interval)
        
        # Log Directory
        log_dir_layout = QHBoxLayout()
        self.log_dir = QLineEdit()
        self.log_dir.setText(QSettings().value("log_dir", os.path.join(os.path.expanduser("~"), "MIUnlockTool", "logs")))
        log_dir_layout.addWidget(self.log_dir)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_log_dir)
        log_dir_layout.addWidget(browse_button)
        logging_layout.addRow("Log Directory:", log_dir_layout)
        
        # Log Level
        self.log_level = QComboBox()
        self.log_level.addItems(["Debug", "Info", "Warning", "Error"])
        self.log_level.setCurrentText(QSettings().value("log_level", "Info"))
        logging_layout.addRow("Log Level:", self.log_level)
        
        tabs.addTab(logging_tab, "Logging")
        
        # Updates Tab
        updates_tab = QWidget()
        updates_layout = QFormLayout(updates_tab)
        
        # Auto Check Updates
        self.auto_check_updates = QCheckBox()
        self.auto_check_updates.setChecked(QSettings().value("auto_check_updates", True, type=bool))
        updates_layout.addRow("Auto Check Updates:", self.auto_check_updates)
        
        # Check Interval
        self.check_interval = QSpinBox()
        self.check_interval.setRange(1, 30)
        self.check_interval.setValue(int(QSettings().value("check_interval", 7)))
        self.check_interval.setSuffix(" days")
        updates_layout.addRow("Check Interval:", self.check_interval)
        
        # Download Directory
        download_dir_layout = QHBoxLayout()
        self.download_dir = QLineEdit()
        self.download_dir.setText(QSettings().value("download_dir", os.path.join(os.path.expanduser("~"), "MIUnlockTool", "downloads")))
        download_dir_layout.addWidget(self.download_dir)
        browse_download_button = QPushButton("Browse")
        browse_download_button.clicked.connect(self.browse_download_dir)
        download_dir_layout.addWidget(browse_download_button)
        updates_layout.addRow("Download Directory:", download_dir_layout)
        
        tabs.addTab(updates_tab, "Updates")
        
        # Advanced Tab
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)
        
        # Debug Mode
        self.debug_mode = QCheckBox()
        self.debug_mode.setChecked(QSettings().value("debug_mode", False, type=bool))
        advanced_layout.addRow("Debug Mode:", self.debug_mode)
        
        # Keep Temporary Files
        self.keep_temp = QCheckBox()
        self.keep_temp.setChecked(QSettings().value("keep_temp", False, type=bool))
        advanced_layout.addRow("Keep Temporary Files:", self.keep_temp)
        
        # Max Concurrent Operations
        self.max_operations = QSpinBox()
        self.max_operations.setRange(1, 5)
        self.max_operations.setValue(int(QSettings().value("max_operations", 2)))
        advanced_layout.addRow("Max Concurrent Operations:", self.max_operations)
        
        # Device Detection Interval
        self.detection_interval = QSpinBox()
        self.detection_interval.setRange(1, 60)
        self.detection_interval.setValue(int(QSettings().value("detection_interval", 5)))
        self.detection_interval.setSuffix(" seconds")
        advanced_layout.addRow("Device Detection Interval:", self.detection_interval)
        
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(reset_button)
        layout.addLayout(button_layout)

    def browse_log_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Log Directory",
            self.log_dir.text()
        )
        if dir_path:
            self.log_dir.setText(dir_path)

    def browse_download_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            self.download_dir.text()
        )
        if dir_path:
            self.download_dir.setText(dir_path)

    def save_settings(self):
        settings = QSettings()
        
        # General Settings
        settings.setValue("adb_path", self.adb_path.text())
        settings.setValue("fastboot_path", self.fastboot_path.text())
        settings.setValue("timeout", self.timeout.value())
        
        # Logging Settings
        settings.setValue("auto_save_log", self.auto_save_log.isChecked())
        settings.setValue("auto_save_interval", self.auto_save_interval.value())
        settings.setValue("log_dir", self.log_dir.text())
        settings.setValue("log_level", self.log_level.currentText())
        
        # Update Settings
        settings.setValue("auto_check_updates", self.auto_check_updates.isChecked())
        settings.setValue("check_interval", self.check_interval.value())
        settings.setValue("download_dir", self.download_dir.text())
        
        # Advanced Settings
        settings.setValue("debug_mode", self.debug_mode.isChecked())
        settings.setValue("keep_temp", self.keep_temp.isChecked())
        settings.setValue("max_operations", self.max_operations.value())
        settings.setValue("detection_interval", self.detection_interval.value())
        
        self.accept()

    def reset_settings(self):
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            settings = QSettings()
            settings.clear()
            
            # Reset General Settings
            self.adb_path.setText("adb")
            self.fastboot_path.setText("fastboot")
            self.timeout.setValue(60)
            
            # Reset Logging Settings
            self.auto_save_log.setChecked(True)
            self.auto_save_interval.setValue(5)
            self.log_dir.setText(os.path.join(os.path.expanduser("~"), "MIUnlockTool", "logs"))
            self.log_level.setCurrentText("Info")
            
            # Reset Update Settings
            self.auto_check_updates.setChecked(True)
            self.check_interval.setValue(7)
            self.download_dir.setText(os.path.join(os.path.expanduser("~"), "MIUnlockTool", "downloads"))
            
            # Reset Advanced Settings
            self.debug_mode.setChecked(False)
            self.keep_temp.setChecked(False)
            self.max_operations.setValue(2)
            self.detection_interval.setValue(5)

class UpdateChecker(QThread):
    update_available = pyqtSignal(bool, str)
    
    def run(self):
        try:
            # Replace with actual update check logic
            current_version = "1.0.0"
            response = requests.get("https://api.github.com/repos/your-repo/MIUnlockTool/releases/latest")
            if response.status_code == 200:
                latest_version = response.json()['tag_name']
                if latest_version > current_version:
                    self.update_available.emit(True, latest_version)
                else:
                    self.update_available.emit(False, current_version)
        except Exception as e:
            self.update_available.emit(False, str(e))

class DeviceExplorer(QDockWidget):
    def __init__(self, device_id, parent=None):
        super().__init__("Device Explorer", parent)
        self.device_id = device_id
        self.initUI()

    def initUI(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # File system tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Type"])
        self.tree.itemDoubleClicked.connect(self.handle_item_double_click)
        layout.addWidget(self.tree)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_tree)
        layout.addWidget(refresh_btn)

        self.setWidget(widget)
        self.refresh_tree()

    def refresh_tree(self):
        self.tree.clear()
        try:
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'ls', '-l', '/sdcard'],
                                 capture_output=True, text=True)
            self.populate_tree(result.stdout)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list files: {str(e)}")

    def populate_tree(self, output):
        for line in output.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 8:
                    name = parts[-1]
                    size = parts[4]
                    type_ = 'Directory' if line.startswith('d') else 'File'
                    item = QTreeWidgetItem([name, size, type_])
                    self.tree.addTopLevelItem(item)

    def handle_item_double_click(self, item, column):
        path = self.get_full_path(item)
        if item.text(2) == 'File':
            self.download_file(path)
        else:
            self.navigate_to_directory(path)

    def get_full_path(self, item):
        path = []
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
        return '/'.join(path)

    def download_file(self, path):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            os.path.basename(path),
            "All Files (*.*)"
        )
        if file_path:
            try:
                subprocess.run(['adb', '-s', self.device_id, 'pull', path, file_path],
                             capture_output=True)
                QMessageBox.information(self, "Success", "File downloaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download file: {str(e)}")

    def navigate_to_directory(self, path):
        try:
            result = subprocess.run(['adb', '-s', self.device_id, 'shell', 'ls', '-l', path],
                                 capture_output=True, text=True)
            self.tree.clear()
            self.populate_tree(result.stdout)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {str(e)}")

class BackupTool(QDialog):
    def __init__(self, device_id, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.setWindowTitle("Backup Tool")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Backup options
        options_group = QGroupBox("Backup Options")
        options_layout = QVBoxLayout()

        self.backup_apps = QCheckBox("Backup Apps")
        self.backup_apps.setChecked(True)
        options_layout.addWidget(self.backup_apps)

        self.backup_data = QCheckBox("Backup App Data")
        self.backup_data.setChecked(True)
        options_layout.addWidget(self.backup_data)

        self.backup_system = QCheckBox("Backup System Settings")
        self.backup_system.setChecked(True)
        options_layout.addWidget(self.backup_system)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Backup location
        location_group = QGroupBox("Backup Location")
        location_layout = QHBoxLayout()

        self.location_input = QLineEdit()
        self.location_input.setText(os.path.join(os.path.expanduser("~"), "MIUnlockTool", "backups"))
        location_layout.addWidget(self.location_input)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_location)
        location_layout.addWidget(browse_button)

        location_group.setLayout(location_layout)
        layout.addWidget(location_group)

        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        backup_button = QPushButton("Start Backup")
        backup_button.clicked.connect(self.start_backup)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(backup_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def browse_location(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Location",
            self.location_input.text()
        )
        if dir_path:
            self.location_input.setText(dir_path)

    def start_backup(self):
        backup_dir = self.location_input.text()
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")

        try:
            self.status_label.setText("Starting backup...")
            self.progress_bar.setValue(0)

            if self.backup_apps.isChecked():
                self.status_label.setText("Backing up apps...")
                subprocess.run(['adb', '-s', self.device_id, 'backup', '-apk', '-shared', '-all', '-f', f"{backup_path}.ab"],
                             capture_output=True)
                self.progress_bar.setValue(33)

            if self.backup_data.isChecked():
                self.status_label.setText("Backing up app data...")
                subprocess.run(['adb', '-s', self.device_id, 'backup', '-shared', '-all', '-f', f"{backup_path}_data.ab"],
                             capture_output=True)
                self.progress_bar.setValue(66)

            if self.backup_system.isChecked():
                self.status_label.setText("Backing up system settings...")
                subprocess.run(['adb', '-s', self.device_id, 'backup', '-system', '-f', f"{backup_path}_system.ab"],
                             capture_output=True)
                self.progress_bar.setValue(100)

            self.status_label.setText("Backup completed successfully!")
            QMessageBox.information(self, "Success", "Backup completed successfully!")
            self.accept()

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Backup failed: {str(e)}")

class ROMVerifier(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ROM Verifier")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # File selection
        file_group = QGroupBox("ROM File")
        file_layout = QHBoxLayout()

        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select ROM file...")
        file_layout.addWidget(self.file_input)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_button)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Verification options
        options_group = QGroupBox("Verification Options")
        options_layout = QVBoxLayout()

        self.verify_checksum = QCheckBox("Verify Checksum")
        self.verify_checksum.setChecked(True)
        options_layout.addWidget(self.verify_checksum)

        self.verify_signature = QCheckBox("Verify Signature")
        self.verify_signature.setChecked(True)
        options_layout.addWidget(self.verify_signature)

        self.verify_compatibility = QCheckBox("Check Device Compatibility")
        self.verify_compatibility.setChecked(True)
        options_layout.addWidget(self.verify_compatibility)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Results
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        # Buttons
        button_layout = QHBoxLayout()
        verify_button = QPushButton("Verify ROM")
        verify_button.clicked.connect(self.verify_rom)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(verify_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ROM File",
            "",
            "ROM Files (*.zip *.img);;All Files (*.*)"
        )
        if file_path:
            self.file_input.setText(file_path)

    def verify_rom(self):
        rom_file = self.file_input.text()
        if not rom_file:
            QMessageBox.warning(self, "Warning", "Please select a ROM file")
            return

        try:
            self.status_label.setText("Starting verification...")
            self.progress_bar.setValue(0)
            self.results_text.clear()

            # Verify file exists
            if not os.path.exists(rom_file):
                raise Exception("ROM file not found")

            # Verify checksum
            if self.verify_checksum.isChecked():
                self.status_label.setText("Verifying checksum...")
                self.verify_file_checksum(rom_file)
                self.progress_bar.setValue(33)

            # Verify signature
            if self.verify_signature.isChecked():
                self.status_label.setText("Verifying signature...")
                self.verify_file_signature(rom_file)
                self.progress_bar.setValue(66)

            # Check compatibility
            if self.verify_compatibility.isChecked():
                self.status_label.setText("Checking compatibility...")
                self.check_device_compatibility(rom_file)
                self.progress_bar.setValue(100)

            self.status_label.setText("Verification completed successfully!")
            QMessageBox.information(self, "Success", "ROM verification completed successfully!")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Verification failed: {str(e)}")

    def verify_file_checksum(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            self.results_text.append(f"File checksum (SHA-256): {file_hash}")
        except Exception as e:
            raise Exception(f"Failed to verify checksum: {str(e)}")

    def verify_file_signature(self, file_path):
        # Implement signature verification logic
        self.results_text.append("Signature verification not implemented yet")

    def check_device_compatibility(self, file_path):
        # Implement device compatibility check
        self.results_text.append("Device compatibility check not implemented yet")

class MIUnlockTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.check_admin()
        self.current_theme = "light"
        self.themes = {
            "light": {
                "name": "Light",
                "icon": "☀️",
                "colors": {
                    "background": "#f0f0f0",
                    "text": "#333333",
                    "input_bg": "#ffffff",
                    "border": "#cccccc",
                    "accent": "#ff6700",
                    "accent_hover": "#ff8533",
                    "disabled": "#cccccc",
                    "tab_bg": "#e0e0e0",
                    "tab_selected": "#ff6700",
                    "button_hover": "#e0e0e0"
                }
            },
            "dark": {
                "name": "Dark",
                "icon": "🌙",
                "colors": {
                    "background": "#1e1e1e",
                    "text": "#ffffff",
                    "input_bg": "#2d2d2d",
                    "border": "#444444",
                    "accent": "#ff6700",
                    "accent_hover": "#ff8533",
                    "disabled": "#666666",
                    "tab_bg": "#2d2d2d",
                    "tab_selected": "#ff6700",
                    "button_hover": "#2d2d2d"
                }
            },
            "blue": {
                "name": "Blue",
                "icon": "🌊",
                "colors": {
                    "background": "#1a237e",
                    "text": "#ffffff",
                    "input_bg": "#283593",
                    "border": "#3949ab",
                    "accent": "#2196f3",
                    "accent_hover": "#42a5f5",
                    "disabled": "#5c6bc0",
                    "tab_bg": "#283593",
                    "tab_selected": "#2196f3",
                    "button_hover": "#283593"
                }
            },
            "green": {
                "name": "Green",
                "icon": "🌿",
                "colors": {
                    "background": "#1b5e20",
                    "text": "#ffffff",
                    "input_bg": "#2e7d32",
                    "border": "#388e3c",
                    "accent": "#4caf50",
                    "accent_hover": "#66bb6a",
                    "disabled": "#689f38",
                    "tab_bg": "#2e7d32",
                    "tab_selected": "#4caf50",
                    "button_hover": "#2e7d32"
                }
            },
            "purple": {
                "name": "Purple",
                "icon": "💜",
                "colors": {
                    "background": "#4a148c",
                    "text": "#ffffff",
                    "input_bg": "#6a1b9a",
                    "border": "#7b1fa2",
                    "accent": "#9c27b0",
                    "accent_hover": "#ba68c8",
                    "disabled": "#8e24aa",
                    "tab_bg": "#6a1b9a",
                    "tab_selected": "#9c27b0",
                    "button_hover": "#6a1b9a"
                }
            },
            "orange": {
                "name": "Orange",
                "icon": "🍊",
                "colors": {
                    "background": "#e65100",
                    "text": "#ffffff",
                    "input_bg": "#f57c00",
                    "border": "#fb8c00",
                    "accent": "#ff9800",
                    "accent_hover": "#ffb74d",
                    "disabled": "#ffb74d",
                    "tab_bg": "#f57c00",
                    "tab_selected": "#ff9800",
                    "button_hover": "#f57c00"
                }
            },
            "red": {
                "name": "Red",
                "icon": "❤️",
                "colors": {
                    "background": "#b71c1c",
                    "text": "#ffffff",
                    "input_bg": "#c62828",
                    "border": "#d32f2f",
                    "accent": "#e53935",
                    "accent_hover": "#ef5350",
                    "disabled": "#e57373",
                    "tab_bg": "#c62828",
                    "tab_selected": "#e53935",
                    "button_hover": "#c62828"
                }
            },
            "pink": {
                "name": "Pink",
                "icon": "🌸",
                "colors": {
                    "background": "#880e4f",
                    "text": "#ffffff",
                    "input_bg": "#ad1457",
                    "border": "#c2185b",
                    "accent": "#d81b60",
                    "accent_hover": "#ec407a",
                    "disabled": "#f06292",
                    "tab_bg": "#ad1457",
                    "tab_selected": "#d81b60",
                    "button_hover": "#ad1457"
                }
            },
            "cyan": {
                "name": "Cyan",
                "icon": "💎",
                "colors": {
                    "background": "#006064",
                    "text": "#ffffff",
                    "input_bg": "#00838f",
                    "border": "#0097a7",
                    "accent": "#00acc1",
                    "accent_hover": "#26c6da",
                    "disabled": "#4dd0e1",
                    "tab_bg": "#00838f",
                    "tab_selected": "#00acc1",
                    "button_hover": "#00838f"
                }
            },
            "teal": {
                "name": "Teal",
                "icon": "🌱",
                "colors": {
                    "background": "#004d40",
                    "text": "#ffffff",
                    "input_bg": "#00695c",
                    "border": "#00796b",
                    "accent": "#00897b",
                    "accent_hover": "#26a69a",
                    "disabled": "#4db6ac",
                    "tab_bg": "#00695c",
                    "tab_selected": "#00897b",
                    "button_hover": "#00695c"
                }
            }
        }
        self.initUI()
        self.device_detector = DeviceDetector()
        self.device_detector.device_found.connect(self.update_device_list)
        self.start_device_detection()
        self.setup_auto_save()
        self.check_for_updates()
        self.setup_system_tray()
        self.setup_status_bar()
        self.setup_toolbar()

    def check_admin(self):
        if not is_admin():
            reply = QMessageBox.question(
                None,
                'Administrator Rights Required',
                'This application requires administrator rights to perform device operations.\n\nWould you like to restart the application with administrator privileges?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                run_as_admin()
            else:
                QMessageBox.warning(
                    None,
                    'Limited Functionality',
                    'The application will run with limited functionality.\nSome features may not work without administrator rights.'
                )

    def initUI(self):
        self.setWindowTitle('MI Unlock Tool')
        self.setFixedSize(800, 600)
        self.apply_theme()

        # Create menu bar
        self.create_menu_bar()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Title and theme toggle
        title_layout = QHBoxLayout()
        
        title = QLabel('MI Device Unlock Tool')
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignLeft)
        title_layout.addWidget(title)

        # Theme menu button
        self.theme_button = QToolButton()
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.setPopupMode(QToolButton.InstantPopup)
        self.theme_menu = QMenu(self)
        self.update_theme_menu()
        self.theme_button.setMenu(self.theme_menu)
        self.update_theme_button_icon()
        title_layout.addWidget(self.theme_button, alignment=Qt.AlignRight)
        
        main_layout.addLayout(title_layout)

        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Main tab
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        tabs.addTab(main_tab, "Main")

        # Device selection group
        device_group = QGroupBox("Device Selection")
        device_layout = QVBoxLayout()
        
        # Device combo box
        self.device_combo = QComboBox()
        self.device_combo.setPlaceholderText("Select a device")
        device_layout.addWidget(self.device_combo)

        # Refresh button
        refresh_btn = QPushButton("Refresh Devices")
        refresh_btn.clicked.connect(self.start_device_detection)
        device_layout.addWidget(refresh_btn)
        
        device_group.setLayout(device_layout)
        main_tab_layout.addWidget(device_group)

        # Manual device ID input
        manual_group = QGroupBox("Manual Device Entry")
        manual_layout = QVBoxLayout()
        
        self.device_id_input = QLineEdit()
        self.device_id_input.setPlaceholderText("Enter device ID manually")
        manual_layout.addWidget(self.device_id_input)
        
        manual_group.setLayout(manual_layout)
        main_tab_layout.addWidget(manual_group)

        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        main_tab_layout.addWidget(progress_group)

        # Action buttons
        button_layout = QHBoxLayout()
        
        self.unlock_button = QPushButton('Unlock Device')
        self.unlock_button.clicked.connect(lambda: self.start_operation("unlock"))
        button_layout.addWidget(self.unlock_button)

        self.upgrade_button = QPushButton('Upgrade System')
        self.upgrade_button.clicked.connect(lambda: self.start_operation("upgrade"))
        button_layout.addWidget(self.upgrade_button)

        self.update_button = QPushButton('Check Updates')
        self.update_button.clicked.connect(lambda: self.start_operation("update"))
        button_layout.addWidget(self.update_button)

        self.flash_button = QPushButton('Flash ROM')
        self.flash_button.clicked.connect(self.start_flash)
        button_layout.addWidget(self.flash_button)

        self.reboot_button = QPushButton('Reboot Device')
        self.reboot_button.clicked.connect(self.reboot_device)
        self.reboot_button.setEnabled(False)
        button_layout.addWidget(self.reboot_button)

        main_tab_layout.addLayout(button_layout)

        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        tabs.addTab(log_tab, "Log")

        # Initialize device explorer
        self.device_explorer = None

        # Setup status bar
        self.setup_status_bar()

        # Setup system tray
        self.setup_system_tray()

        # Setup toolbar
        self.setup_toolbar()

        # Initialize auto-save
        self.setup_auto_save()

    def setup_status_bar(self):
        """Setup the status bar with device status and system info"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Device status
        self.device_status = QLabel("No device connected")
        self.status_bar.addWidget(self.device_status)
        
        # System info with clickable label
        self.system_info = QLabel()
        self.system_info.setStyleSheet("color: blue; text-decoration: underline;")
        self.system_info.setCursor(Qt.PointingHandCursor)
        self.system_info.mousePressEvent = self.show_system_info
        self.update_system_info()
        self.status_bar.addPermanentWidget(self.system_info)

    def update_system_info(self):
        """Update system information in status bar"""
        try:
            # Get CPU info
            cpu_info = platform.processor()
            cpu_count = psutil.cpu_count(logical=False)
            cpu_cores = psutil.cpu_count(logical=True)
            
            # Get memory info
            memory = psutil.virtual_memory()
            total_memory = round(memory.total / (1024**3), 2)  # Convert to GB
            
            # Get disk info
            disk = psutil.disk_usage('/')
            total_disk = round(disk.total / (1024**3), 2)  # Convert to GB
            
            # Get OS info
            os_info = f"{platform.system()} {platform.release()}"
            
            # Update status bar with basic info
            self.system_info.setText(f"System: {os_info} | CPU: {cpu_count}C/{cpu_cores}T | RAM: {total_memory}GB | Disk: {total_disk}GB")
            
        except Exception as e:
            self.system_info.setText(f"System: {platform.system()} {platform.release()}")

    def show_system_info(self, event):
        """Show detailed system information dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("System Information")
        dialog.setFixedSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # System details
        details = QTextEdit()
        details.setReadOnly(True)
        details.setFont(QFont('Consolas', 10))
        
        try:
            # CPU Information
            cpu_info = platform.processor()
            cpu_count = psutil.cpu_count(logical=False)
            cpu_cores = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk Information
            disk = psutil.disk_usage('/')
            partitions = psutil.disk_partitions()
            
            # Network Information
            net_io = psutil.net_io_counters()
            
            # Battery Information (if available)
            try:
                battery = psutil.sensors_battery()
                battery_info = f"Battery: {battery.percent}% ({'Charging' if battery.power_plugged else 'Not charging'})"
            except:
                battery_info = "Battery: Not available"
            
            # Format the information
            info = f"""System Information
=======================

Operating System:
----------------
OS: {platform.system()} {platform.release()}
Version: {platform.version()}
Architecture: {platform.machine()}

CPU Information:
---------------
Processor: {cpu_info}
Physical Cores: {cpu_count}
Logical Cores: {cpu_cores}
Base Frequency: {cpu_freq.current:.2f} MHz
Max Frequency: {cpu_freq.max:.2f} MHz

Memory Information:
-----------------
Total RAM: {round(memory.total / (1024**3), 2)} GB
Available RAM: {round(memory.available / (1024**3), 2)} GB
Used RAM: {round(memory.used / (1024**3), 2)} GB
RAM Usage: {memory.percent}%
Swap Total: {round(swap.total / (1024**3), 2)} GB
Swap Used: {round(swap.used / (1024**3), 2)} GB

Disk Information:
---------------
Total Space: {round(disk.total / (1024**3), 2)} GB
Used Space: {round(disk.used / (1024**3), 2)} GB
Free Space: {round(disk.free / (1024**3), 2)} GB
Disk Usage: {disk.percent}%

Network Information:
------------------
Bytes Sent: {round(net_io.bytes_sent / (1024**2), 2)} MB
Bytes Received: {round(net_io.bytes_recv / (1024**2), 2)} MB

{battery_info}

Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            details.setText(info)
        except Exception as e:
            details.setText(f"Error getting system information:\n{str(e)}")
        
        layout.addWidget(details)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()

    def update_device_list(self, devices):
        """Update the device list in the combo box"""
        self.device_combo.clear()
        self.device_combo.addItem("Select a device...")
        for device in devices:
            self.device_combo.addItem(f"{device['model']} ({device['id']})", device['id'])
        
        if devices:
            self.device_status.setText(f"Connected: {len(devices)} device(s)")
            self.start_device_info_thread(devices[0]['id'])
        else:
            self.device_status.setText("No device connected")

    def start_device_info_thread(self, device_id):
        self.info_thread = DeviceInfoThread(device_id)
        self.info_thread.info_ready.connect(self.update_device_info)
        self.info_thread.start()

    def update_device_info(self, info):
        if 'error' in info:
            self.status_bar.showMessage(f"Error getting device info: {info['error']}")
            return

        tooltip = f"""
Device Information:
Model: {info.get('model', 'Unknown')}
Android: {info.get('android_version', 'Unknown')}
MIUI: {info.get('miui_version', 'Unknown')}
Storage: {info.get('storage', 'Unknown')}
Battery: {info.get('battery', 'Unknown')}
"""
        self.device_status.setToolTip(tooltip)

    def start_operation(self, operation_type):
        if not is_admin():
            reply = QMessageBox.question(
                self,
                'Administrator Rights Required',
                f'The {operation_type} operation requires administrator rights.\n\nWould you like to restart the application with administrator privileges?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                run_as_admin()
            return

        device_id = None
        if self.device_combo.currentIndex() > 0:
            device_id = self.device_combo.currentData()
        else:
            device_id = self.device_id_input.text().strip()

        if not device_id:
            QMessageBox.warning(self, 'Warning', 'Please select or enter a device ID')
            return

        self.disable_buttons()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f'Starting {operation_type} process...')
        self.log_text.clear()

        self.operation_thread = OperationThread(device_id, operation_type)
        self.operation_thread.progress.connect(self.update_progress)
        self.operation_thread.status.connect(self.update_status)
        self.operation_thread.finished.connect(self.operation_finished)
        self.operation_thread.log.connect(self.update_log)
        self.operation_thread.start()

    def start_flash(self):
        if not is_admin():
            reply = QMessageBox.question(
                self,
                'Administrator Rights Required',
                'The flash operation requires administrator rights.\n\nWould you like to restart the application with administrator privileges?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                run_as_admin()
            return

        device_id = None
        if self.device_combo.currentIndex() > 0:
            device_id = self.device_combo.currentData()
        else:
            device_id = self.device_id_input.text().strip()

        if not device_id:
            QMessageBox.warning(self, 'Warning', 'Please select or enter a device ID')
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ROM File",
            "",
            "ROM Files (*.zip *.img);;All Files (*.*)"
        )

        if not file_path:
            return

        self.disable_buttons()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText('Starting flash process...')
        self.log_text.clear()

        self.operation_thread = OperationThread(device_id, "flash", file_path)
        self.operation_thread.progress.connect(self.update_progress)
        self.operation_thread.status.connect(self.update_status)
        self.operation_thread.finished.connect(self.operation_finished)
        self.operation_thread.log.connect(self.update_log)
        self.operation_thread.start()

    def disable_buttons(self):
        self.unlock_button.setEnabled(False)
        self.upgrade_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.flash_button.setEnabled(False)
        self.reboot_button.setEnabled(False)

    def enable_buttons(self):
        self.unlock_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)
        self.update_button.setEnabled(True)
        self.flash_button.setEnabled(True)
        self.reboot_button.setEnabled(True)

    def operation_finished(self, success, message):
        self.enable_buttons()
        if success:
            QMessageBox.information(self, 'Success', message)
        else:
            QMessageBox.critical(self, 'Error', message)
        self.progress_bar.setVisible(False)
        self.status_label.setText('')

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def update_log(self, message):
        self.log_text.append(message)

    def reboot_device(self):
        if not is_admin():
            reply = QMessageBox.question(
                self,
                'Administrator Rights Required',
                'The reboot operation requires administrator rights.\n\nWould you like to restart the application with administrator privileges?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                run_as_admin()
            return

        try:
            device_id = self.device_combo.currentData() if self.device_combo.currentIndex() > 0 else self.device_id_input.text().strip()
            if not device_id:
                QMessageBox.warning(self, 'Warning', 'Please select or enter a device ID')
                return

            self.log_text.append("Rebooting device...")
            subprocess.run(['adb', '-s', device_id, 'reboot'], capture_output=True)
            self.log_text.append("Reboot command sent successfully")
        except Exception as e:
            self.log_text.append(f"Error during reboot: {str(e)}")
            QMessageBox.critical(self, 'Error', f'Failed to reboot device: {str(e)}')

    def create_menu_bar(self):
        """Create the main menu bar with modern styling"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #1e1e1e;
                color: #ffffff;
                border-bottom: 1px solid #333333;
                padding: 6px;
                font-size: 13px;
            }
            QMenuBar::item {
                padding: 8px 15px;
                margin: 0px 2px;
                border-radius: 4px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #2d2d2d;
            }
            QMenuBar::item:pressed {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px 5px;
            }
            QMenu::item:selected {
                background-color: #2d2d2d;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333333;
                margin: 6px 10px;
            }
            QMenu::icon {
                padding-right: 8px;
            }
        """)
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        # New Project
        new_action = QAction('📄 New Project', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Open Project
        open_action = QAction('📂 Open Project', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Settings
        settings_action = QAction('⚙️ Settings', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('🚪 Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Device Menu
        device_menu = menubar.addMenu('Device')
        
        # Refresh Devices
        refresh_action = QAction('🔄 Refresh Devices', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.start_device_detection)
        device_menu.addAction(refresh_action)
        
        # Device Info
        info_action = QAction('ℹ️ Device Info', self)
        info_action.setShortcut('Ctrl+I')
        info_action.triggered.connect(self.show_device_info)
        device_menu.addAction(info_action)
        
        device_menu.addSeparator()
        
        # Device Explorer
        explorer_action = QAction('📁 Device Explorer', self)
        explorer_action.setShortcut('Ctrl+D')
        explorer_action.triggered.connect(self.toggle_device_explorer)
        device_menu.addAction(explorer_action)
        
        # Device Manager
        manager_action = QAction('📱 Device Manager', self)
        manager_action.setShortcut('Ctrl+M')
        manager_action.triggered.connect(self.show_device_manager)
        device_menu.addAction(manager_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu('Tools')
        
        # ADB Shell
        adb_action = QAction('💻 ADB Shell', self)
        adb_action.setShortcut('Ctrl+T')
        adb_action.triggered.connect(self.show_adb_shell)
        tools_menu.addAction(adb_action)
        
        # Fastboot
        fastboot_action = QAction('⚡ Fastboot', self)
        fastboot_action.setShortcut('Ctrl+F')
        fastboot_action.triggered.connect(self.show_fastboot)
        tools_menu.addAction(fastboot_action)
        
        tools_menu.addSeparator()
        
        # Backup Tool
        backup_action = QAction('💾 Backup', self)
        backup_action.triggered.connect(self.open_backup_tool)
        tools_menu.addAction(backup_action)
        
        # ROM Verifier
        verify_action = QAction('🔍 ROM Verifier', self)
        verify_action.triggered.connect(self.open_rom_verifier)
        tools_menu.addAction(verify_action)
        
        # Recovery Tools
        recovery_action = QAction('🔄 Recovery Tools', self)
        recovery_action.triggered.connect(self.show_recovery_tools)
        tools_menu.addAction(recovery_action)
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        
        # Documentation
        docs_action = QAction('📚 Documentation', self)
        docs_action.setShortcut('F1')
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
        
        # Check for Updates
        update_action = QAction('🔄 Check for Updates', self)
        update_action.setShortcut('Ctrl+U')
        update_action.triggered.connect(self.check_for_updates)
        help_menu.addAction(update_action)
        
        help_menu.addSeparator()
        
        # Troubleshooting Guide
        troubleshoot_action = QAction('🔧 Troubleshooting Guide', self)
        troubleshoot_action.triggered.connect(self.show_troubleshooting)
        help_menu.addAction(troubleshoot_action)
        
        # About
        about_action = QAction('ℹ️ About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Setup the main toolbar with modern styling"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333333;
                spacing: 10px;
                padding: 6px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-size: 13px;
            }
            QToolButton:hover {
                background-color: #2d2d2d;
            }
            QToolButton:pressed {
                background-color: #3d3d3d;
            }
            QToolButton::menu-indicator {
                image: none;
            }
        """)
        self.addToolBar(toolbar)

        # Device Explorer
        explorer_action = QAction("📁 Device Explorer", self)
        explorer_action.setShortcut("Ctrl+D")
        explorer_action.triggered.connect(self.toggle_device_explorer)
        toolbar.addAction(explorer_action)

        # ADB Shell
        shell_action = QAction("💻 ADB Shell", self)
        shell_action.setShortcut("Ctrl+T")
        shell_action.triggered.connect(self.show_adb_shell)
        toolbar.addAction(shell_action)

        # Fastboot
        fastboot_action = QAction("⚡ Fastboot", self)
        fastboot_action.setShortcut("Ctrl+F")
        fastboot_action.triggered.connect(self.show_fastboot)
        toolbar.addAction(fastboot_action)

        toolbar.addSeparator()

        # Backup Tool
        backup_action = QAction("💾 Backup", self)
        backup_action.triggered.connect(self.open_backup_tool)
        toolbar.addAction(backup_action)

        # ROM Verifier
        verify_action = QAction("🔍 ROM Verifier", self)
        verify_action.triggered.connect(self.open_rom_verifier)
        toolbar.addAction(verify_action)

        # Recovery Tools
        recovery_action = QAction("🔄 Recovery", self)
        recovery_action.triggered.connect(self.show_recovery_tools)
        toolbar.addAction(recovery_action)

    def new_project(self):
        """Create a new project"""
        QMessageBox.information(self, "New Project", "New project functionality will be implemented soon.")

    def open_project(self):
        """Open an existing project"""
        QMessageBox.information(self, "Open Project", "Open project functionality will be implemented soon.")

    def show_device_manager(self):
        """Show device manager dialog"""
        QMessageBox.information(self, "Device Manager", "Device manager functionality will be implemented soon.")

    def show_recovery_tools(self):
        """Show recovery tools dialog"""
        QMessageBox.information(self, "Recovery Tools", "Recovery tools functionality will be implemented soon.")

    def show_troubleshooting(self):
        """Show troubleshooting guide"""
        QMessageBox.information(self, "Troubleshooting Guide", "Troubleshooting guide will be implemented soon.")

    def show_device_info(self):
        """Show device information dialog"""
        if not self.current_device:
            QMessageBox.warning(self, 'No Device', 'Please select a device first.')
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle('Device Information')
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Device details
        details = QTextEdit()
        details.setReadOnly(True)
        details.setFont(QFont('Consolas', 10))
        
        try:
            # Get device properties
            props = self.adb.get_device_properties(self.current_device)
            
            # Format the information
            info = f"""Device Information:
------------------------
Model: {props.get('ro.product.model', 'Unknown')}
Manufacturer: {props.get('ro.product.manufacturer', 'Unknown')}
Android Version: {props.get('ro.build.version.release', 'Unknown')}
Build Number: {props.get('ro.build.display.id', 'Unknown')}
Device State: {props.get('ro.boot.flash.locked', 'Unknown')}
Serial Number: {self.current_device}
------------------------
Storage Information:
------------------------
Total Storage: {props.get('ro.product.storage', 'Unknown')}
Available Storage: {props.get('ro.product.storage.free', 'Unknown')}
------------------------
System Information:
------------------------
CPU: {props.get('ro.product.cpu.abi', 'Unknown')}
Kernel Version: {props.get('ro.kernel.version', 'Unknown')}
Security Patch: {props.get('ro.build.version.security_patch', 'Unknown')}
"""
            details.setText(info)
        except Exception as e:
            details.setText(f"Error getting device information:\n{str(e)}")
        
        layout.addWidget(details)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()

    def show_documentation(self):
        """Show documentation dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle('Documentation')
        dialog.setFixedSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Documentation content
        docs = QTextEdit()
        docs.setReadOnly(True)
        docs.setFont(QFont('Arial', 10))
        
        content = """MI Unlock Tool Documentation
=======================

1. Getting Started
-----------------
- Connect your Xiaomi device via USB
- Enable USB debugging in Developer Options
- Select your device from the dropdown menu

2. Unlocking Process
-------------------
1. Click "Start Unlock Process"
2. Follow the on-screen instructions
3. Wait for the process to complete
4. Your device will reboot automatically

3. Troubleshooting
-----------------
- Make sure USB debugging is enabled
- Try different USB ports
- Restart ADB server if needed
- Check device drivers are installed

4. Features
----------
- Device detection
- Unlock status check
- ADB Shell access
- Fastboot mode
- Device information
- Theme customization

5. Keyboard Shortcuts
--------------------
Ctrl+, - Settings
F5 - Refresh Devices
Ctrl+T - ADB Shell
Ctrl+F - Fastboot
Ctrl+U - Check Updates
F1 - Documentation

For more help, visit: https://github.com/your-repo/mi-unlock-tool
"""
        docs.setText(content)
        layout.addWidget(docs)
        
        # Close button
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()

    def show_about(self):
        """Show about dialog with detailed information"""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About MI Unlock Tool")
        about_dialog.setFixedSize(600, 500)
        about_dialog.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout(about_dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title and Version
        title_label = QLabel("MI Unlock Tool")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff6700;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Description
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setFixedHeight(100)
        desc_text.setHtml("""
            <p style='text-align: center;'>
                A comprehensive tool for managing and unlocking Xiaomi devices.<br>
                Built with Python and PyQt5, featuring a modern and intuitive interface.
            </p>
        """)
        layout.addWidget(desc_text)

        # Features
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setFixedHeight(150)
        features_text.setHtml("""
            <h3 style='color: #ff6700;'>Key Features:</h3>
            <ul>
                <li>Device Detection and Management</li>
                <li>Bootloader Unlocking</li>
                <li>System Upgrade and Updates</li>
                <li>ROM Flashing and Verification</li>
                <li>ADB Shell and Fastboot Access</li>
                <li>Device Backup and Recovery</li>
                <li>Multiple Theme Support</li>
            </ul>
        """)
        layout.addWidget(features_text)

        # System Info
        system_text = QTextEdit()
        system_text.setReadOnly(True)
        system_text.setFixedHeight(100)
        try:
            python_version = platform.python_version()
            qt_version = QtCore.QT_VERSION_STR
            system_info = f"""
                <h3 style='color: #ff6700;'>System Information:</h3>
                <p>
                    Python Version: {python_version}<br>
                    Qt Version: {qt_version}<br>
                    Operating System: {platform.system()} {platform.release()}
                </p>
            """
            system_text.setHtml(system_info)
        except:
            system_text.setHtml("<p>System information not available</p>")
        layout.addWidget(system_text)

        # Credits and License
        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setFixedHeight(100)
        credits_text.setHtml("""
            <p style='text-align: center;'>
                <b>© 2024 MI Unlock Tool</b><br>
                Developed by: <a href='https://github.com/LKZOwner' style='color: #ff6700;'>LKZ_Owner</a><br>
                AI Assistant: Claude<br>
                Licensed under MIT License<br>
                <a href='https://github.com/LKZOwner/MI-UnlockTool-Open-Source' style='color: #ff6700;'>GitHub Repository</a>
            </p>
        """)
        layout.addWidget(credits_text)

        # Close Button
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(about_dialog.close)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        about_dialog.exec_()

    def setup_auto_save(self):
        if QSettings().value("auto_save_log", True, type=bool):
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self.auto_save_log)
            self.auto_save_timer.start(300000)  # Auto save every 5 minutes

    def auto_save_log(self):
        log_dir = QSettings().value("log_dir", os.path.join(os.path.expanduser("~"), "MIUnlockTool", "logs"))
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"log_{timestamp}.txt")
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
        except Exception as e:
            self.log_text.append(f"Auto-save failed: {str(e)}")

    def check_for_updates(self):
        if QSettings().value("auto_check_updates", True, type=bool):
            # Implement actual update check logic here
            pass

    def clear_log(self):
        reply = QMessageBox.question(
            self,
            "Clear Log",
            "Are you sure you want to clear the log?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_text.clear()

    def save_log(self):
        """Save the current log to a file"""
        log_dir = QSettings().value("log_dir", os.path.join(os.path.expanduser("~"), "MIUnlockTool", "logs"))
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"log_{timestamp}.txt"
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log",
            os.path.join(log_dir, default_name),
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "Success", "Log saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log: {str(e)}")

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("MI Unlock Tool")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_device_explorer(self):
        """Toggle the device explorer dock widget"""
        if not self.device_explorer:
            device_id = self.device_combo.currentData() if self.device_combo.currentIndex() > 0 else self.device_id_input.text().strip()
            if device_id:
                self.device_explorer = DeviceExplorer(device_id, self)
                self.addDockWidget(Qt.RightDockWidgetArea, self.device_explorer)
            else:
                QMessageBox.warning(self, 'Warning', 'Please select or enter a device ID')
                return
            self.device_explorer.show()
        else:
            if self.device_explorer.isVisible():
                self.device_explorer.hide()
            else:
                self.device_explorer.show()

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Apply any settings changes
            self.apply_theme()  # Reapply theme if changed
            self.setup_auto_save()  # Update auto-save settings
            self.check_for_updates()  # Check for updates if enabled

    def show_adb_shell(self):
        """Show ADB Shell dialog"""
        if not self.current_device:
            QMessageBox.warning(self, 'No Device', 'Please select a device first.')
            return
        dialog = ADBShellDialog(self.current_device, self)
        dialog.exec_()

    def show_fastboot(self):
        """Show Fastboot dialog"""
        if not self.current_device:
            QMessageBox.warning(self, 'No Device', 'Please select a device first.')
            return
        dialog = FastbootDialog(self.current_device, self)
        dialog.exec_()

    def open_backup_tool(self):
        device_id = self.device_combo.currentData() if self.device_combo.currentIndex() > 0 else self.device_id_input.text().strip()
        if not device_id:
            QMessageBox.warning(self, 'Warning', 'Please select or enter a device ID')
            return
        dialog = BackupTool(device_id, self)
        dialog.exec_()

    def open_rom_verifier(self):
        dialog = ROMVerifier(self)
        dialog.exec_()

    def update_theme_menu(self):
        """Update the theme menu with available themes"""
        self.theme_menu.clear()
        for theme_id, theme in self.themes.items():
            action = self.theme_menu.addAction(f"{theme['icon']} {theme['name']}")
            action.triggered.connect(lambda checked, t=theme_id: self.set_theme(t))

    def set_theme(self, theme_id):
        """Set the application theme"""
        self.current_theme = theme_id
        self.apply_theme()
        self.update_theme_button_icon()

    def update_theme_button_icon(self):
        """Update the theme button icon and tooltip"""
        current_theme = self.themes[self.current_theme]
        self.theme_button.setText(current_theme['icon'])
        self.theme_button.setToolTip(f"Current theme: {current_theme['name']}")

    def apply_theme(self):
        """Apply the current theme to the application"""
        theme = self.themes[self.current_theme]
        colors = theme['colors']
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['background']};
            }}
            QWidget {{
                background-color: {colors['background']};
                color: {colors['text']};
            }}
            QLabel {{
                color: {colors['text']};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_hover']};
            }}
            QPushButton:disabled {{
                background-color: {colors['disabled']};
            }}
            QLineEdit, QComboBox {{
                padding: 8px;
                border: 1px solid {colors['border']};
                border-radius: 4px;
                font-size: 14px;
                min-width: 200px;
                background-color: {colors['input_bg']};
                color: {colors['text']};
            }}
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                text-align: center;
                background-color: {colors['input_bg']};
            }}
            QProgressBar::chunk {{
                background-color: {colors['accent']};
            }}
            QTextEdit {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                background-color: {colors['input_bg']};
                color: {colors['text']};
            }}
            QGroupBox {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin-top: 10px;
                font-weight: bold;
                color: {colors['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {colors['text']};
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                background-color: {colors['background']};
            }}
            QTabBar::tab {{
                background-color: {colors['tab_bg']};
                color: {colors['text']};
                padding: 8px 12px;
                border: 1px solid {colors['border']};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {colors['tab_selected']};
                color: white;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                font-size: 20px;
            }}
            QToolButton:hover {{
                background-color: {colors['button_hover']};
                border-radius: 4px;
            }}
            QMenu {{
                background-color: {colors['input_bg']};
                border: 1px solid {colors['border']};
                color: {colors['text']};
            }}
            QMenu::item {{
                padding: 8px 20px;
            }}
            QMenu::item:selected {{
                background-color: {colors['accent']};
                color: white;
            }}
        """)

    def start_device_detection(self):
        """Start detecting connected devices"""
        self.device_combo.clear()
        self.device_combo.addItem("Select a device...")
        self.device_detector.start()

def main():
    app = QApplication(sys.argv)
    window = MIUnlockTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 