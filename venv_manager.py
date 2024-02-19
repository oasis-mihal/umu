import os
import subprocess

class VenvManager():
    def create(self):
        path = os.getcwd()
        os.mkdir(os.path.join(path, "umuenv"))

        # TODO: This needs to create the activate.bat / sh file or perhaps just copy it in instead?
