import csv
from pathlib import Path
from datetime import datetime

class DataLogger:
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

    def log(self, data):
        file = self.log_dir / f"{datetime.now().strftime('%Y%m%d')}.csv"
        is_new = not file.exists()
        
        with open(file, 'a', newline='') as f:
            writer = csv.writer(f)
            if is_new:
                writer.writerow(data.keys())
            writer.writerow(data.values())
