from PyQt5.QtWidgets import QLCDNumber

class DigitalGauge(QLCDNumber):
    def __init__(self, title, value):
        super().__init__()
        self.setDigitCount(6)
        self.display(value)
