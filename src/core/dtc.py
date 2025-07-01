import json

class DTCDecoder:
    def __init__(self, protocol):
        with open(f"db/{protocol}_codes.json") as f:
            self.codes = json.load(f)

    def decode(self, code):
        return self.codes.get(code, {"description": "Unknown code"})
