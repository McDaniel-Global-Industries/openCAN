import sys
from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, 
                              QPushButton, QStatusBar, QHBoxLayout)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("openCAN - PySide6")
        self.setMinimumSize(400, 300)
        
        # Initialize UI
        self.init_ui()
        
        # Initialize CAN data variables
        self.rpm = 0
        self.speed = 0
        self.temperature = 0
        
        # Data update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Update every 100ms

    def init_ui(self):
        """Initialize the user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("openCAN Dashboard")
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Data display labels
        self.rpm_label = QLabel("RPM: 0")
        self.rpm_label.setFont(QFont('Arial', 14))
        
        self.speed_label = QLabel("Speed: 0 km/h")
        self.speed_label.setFont(QFont('Arial', 14))
        
        self.temp_label = QLabel("Engine Temp: 0 °C")
        self.temp_label.setFont(QFont('Arial', 14))
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self.start_monitoring)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.rpm_label)
        main_layout.addWidget(self.speed_label)
        main_layout.addWidget(self.temp_label)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def update_data(self):
        """Update the displayed data"""
        # Simulate changing data
        self.rpm = (self.rpm + 10) % 8000
        self.speed = (self.speed + 0.5) % 220
        self.temperature = 80 + (self.rpm / 200) % 40
        
        # Update labels
        self.rpm_label.setText(f"RPM: {self.rpm}")
        self.speed_label.setText(f"Speed: {self.speed:.1f} km/h")
        self.temp_label.setText(f"Engine Temp: {self.temperature:.1f} °C")

    def start_monitoring(self):
        """Start CAN data monitoring"""
        self.timer.start()
        self.status_bar.showMessage("Monitoring CAN data...")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_monitoring(self):
        """Stop CAN data monitoring"""
        self.timer.stop()
        self.status_bar.showMessage("Monitoring stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        """Handle window close event"""
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
