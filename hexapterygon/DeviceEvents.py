class DeviceEvents:
    @property
    def event_uninstall   (self): return self.__event_uninstall
    @property
    def event_install     (self): return self.__event_install
    @property
    def event_shell       (self): return self.__event_shell
    @property
    def event_download    (self): return self.__event_download
    @property
    def event_downloading (self): return self.__event_downloading
    @property
    def event_debloat     (self): return self.__event_debloat

    @event_uninstall.setter
    def event_uninstall   (self, value): self.__event_uninstall   = value
    @event_install.setter
    def event_install     (self, value): self.__event_install     = value
    @event_shell.setter
    def event_shell       (self, value): self.__event_shell       = value
    @event_download.setter
    def event_download    (self, value): self.__event_download    = value
    @event_downloading.setter
    def event_downloading (self, value): self.__event_downloading = value
    @event_debloat.setter
    def event_debloat     (self, value): self.__event_debloat     = value

    def __init__(self):
        self.__event_uninstall   = lambda *args : None
        self.__event_install     = lambda *args : None
        self.__event_shell       = lambda *args : None
        self.__event_download    = lambda *args : None
        self.__event_downloading = lambda *args : None
        self.__event_debloat     = lambda *args : None
