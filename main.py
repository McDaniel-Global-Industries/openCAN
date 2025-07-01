import sys
import can
from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, 
                              QWidget, QPushButton, QStatusBar, QHBoxLayout)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("openCAN - PySide6")
        self.setMinimumSize(400, 300)
        
        # CAN bus configuration
        self.can_bus = None
        self.can_interface = 'socketcan'  # Change to your interface (socketcan, virtual, etc.)
        self.can_channel = 'can0'         # Change to your channel
        
        # Initialize UI
        self.init_ui()
        
        # Initialize CAN data variables
        self.rpm = 0
        self.speed = 0
        self.temperature = 0
        
        # Data update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)

    def init_ui(self):
        """Initialize the user interface"""
        # ... [keep all the existing UI initialization code from previous example] ...

    def start_monitoring(self):
        """Start CAN data monitoring"""
        try:
            # Initialize CAN bus connection
            self.can_bus = can.interface.Bus(
                interface=self.can_interface,
                channel=self.can_channel,
                receive_own_messages=False
            )
            
            self.timer.start(100)  # Update every 100ms
            self.status_bar.showMessage(f"Monitoring CAN data on {self.can_channel}...")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        except Exception as e:
            self.status_bar.showMessage(f"CAN Error: {str(e)}")
            self.stop_monitoring()

    def stop_monitoring(self):
        """Stop CAN data monitoring"""
        self.timer.stop()
        if self.can_bus is not None:
            self.can_bus.shutdown()
            self.can_bus = None
        self.status_bar.showMessage("Monitoring stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def update_data(self):
        """Read and update data from CAN bus"""
        if self.can_bus is None:
            return
            
        try:
            # Read all available messages
            while True:
                msg = self.can_bus.recv(timeout=0)  # Non-blocking read
                if msg is None:
                    break
                
                # Process CAN message (example for standard CAN frames)
                if msg.arbitration_id == 0x0C1:  # Example RPM message ID
                    self.rpm = int.from_bytes(msg.data[0:2], byteorder='big')
                elif msg.arbitration_id == 0x0C2:  # Example Speed message ID
                    self.speed = int.from_bytes(msg.data[0:2], byteorder='big') / 10
                elif msg.arbitration_id == 0x0C3:  # Example Temp message ID
                    self.temperature = msg.data[0]
                
            # Update UI
            self.rpm_label.setText(f"RPM: {self.rpm}")
            self.speed_label.setText(f"Speed: {self.speed:.1f} km/h")
            self.temp_label.setText(f"Engine Temp: {self.temperature:.1f} °C")
            
        except Exception as e:
            self.status_bar.showMessage(f"CAN Read Error: {str(e)}")
            self.stop_monitoring()

    def closeEvent(self, event):
        """Handle window close event"""
        self.stop_monitoring()
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
