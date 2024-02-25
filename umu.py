# Umu is a c-style package manager modelled after pip
import argparse
import tempfile

from install import InstallManager
from venv_manager import VenvManager

parser = argparse.ArgumentParser(
                    prog='umu',
                    description='umu package manager',
                    epilog='Help')
subparser = parser.add_subparsers(dest="operating_mode")
## VENV (unfinished)

## INSTALL
install_subparser = subparser.add_parser("install")
install_subparser.add_argument('-r', required=False)
install_subparser.add_argument('command', nargs='?')
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
        install_mgr = InstallManager()
        if args.r is not None:
            install_mgr.install_from_requirements(args.r)
        elif args.command is not None:
            install_mgr.install_single(args.command)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    entry()
