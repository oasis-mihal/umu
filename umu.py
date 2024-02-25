# Umu is a c-style package manager modelled after pip
import argparse
import tempfile

from VenvData import PackageData, VenvData
from install import InstallManager
from venv_manager import VenvManager

parser = argparse.ArgumentParser(
                    prog='umu',
                    description='umu package manager',
                    epilog='Help')
subparser = parser.add_subparsers(dest="operating_mode")

## VENV (unfinished)
create_subparser = subparser.add_parser("create")
create_subparser.add_argument('-v', '--cpp-version', required=True)

## INSTALL
install_subparser = subparser.add_parser("install")
install_subparser.add_argument('-r', required=False)
install_subparser.add_argument('command', nargs='?')

## UNINSTALL
uninstall_subparser = subparser.add_parser("uninstall")
uninstall_subparser.add_argument('-r', required=False)
uninstall_subparser.add_argument('command', nargs='?')

## LIST
list_subparser = subparser.add_parser("list")

args = parser.parse_args()

def entry():
    venv_mgr = VenvManager()
    if args.operating_mode == "create":
        # Create a venv
        # Activate the necessary environment variables, add libs to path
        venv_mgr.create(args.cpp_version)
    elif args.operating_mode == "list":
        venv_data = VenvData(venv_mgr.data_file_path)
        packages = venv_data.packages
        # Sort by name for readability
        packages = dict(sorted(packages.items()))
        packages_s = [str(x) for x in packages.values()]
        packages_concat = "\n".join(packages_s)

        print(f"umu Installed Packages ({venv_data.cpp_version}):\n{packages_concat}")

    elif args.operating_mode == "install":
        venv_data = VenvData(venv_mgr.data_file_path)
        install_mgr = InstallManager(venv_data)
        if args.r is not None:
            install_mgr.install_from_requirements(args.r)
        elif args.command is not None:
            install_mgr.install_single(args.command)

    elif args.operating_mode == "uninstall":
        venv_data = VenvData(venv_mgr.data_file_path)
        install_mgr = InstallManager(venv_data)
        if args.r is not None:
            raise NotImplementedError()
        #    install_mgr.install_from_requirements(args.r)
        elif args.command is not None:
            install_mgr.uninstall_single(args.command)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    entry()
