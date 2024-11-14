from enum import Enum

class InstallState(Enum):
    ALREADY_INSTALLED = 2
    INSTALLED         = 1
    BLOCKED           = 0


class UninstallState(Enum):
    ALREADY_UNINSTALLED = 2
    UNINSTALLED         = 1
    ERROR               = 0


class DownloadState(Enum):
    FALLBACK  = 3
    BEGINS    = 2
    SUCCEEDED = 1
    FAILED    = 0
