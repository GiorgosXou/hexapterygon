from subprocess     import Popen, PIPE 
from ppadb.client   import Client as AdbClient
from os             import makedirs
from .DeviceEvents  import DeviceEvents
from .DeviceOverlay import DeviceOverlay
from github         import Github
import hexapterygon.HexaGlobals as g
from shutil import rmtree



__version__ = '1.1.1'
def get_global_server_repo(): return g.SERVER_REPO
def set_global_server_repo(value): g.SERVER_REPO = value
def set_github_token      (value): g.GIT         = Github(login_or_token=value)



class Hexapterygon(DeviceEvents): # TODO: restore via cmd package install-existing <package>

    client = None
    def start_server(self):
        assert g.ADB, 'Please Install adb tools https://developer.android.com/studio/releases/platform-tools'
        Popen([g.ADB, 'start-server'], shell=False, stdout=PIPE, stderr=PIPE).wait() #.exe for windows
        return AdbClient(host="127.0.0.1", port=5037)


    def __del__(self):
        if not self.client: return
        self.client.kill()
        rmtree(g.TMPAPP_PATH)
        # TODO: delete TMPAPP_PATH *


    def __init__(self, config=g.SERVER_REPO, start_adb_server=True, ignore_flags=False): # Maybe Warning and error flags to ignore ? (flags is a TODO for the config file)
        self.client = self.start_server() if start_adb_server else None
        self.__config = config
        makedirs(g.DEVICE_PATH, exist_ok=True)
        makedirs(g.TMPAPP_PATH, exist_ok=True)
        super().__init__()


    def __pass_common_init_events_for(self, device): # Meh ... too much memmory for possibilities\variables that might never be used | To be honest I could just pass self to DeviceOverlay and pass device to each event But nvm...
        device.event_uninstall   = self.event_uninstall
        device.event_install     = self.event_install
        device.event_shell       = self.event_shell
        device.event_download    = self.event_download
        device.event_downloading = self.event_downloading
        device.event_debloat     = self.event_debloat


    def debloat(self, devices=[], config=g.SERVER_REPO):
        if not self.client: self.client = self.start_server()
        if not isinstance(devices, list): devices = [devices]
        self.__config  = config # repo URL (full_name) or PATH (file\Directory)
        self.devices   = self.get_devices() if not devices else devices
        assert self.devices, f'No {"authorized " if self.get_unauthorized_devices() else ""}devices found connected'
        for device in self.devices:
            self.__pass_common_init_events_for(device)
            yield device.debloat()


    def get_devices(self):
        if not self.client: return None 
        return [DeviceOverlay(d, self.__config) for d in self.client.devices("device")]

    def get_unauthorized_devices(self):
        if not self.client: return None
        return self.client.devices("unauthorized")


    def begin_tui(self):
        import unicurses as uc
        from .HexaTUI import HexaTUI
        global stdscr
        stdscr = uc.initscr() # Global UniCurses Variable
        event  = -1

        uc.start_color  ( )
        uc.cbreak       ( )
        uc.noecho       ( )
        uc.curs_set     (0)
        uc.mouseinterval(0)  # Initializing Mouse and then Update/refresh() stdscr
        uc.mousemask    (uc.ALL_MOUSE_EVENTS | uc.REPORT_MOUSE_POSITION) # print("\033[?1003h\n")
        uc.keypad       (stdscr, True )
        uc.nodelay      (stdscr, False)
        # print           (BEGIN_MOUSE) # Initializing mouse movement | Don't move it above because it won't work on Windows
        uc.refresh      ( )
        # Initializing HexaTUI
        HEIGHT,WIDTH = uc.getmaxyx(stdscr)
        debloater_ui = HexaTUI(self, is_focused=True) 
        debloater_ui.begin()

        while event != 27 or debloater_ui.escape_event_consumed: 
            event = uc.get_wch()
            if event == uc.KEY_RESIZE:uc.resize_term(0,0)
            debloater_ui.handle_events(event)
            debloater_ui.refresh()
        # print(END_MOUSE)
        uc.endwin()




"""
TODO: Maybe auto-setup adb\platform-tools (for windows at least) https://stackoverflow.com/a/63840426/11465149
"""
