# "Borrowed" from https://pythonbasics.org/webserver/
# This class is mostly just used for local testing so nobody has to download Apache or something
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

host_name = "localhost"
server_port = 8080

class ZipServer(BaseHTTPRequestHandler):
    def do_GET(self):

        if self.path == "/visual-leak-detector":
            self.get_zip_response()
        else:
            self.get_config_response()

    def get_zip_response(self):
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()

        self.get_example_zip()

    def get_config_response(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.get_example_file()

    def get_example_zip(self):
        # Get the test_json file to server back to the client
        with open(os.path.join("test_server", "visual-leak-detector_v1.0.0_x64.zip"), "rb") as f:
            contents = f.read()
            self.wfile.write(contents)

    def get_example_file(self):
        # Get the test_json file to server back to the client
        with open(os.path.join("test_server", "visual-leak-detector_v1.0.0_x64.json"), "r") as f:
            contents = f.read()
            self.wfile.write(bytes(contents, "utf-8"))

if __name__ == "__main__":
    web_server = HTTPServer((host_name, server_port), ZipServer)
    print(f"Server started at http://{host_name}:{server_port}")
    print(f"JSON at http://{host_name}:{server_port}/visual-leak-detector-config")
    print(f"Zip at http://{host_name}:{server_port}/visual-leak-detector")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()