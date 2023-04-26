from math import log10
import hexapterygon
import unicurses as uc

from .StateEnums import DownloadState, InstallState, UninstallState
from .TUItilities import Border, Highlight, Label, TextBox, Parent
from time import sleep
import re
import threading
import hexapterygon.HexaGlobals as g


class HexaTUI(Parent): # And a Component that can be used stand alone as it is with a uni-curses project | uni-curses compatible component

    def on_debloat(self, instruction, comment):
        self.comment = comment


    def on_install(self, package, output):
        if output == InstallState.INSTALLED:
            self.textbox_instructions.text = f'│ ✓  [INSTALLED] {self.comment}\n' + self.textbox_instructions.text 
        elif output == InstallState.ALREADY_INSTALLED:
            self.textbox_instructions.text = f'│ ○  [INSTALLED] {self.comment}\n' + self.textbox_instructions.text 
        else: # BLOCKED
            self.textbox_instructions.text = f'│ ✗  [BLOCKED] Skipping installation\n' + self.textbox_instructions.text # TIMESTAMP TOOOOO
        self.refresh()


    def on_shell(self, output): # TODO: Show output only if user passes arg  | if it contains Error then show x else tick maybe
        if not output: 
            self.textbox_instructions.text = f'│ ○  [SHELL] {self.comment}\n' + self.textbox_instructions.text 
            self.refresh()
            return
        self.textbox_instructions.text = f'│ ○  └─ [SHELL] {self.comment}\n' + self.textbox_instructions.text 
        lines = output.split('\n')
        if len(lines) >=2:
            lines = lines[:-1]
        for ln in lines:
            self.textbox_instructions.text = f'│ ○  ├─ {ln}\n' + self.textbox_instructions.text
        self.textbox_instructions.text = f'│ ○  ┌───────────────────────────────────┐\n' + self.textbox_instructions.text # long pipi energy
        self.refresh()


    def on_downloading(self,package, i, total_length): # TODO: replace the first line as an update
        percentage =  int((i)*100/total_length)
        steps = int((i)*30/total_length)
        blanks = 30-steps 
        if i == 1 : self.textbox_instructions.text = f"│ ○  ├─ {'━'*steps}{' '*blanks} {percentage}%\n" + self.textbox_instructions.text
        lines = self.textbox_instructions.text.split('\n')  
        self.textbox_instructions.text = f"│ ○  ├─ {'━'*steps}{' '*blanks} {percentage}%\n" + '\n'.join(lines[1:])
        self.refresh()


    def on_download(self, package, output):
        if output == DownloadState.BEGINS:
            self.textbox_instructions.text = f'│ ○  └─ [DOWNLOADING] {self.comment}\n' + self.textbox_instructions.text 
        elif output == DownloadState.SUCCEEDED:
            self.textbox_instructions.text = f'│ ✓  ┌─ Successfully downloaded\n' + self.textbox_instructions.text 
        elif output == DownloadState.FAILED:
            self.textbox_instructions.text = f'│ ✗  ┌─ Failed to download\n' + self.textbox_instructions.text 
        self.refresh()


    def on_uninstall(self, package, output):
        if output == UninstallState.UNINSTALLED:
            self.textbox_instructions.text = f'│ ✓  [UNINSTALLED] {self.comment}\n' + self.textbox_instructions.text 
        elif output == UninstallState.ALREADY_UNINSTALLED:
            self.textbox_instructions.text = f'│ ○  [ALREADY UNINSTALLED] {self.comment}\n' + self.textbox_instructions.text 
        else:
            self.textbox_instructions.text = f'│ ✗  Failed to uninstall {package}\n' + self.textbox_instructions.text # TIMESTAMP TOOOOO
        self.refresh()


    def __add_components(self, win, color_pair_offset): # │
        self.label_device          = Label(1,2,'⟡ Informations: ', (False,False, True,True), width = self.columns-4, win = win, color_pair_offset = color_pair_offset)
        self.label_info            = Label(self.lines-2 ,2,'● Press ESC to exit  ░▒▓██▓▒░ HEXAPTERYGON 2023 ░▒▓██▓▒░', (False,True, True,True), width = self.columns-4, win = win, color_pair_offset = color_pair_offset)
        self.textbox_instructions  = TextBox(3,2, self.lines -6, self.columns -4 , ' ', (True,True, True,True),  win = win, color_pair_offset = color_pair_offset) #│ ✓  Press ESC to exit\n│ █▓▒░ Press ESC to exit ░▒▓█
        self.label_device.style    = uc.A_ITALIC | uc.A_BOLD 
        self.label_info.style      = uc.A_DIM
        self.label_info.color_pair = 2    
        patterns = [ # lol another piece of code for which I feel guilty for all the enviromental disaster it will create | CPU goes brrr
            Highlight(re.compile( r'[0-9]+%')                         , 5 , uc.A_BOLD  ),
            Highlight(re.compile( r'(?<=│ ✓  )\[DONE\]')              , 5 , uc.A_BOLD  ),
            Highlight(re.compile( r'(?<=│ ✗  )\[FAILED\]')            , 3 , uc.A_BOLD  ),
            Highlight(re.compile( r'[0-9]+\.')                        , 2 , uc.A_BOLD  ),
            Highlight(re.compile( r'"(.*?)"')                         , 1 , uc.A_ITALIC),
            Highlight(re.compile( r'^│ ✓')                            , 5),
            Highlight(re.compile( r'^│ ✗')                            , 3),
            Highlight(re.compile( r'^│ ○')                            , 2),
            Highlight(re.compile( r'^│ ★')                            , 2),
            Highlight(re.compile( r'\[[0-9]+( )+Stars\]')             , 2),
            Highlight(re.compile( r'(Failed|Error|INVALID)')          , 3),
            Highlight(re.compile( r' (━){1,5}')                       , 3),
            Highlight(re.compile( r'(?<= ━━━━━)(━){1,12}')            , 2),
            Highlight(re.compile( r'(?<= ━━━━━━━━━━━━━━━━━)(━){1,8}') , 5),
            Highlight(re.compile( r'Successfully')                    , 5),
            Highlight(re.compile( r'(┌───────────────────────────────────┐|└─|┌─|├─)'), 1, uc.A_DIM),
            Highlight(re.compile( r'(LOADING|DOWNLOADING|ALREADY UNINSTALLED|UNINSTALLED|INSTALLED|SHELL|BLOCKED)'), 1, uc.A_DIM),
        ]
        self.textbox_instructions.set_inline_highlight_patterns(patterns)


    def __init__(self, debloater: hexapterygon, win=None, color_pair_offset=0, is_focused=False): # TODO: I might need to create a function for is_focused ?
        super().__init__(win or uc.stdscr)
        self.is_focused                  = is_focused
        self.debloater                   = debloater
        self.debloater.event_uninstall   = self.on_uninstall
        self.debloater.event_install     = self.on_install
        self.debloater.event_shell       = self.on_shell
        self.debloater.event_download    = self.on_download
        self.debloater.event_downloading = self.on_downloading
        self.debloater.event_debloat     = self.on_debloat
        self.__add_components(self.win, color_pair_offset)


    def killAll(self,etype, value, tb): # Ignore this cr@p for now :P | top 10 ways to handle an error in a thread lol | https://stackoverflow.com/a/76071252/11465149
        if isinstance(self.feedback, str):
            print(self.feedback)
            return
        import traceback
        traceback.print_tb(self.feedback.exc_traceback)


    def __exit_with_reason(self, msg): # thread exiting | https://stackoverflow.com/questions/323972
        from os import kill, getpid
        from signal import SIGINT
        import sys
        uc.endwin()
        self.feedback  = msg
        sys.excepthook = self.killAll
        kill(getpid(), SIGINT)


    def __print_result_for(self, device, output):
        if output:
            self.textbox_instructions.text = '│ ✓  [DONE]\n' + self.textbox_instructions.text
        else:
            self.textbox_instructions.text = f'│ ✗  [FAILED] No available debloating-list for "{device.type_identifier}" under "{device.config}"\n' + self.textbox_instructions.text
        self.refresh()


    def __get_len_of_int(self, num): return int(log10(num))+1 if not num == 0 else 0


    def __validate_feedback(self, repos): # TODO: Expand
        if not (1 <= int(self.feedback) <= len(repos)):
            self.textbox_instructions.text = f'│ ✗  [INVALID] Out of range INPUT {self.feedback}\n' + self.textbox_instructions.text
            self.feedback = ''
            self.refresh()
            return True
        return False


    feedback = ''
    def __choose_available_repo_if_needed_for(self, device): # WHY SUCH A LONG NAME FOR AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        if device.locally or device.config != g.SERVER_REPO: return None # aahh whatever double checking for g.SERVER_REPO for no reason because I HAVE NO TIME TO EVEN THINK CLEARLY! F@CKING MONEY
        self.feedback = '' # this line was above, just in case, a reminder lol
        self.textbox_instructions.text = f'│ ○  Gathering available repositories\n' + self.textbox_instructions.text
        self.refresh()
        repos = device.get_available_repos()
        if not repos: return None # None because it is being handled by DeviceOverlay later and we don't want to interapt the debloating proccess of the next devices in case there is a config for them | self.__exit_with_reason(f'No available debloating-list for "{device.type_identifier}"')
        digit_len_of_most_started_repo = self.__get_len_of_int(repos[0][0])
        i = len(repos)
        for repo in reversed(repos):
            stars = repo[0]
            digit_len_of_repo = self.__get_len_of_int(stars)
            self.textbox_instructions.text = f'│ ★  {i}. ' + f'[{stars} ' + ' '* (digit_len_of_most_started_repo - digit_len_of_repo) + f'Stars] "{repo[2].strip()}"\n' + self.textbox_instructions.text 
            i -=1
        self.label_device.text = f'⟡ Select a debloating-list for {device.type_identifier}:'; self.refresh()
        while not self.feedback or self.__validate_feedback(repos) : sleep(1) # I thought about it before looking into there https://superfastpython.com/thread-wait-for-result/ | feedback - no need for validation if int as of now
        repo = repos[int(self.feedback)-1]
        self.textbox_instructions.text = f'│ ○  [LOADING] "{repo[2].strip()}"\n' + self.textbox_instructions.text; self.refresh()
        device.config = repo[1]


    def __reset_device_label_style(self):
        self.label_device.style      = uc.A_BOLD | uc.A_ITALIC
        self.label_device.color_pair = 2


    def __check_for_unauthorized_devices(self):
        self.refresh()
        devices = self.debloater.get_unauthorized_devices()
        self.label_device.color_pair = 3
        while devices: # unauthorized
            self.label_device.style = uc.A_ITALIC |  uc.A_DIM
            serials = ' ' + str( [str(d.serial) for d in devices] )
            self.lines, self.columns = uc.getmaxyx(self.win)
            l = len(serials) if len(serials) <= self.columns -4 -49 else self.columns -4 -49
            if l < len(serials) and not l < 4: 
                serials = serials[:l-3] + '..]'
            elif l < 4:
                serials = ''
            self.label_device.text  = f'Please authorize your{serials[:l]} device(s) before continuing'; self.refresh(); sleep(1)
            self.label_device.style = uc.A_BOLD; self.refresh(); sleep(1)
            devices = self.debloater.get_unauthorized_devices()


    def __async_begin(self):
        self.textbox_instructions.text = '│ ○  Checking for available devices'
        self.__check_for_unauthorized_devices()
        devices = self.debloater.get_devices()
        if not devices: self.__exit_with_reason('No connected devices found')
        for device in devices:
            self.__reset_device_label_style()
            self.__choose_available_repo_if_needed_for(device) 
            self.label_device.text = f'⟡ Debloating, {device.type_identifier}:'; self.refresh()
            self.__print_result_for(device, next(self.debloater.debloat(device)))


    def begin(self):
        threading.excepthook = self.__exit_with_reason # ahh whatever
        t = threading.Thread(target=self.__async_begin)
        t.daemon = True
        t.start()


    def handle_resize(self, redraw_parent=True):
        self.label_info          .handle_resize(False)
        self.label_device        .handle_resize(False)
        self.textbox_instructions.handle_resize(False)
        if redraw_parent:
            uc.touchwin(self.win)


    __feedback = ''
    escape_event_consumed = False
    def __reset_feedback(self):
            self.__feedback       = ''
            self.label_info.style = uc.A_DIM
            self.label_info.text  = '● Press ESC to exit  ░▒▓██▓▒░ HEXAPTERYGON 2023 ░▒▓██▓▒░'


    def handle_feedback_over_thread(self, event):
        self.escape_event_consumed = False
        if  47 < event < 58: 
            self.__feedback      += uc.RCCHAR(event) 
            self.label_info.style = uc.A_BOLD
            self.label_info.text  = f'INPUT: {self.__feedback}'
        elif self.__feedback and event == 27: 
            self.escape_event_consumed = True
            self.__reset_feedback()
        elif event == uc.KEY_BACKSPACE:
            if self.__feedback:
                self.__feedback      = self.__feedback[:-1]
                self.label_info.text = f'INPUT: {self.__feedback}'
            else:
                self.__reset_feedback()
        elif event in (uc.KEY_ENTER, 10):
            self.feedback = self.__feedback
            self.__reset_feedback()


    def handle_events(self, event, redraw_parent=True):
        if event == uc.KEY_RESIZE: self.handle_resize(redraw_parent)
        if not self.is_focused: return
        self.textbox_instructions.handle_events(event)
        self.handle_feedback_over_thread(event)


    def refresh(self):
        uc.wrefresh(self.win) 
        self.label_info          .refresh()
        self.label_device        .refresh()
        self.textbox_instructions.refresh()

