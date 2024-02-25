# "Borrowed" from https://pythonbasics.org/webserver/
# This class is mostly just used for local testing so nobody has to download Apache or something
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

host_name = "localhost"
server_port = 8080

class ZipServer(BaseHTTPRequestHandler):
    def do_GET(self):
        result = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(result.query)
        print(f"Path: {result.path}, params: {params}")
        if result.path.startswith("/assets/"):
            self.get_zip_response(result.path)
        elif result.path == "/package/":
            self.get_config_response(params)

    def get_zip_response(self, path):
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.end_headers()

        asset_name = path.removeprefix("/assets/")
        self.get_example_zip(asset_name)

    def get_config_response(self, config):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.get_example_file(config.get("name")[0])

    def get_example_zip(self, package_file):
        # Get the test_json file to server back to the client
        with open(os.path.join("test_server", package_file), "rb") as f:
            contents = f.read()
            self.wfile.write(contents)

    def get_example_file(self, package_name):
        # Get the test_json file to server back to the client
        with open(os.path.join("test_server", f"{package_name}.json"), "r") as f:
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