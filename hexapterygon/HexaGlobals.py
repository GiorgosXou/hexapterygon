from os                     import getenv, sep
from shutil                 import which
from platform               import system
from github                 import Github

ADB         = which('adb') # test
IS_WINDOWS  = system() == 'Windows'
HOME_DIR    = getenv('UserProfile') if IS_WINDOWS else getenv('HOME')
CONFIG_PATH = getenv('hexapterygon_config_path',f'{HOME_DIR}{sep}.config{sep}hexapterygon')
DEVICE_PATH = f'{CONFIG_PATH}{sep}devices'
TMPAPP_PATH = f'{CONFIG_PATH}{sep}.temp_apps' # the path in which the apps are downloaded temporarly
SERVER_REPO = 'GiorgosXou/hexapterygon' # Repo containing other repos
GIT = Github(login_or_token=getenv('hexapterygon_github_token', None))

