# import sys                                                          # TESTING: UNCOMMENT TO USE LOCAL PACKAGE (./__init__.py) | https://stackoverflow.com/a/25888670/11465149
# from os.path import dirname, abspath                                # TESTING: UNCOMMENT TO USE LOCAL PACKAGE (./__init__.py) | https://stackoverflow.com/a/25888670/11465149
# sys.path.insert(0, dirname(dirname(abspath(__file__))))             # TESTING: UNCOMMENT TO USE LOCAL PACKAGE (./__init__.py) | https://stackoverflow.com/a/25888670/11465149
# sys.path.append('..')                                               # TESTING WITH DAP
# sys.path.append('/home/xou/.local/lib/python3.10/site-packages/')   # TESTING WITH DAP
from hexapterygon import Hexapterygon, __version__, get_global_server_repo, set_github_token, set_global_server_repo
import argparse



def parse_terminal_arguments(): 
    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='?', default=get_global_server_repo(), help=f'Path or repository (default: "{get_global_server_repo()}")')
    parser.add_argument('-v', '--version', action='version', version=f'Hexapterygon v.{__version__} | Powered by UNI-CURSES')
    parser.add_argument('--getid', action='store_true', help='Display type_identifier for each authorised device')
    return vars(parser.parse_args())


def print_type_identifiers(debloater, getid):
    if not getid: return
    authorised_devices = debloater.get_devices()
    if not authorised_devices: print(f'No {"authorized " if debloater.get_unauthorized_devices() else ""}devices found connected');exit()
    for i, device in enumerate(authorised_devices):
        print(f'[{i}]: {device.type_identifier}')
    exit()


def main(): # TODO: pass args to set_global_server_repo() set_github_token('')     
    args = parse_terminal_arguments()
    debloater = Hexapterygon(args['config'])#'./../Xiaomi test.txt')
    print_type_identifiers(debloater, args['getid'])
    debloater.begin_tui()
    exit()


if __name__ == "__main__":
    main()



"""
Fun fact: this whole time I am developing this module\\utility with the assumption that it is also going to work with multiple connected devices *(surely not parallely [as of now] but yeah... just so you know...)*
"""
