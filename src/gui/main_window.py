from PyQt5.QtWidgets import QMainWindow, QTabWidget
from .widgets.gauges import DigitalGauge
from .widgets.log_view import LogViewer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("openCAN")
        self.tabs = QTabWidget()
        
        # Add tabs
        self.tabs.addTab(self.create_dashboard(), "Dashboard")
        self.tabs.addTab(LogViewer(), "Logs")
        
        self.setCentralWidget(self.tabs)

    def create_dashboard(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(DigitalGauge("RPM", "0"))
        widget.setLayout(layout)
        return widget
