import http.server
import socketserver
import urllib.parse
from datetime import datetime

# CONFIGURATION
PORT = 8000
# Map the 'act' ID from the URL to the internal state key
# MUST MATCH your const.py CMD_MAP IDs
ACT_MAP = {1: "setpoint", 2: "fanspeed", 3: "floorenable", 4: "systemheat"}

# INITIAL STATE (Based on your uploaded XML)
# We store 'value' and the 'xml_path' to inject it into
state = {
    "currenttemp": {"val": 140, "path": "currenttemp"},  # 14.0 C
    "battv": {"val": 124, "path": "heater1/battv"},  # 12.4 V
    "setpoint": {"val": 140, "path": "settings/setpoint"},
    "fanspeed": {"val": 10, "path": "settings/fanspeed"},
    "floorenable": {"val": 0, "path": "settings/floorenable"},  # 0=Off, 1=On
    "systemheat": {"val": 1, "path": "systemheat"},
}


class RixenMockHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        # 1. Handle Status XML Request
        if parsed_path.path == "/status.xml":
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.end_headers()
            xml = self.generate_xml()
            self.wfile.write(xml.encode("utf-8"))
            print(f"[MOCK] Served XML status (Setpoint: {state['setpoint']['val']})")

        # 2. Handle Control Commands (interface.cgi?act=X&val=Y)
        elif parsed_path.path == "/interface.cgi":
            act = int(query.get("act", [-1])[0])
            val = int(query.get("val", [0])[0])

            if act in ACT_MAP:
                key = ACT_MAP[act]
                state[key]["val"] = val
                print(f"[MOCK] Command Received: Set {key} to {val}")

                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                print(f"[MOCK] Unknown action ID: {act}")
                self.send_response(400)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def generate_xml(self):
        """Reconstructs the XML with current state values."""
        # Note: This is a simplified template based on your file
        return f"""<response>
<version>MOCK_DEVICE_V1</version>
<uptime>99999</uptime>
<systemheat>{state['systemheat']['val']}</systemheat>
<currenttemp>{state['currenttemp']['val']}</currenttemp>
<heater1>
    <battv>{state['battv']['val']}</battv>
    <flametemp>7525</flametemp>
    <inlettemp>150</inlettemp>
    <outlettemp>160</outlettemp>
</heater1>
<settings>
    <setpoint>{state['setpoint']['val']}</setpoint>
    <fanspeed>{state['fanspeed']['val']}</fanspeed>
    <floorenable>{state['floorenable']['val']}</floorenable>
</settings>
</response>"""


if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), RixenMockHandler) as httpd:
        print(f"Rixen Mock Heater running at http://localhost:{PORT}")
        print(f"XML Status: http://localhost:{PORT}/status.xml")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
