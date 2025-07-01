import can
from cantools.database import load_file
import threading

class CANBus:
    def __init__(self, protocol="j1939"):
        self.protocol = protocol
        self.lock = threading.Lock()
        self.db = load_file(f"db/{protocol}.dbc")
        self.bus = can.interface.Bus(
            channel='can0',
            bustype='socketcan',
            bitrate=250000 if protocol == "j1939" else 500000
        )

    def stream_data(self):
        while True:
            with self.lock:
                msg = self.bus.recv(timeout=1)
                if msg:
                    yield {
                        "id": hex(msg.arbitration_id),
                        "data": self.db.decode_message(msg.arbitration_id, msg.data),
                        "timestamp": msg.timestamp
                    }

    def __del__(self):
        self.bus.shutdown()
