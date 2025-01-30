from   ppadb                  import InstallError
from   os.path                import isfile, basename, exists, isdir, sep
from   github.GithubException import UnknownObjectException
from   .StateEnums            import DownloadState, InstallState, UninstallState
from   ppadb.device           import Device
from   .DeviceEvents          import DeviceEvents
from   sys                    import version_info
import hexapterygon.HexaGlobals as g
import requests

if version_info >= (3,10): # because i think it has a C implementation too (from _bisect import *)
    from bisect import insort_left
else:
    from .InsortForOldPython import insort_left



class DeviceOverlay(Device, DeviceEvents): # TODO 2023-04-02 01:59:35 AM No need for additional info on events, remove them (comment them) + add  downloading event or something


    def __check_repo(self, repo):
        try:
            return self.is_repo_valid(g.GIT.get_repo(repo))
        except:
            return False


    def __file_under_dir_exists(self):
        potential_file = f'{self.config}{sep}{self.type_identifier}.txt' 
        if isfile(potential_file):
            self.config = potential_file # Eeww?
            return True
        return False


    def __is_config_local(self):
        return isfile(self.config) or self.__file_under_dir_exists()


    def __init_config_check(self): # TODO: Instead of this function just create a setter for config where the checking happens there | meh for every device check the same config when passed from the debloater? come ooon...
        self.locally = self.__is_config_local()
        if not self.locally and not self.__check_repo(self.config): # omg.... what have i done | I could raise event_debloat on those things but anyways for now
            if not self.config == g.SERVER_REPO:
                return False
            self.config = g.SERVER_REPO  # raise event_debloat or another event idk, with message "Invalid {self.config} switching to {g.SERVER_REPO}" ?
        return True


    def __init__(self, device, config=g.SERVER_REPO): # TODO: self.shell('su') to check if rooted
        super().__init__( device.client, device.serial)
        DeviceEvents.__init__(self)
        self.__device        = device
        self.__brand         = self.get_property('ro.product.brand')
        self.__model         = self.get_property('ro.product.model')
        self.__name          = self.get_property('ro.product.name')
        self.__locked        = True if self.get_property('ro.boot.flash.locked') == '1' else False
        self.install_allowed = True
        self.shell_allow     = False
        self.config          = config
        self.locally         = self.__is_config_local()
    

    def get_local_config_instructions(self): # returns local instructions
        assert isfile(self.config), f'"{self.config}" is not a file path.'
        with open(self.config, 'r') as f:
            lines = f.readlines()
        return lines


    def is_repo_valid(self, repo): # Eeww 4 indentations ... 
        for content_file in repo.get_contents(""):
            if content_file.type == "file" or content_file.path != 'devices': continue
            for content_file in repo.get_contents("devices"):
                if content_file.type == "dir" or content_file.path[8:] != f'{self.type_identifier}.txt': continue
                return True
        return False


    def get_summary(self, repo): # meh
        config = repo.get_contents(f"devices/{self.type_identifier}.txt")
        lines = config.decoded_content.decode().splitlines() # Eww
        if lines[0].strip() != '[SUMMARY]': return []
        summary = ['']
        for ln in lines[1:]:
            if ln.strip() == '': return summary
            summary.append(ln.strip())


    def get_available_repos(self, get_summary=False): # TODO: Maybe add a limit because of the github's limit for requests (without key) [if too many lists for one device] | Maybe add recursion with 'device' -> 'devices' if list 
        try:
            repo = g.GIT.get_repo(self.config) 
            config = repo.get_contents(f'device_repo_lists/{self.type_identifier}.txt')
        except UnknownObjectException as e:
            return []
        config = config.decoded_content.decode()
        repos = []
        for repo_line in config.splitlines():
            try:
                split_repo_line = repo_line.split('|')
                repo = g.GIT.get_repo(split_repo_line[0].strip())
                if not self.is_repo_valid(repo): continue
                if repo: insort_left(repos, (repo.stargazers_count, repo.full_name, split_repo_line[1] if len(split_repo_line) > 1 else split_repo_line[0], self.get_summary(repo) if get_summary else []), key=lambda x: -x[0]) # ('|')[1] = Description
            except UnknownObjectException as e:
                continue # ignore the bad repository or list them ?
        return repos


    def get_online_config_instructions(self):
        if self.config == g.SERVER_REPO: # no need for 'else' because self.config
            available_repos = self.get_available_repos()
            if not available_repos: return None # assert available_repos, f'No available repositories for you device "{self.type_identifier}" or something went wrong with the network'
            self.config = available_repos[0][1]
        repo = g.GIT.get_repo(self.config)
        try:
            config = repo.get_contents(f'devices/{self.type_identifier}.txt')
        except UnknownObjectException as e:
            return None
        return config.decoded_content.decode().splitlines()


    def get_config_instructions(self):
        if not self.__init_config_check(): return None
        return self.get_online_config_instructions() if not self.locally else self.get_local_config_instructions()


    def __handle_url(self, package):
        return None # TODO: download from github


    def __download(self, package, version): # TODO: add max retires
        r = requests.get(f'https://f-droid.org/repo/{package}_{version}.apk', stream=True)
        if not r:
            r = requests.get(f'https://f-droid.org/archive/{package}_{version}.apk', stream=True)
            self.event_download(package, version, DownloadState.FALLBACK) # f'"{package}" Successfully downloaded'
        if not r:
            r = requests.get(f'https://apt.izzysoft.de/fdroid/repo/{package}_{version}.apk', stream=True)
            self.event_download(package, version, DownloadState.FALLBACK) # f'"{package}" Successfully downloaded'
        if not r:
            self.event_download(package, version, DownloadState.FAILED) # f'"{package}" Successfully downloaded'
            return False

        #TODO: add a try catch
        with open(f'{g.TMPAPP_PATH}{sep}{package}_{version}.apk', 'wb') as f:
            total_length = int(r.headers.get('content-length'))/1024
            for i, chunk in enumerate(r.iter_content(chunk_size=1024), start=1): #expected_size=(total_length/1024) + 1): 
                if chunk:
                    f.write(chunk)
                    f.flush()
                    self.event_downloading(package, i, total_length) # f'"{package}" Successfully downloaded' | int((i)*100/total_length)

        self.event_download(package, version, DownloadState.SUCCEEDED) # f'"{package}" Successfully downloaded'
        return True


    def download(self, package, version=None): #github url or package name for fdroid
        # TODO: if package.startswith('https:'): return self.__handle_url(package)
        # check if chached
        response = requests.get(f'https://f-droid.org/api/v1/packages/{package}').json().get('suggestedVersionCode', None)
        if not response: 
            self.event_download(package, version, DownloadState.FAILED) # '"{package}" Failed to download'
            return (False, version)
        version = version if version else response
        return (self.__download(package, version), version)


    def install(self, package, *args): # TODO split (| version)
        if not self.install_allowed: return False
        tmp_pkg_splt = package.split('|')
        version = None if len(tmp_pkg_splt) == 1 else int(tmp_pkg_splt[1])
        package = tmp_pkg_splt[0]
        pkgname = package
        if isfile(package) and package.endswith('.apk'):
            package = package
            # TODO: check if is_installed
        else: 
            if self.is_installed(package):
                self.event_install(pkgname, None, InstallState.ALREADY_INSTALLED) # '"{package}" Package is already installed'
                return True
            # yield from (f"Downloading proccess at {i}%" for i in )
            self.event_download(package, version, DownloadState.BEGINS) # f'"{package}" Successfully downloaded'
            downloaded, version = self.download(package, version)
            if downloaded:
                package = f'{g.TMPAPP_PATH}{sep}{package}_{version}.apk'
            else:
                return False
        try:
            super().install(package, *args)
            self.event_install(pkgname, version, InstallState.INSTALLED) # '"{package}" Successfully installed'
            return True
        except InstallError: # TODO: self.push(path,) into a folder if no install allowed and there's enought space
            self.install_allowed = False
            self.event_install(pkgname, version, InstallState.BLOCKED) # 'Install is not allowed'
            return False


    def __shell(self, *args): # Aaahh no f@ck1ng time again...
        output = super().shell(*args) 
        self.event_shell(output) # TODO: pass args
        return output


    def uninstall(self, package):
        if not self.is_installed(package):
            self.event_uninstall(package, UninstallState.ALREADY_UNINSTALLED)
            return True
        output = True if super().shell(f'pm uninstall -k --user 0 {package}').strip() == "Success" else False # TODO: if self.is_installed(package) ? maybe ? | if i wont specify --user it wont work for all packages eg. com.xiaomi.discover
        self.event_uninstall(package, UninstallState.UNINSTALLED if output else UninstallState.ERROR)
        return output


    def restore(self, package):
        #cmd package install-existing <package>
        pass


    __temp_instriction_call = None
    def __perform(self, instruction): # 3-7 if statements i think they are faster than a built-in hash map in this case
        if not instruction                 : return 
        elif   instruction == '[UNINSTALL]': self.__temp_instriction_call = self.uninstall
        elif   instruction == '[INSTALL]'  : self.__temp_instriction_call = self.install
        elif   instruction == '[SHELL]'    : self.__temp_instriction_call = self.__shell 
        elif   instruction == '[SUMMARY]'  : self.__temp_instriction_call = None
        elif self.__temp_instriction_call: # TODO: Add extra instruction called EXTERNAL (or something) for external shell commands if user allows so by arg
            tmp_split   = instruction.split('#')
            comment     = tmp_split[len(tmp_split)-1].strip()
            instruction = tmp_split[0].strip()
            self.event_debloat(instruction, comment)
            self.__temp_instriction_call(instruction)


    def debloat(self):
        instructions = self.get_config_instructions()
        if not instructions: return False
        for i, instruction in enumerate(instructions):
            self.__perform(instruction.strip())
        return True


    @property
    def device(self): return self.__device

    @property
    def brand(self): return self.__brand

    @property
    def model(self): return self.__model

    @property
    def name(self): return self.__name

    @property
    def locked(self): return self.__locked

    @property
    def type_identifier(self): # TODO: make it safe as name for paths
        return f'{self.brand} {self.model} {self.name}'

    def get_property(self, prop):
        return self.device.shell(f'getprop {prop}').strip()
