# Umu is a c-style package manager modelled after pip
import argparse
import tempfile

from venv_manager import VenvManager

parser = argparse.ArgumentParser(
                    prog='umu',
                    description='umu package manager',
                    epilog='Help')

parser.add_argument('operating_mode')
parser.add_argument('-r', required=False)
args = parser.parse_args()

def entry():
    venv_mgr = VenvManager()
    if args.operating_mode == "venv":
        # Create a venv
        # Activate the necessary environment variables, add libs to path
        venv_mgr.create()
    # elif args.operating_mode == "activate":
    #     venv_mgr.activate()
    # elif args.operating_mode == "deactivate":
    #     venv_mgr.deactivate()
    elif args.operating_mode == "install":
        print("installing")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    entry()
