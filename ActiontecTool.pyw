#!/bin/python3

'''
		Copyright (C) 2014 Alexander B. Libby

 ActiontecTool is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation.

 This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License (version 3) for more details.

 You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/gpl.txt>.
'''

from telnetlib import Telnet
from time import sleep
from tkinter import Tk, LabelFrame, Button, Entry, Scrollbar, \
  Text, Label, LEFT, RIGHT, END, INSERT, VERTICAL, X, Y, BOTH, YES

SLEEPTIME = 0.15 # Time to hold for telnet output.

def debug(string):
    """Print string if python was started with the -O flag."""
    if not __debug__:
        print(string)

class MainGUI(Tk):

    def __init__(self, updateTime=0):
        """"""
        self.update = [updateTime, updateTime>0]
        try:
            self.telnet = Telnet("192.168.0.1", 23, 5)
        except:
            debug("Can't Login!")
            raise TimeoutError("Can't Login!")
        super().__init__()
        debug("WebLogGUI")
        self.title("Actiontec Config")
        self.minsize(700, 130)
        # Make the (login as) LabelFrame
        self.lblfLogin = MainGUI.theme(LabelFrame(self, text="Login As"))
        lblUsername = MainGUI.theme(Label(self.lblfLogin, text="UserName:"))
        lblUsername.pack(side=LEFT, padx=10)
        self.entUsername = MainGUI.theme(Entry(self.lblfLogin))
        self.entUsername.insert(0, "admin")
        self.entUsername.pack(side=LEFT)
        lblPassword = MainGUI.theme(Label(self.lblfLogin, text="PassWord:"))
        lblPassword.pack(side=LEFT, padx=10)
        self.entPassword = MainGUI.theme(Entry(self.lblfLogin, show='*'))
        self.entPassword.pack(side=LEFT)
        btnLogin = MainGUI.theme(Button(
          self.lblfLogin, text="Login", command=self.start_telnet))
        btnLogin.pack(side=LEFT, padx=10)
        self.lblfLogin.pack(fill=X)
        # Make the (log settings) LabelFrame
        lblfSettings = MainGUI.theme(LabelFrame(self, text="Log Settings"))
        self.btnExit = MainGUI.theme(Button(
          lblfSettings, text="Exit Log", width=15, command=self.destroy))
        self.btnReset = MainGUI.theme(
          Button(lblfSettings, width=15, command=self.reset_log))
        self.btnDisable = MainGUI.theme(Button(
          lblfSettings, text="Disable Log", width=15, command=self.disable_log))
        self.btnUpdate = MainGUI.theme(Button(
          lblfSettings, text="Update Log", width=15, command=self.update_log))
        lblfSettings.pack(side=LEFT, fill=Y)
        # Make the (view log) LabelFrame
        self.btnExit.pack()
        lblfLog = MainGUI.theme(LabelFrame(self, text="View Log"))
        self.txtLog = MainGUI.theme(Text(
          lblfLog, font=("Purisa",12), width=50, state='disabled'))
        self.txtLog.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollLog = MainGUI.theme(
          Scrollbar(lblfLog, orient=VERTICAL, command=self.txtLog.yview))
        self.txtLog.config(yscrollcommand=scrollLog.set)
        scrollLog.pack(side=RIGHT, fill=Y)
        lblfLog.pack(side=LEFT, fill=BOTH, expand=YES)

    def __enter__(self):
        """"""
        return self

    def __exit__(self, type, value, traceback):
        """"""
        debug("Exit")
        if value:
            #self.destroy()
            debug("Fatal Bug")
            root = Tk()
            root.title("Fatal Bug")
            note = "Fatal Bug: " + str(value)
            lblnote = Label(root, font=("Purisa",24), text=note)
            lblnote["fg"] = "#d00000"
            lblnote["bg"] = "#383635"
            lblnote.pack()
            root.mainloop()
        self.stop_telnet()

    def __auto_update_log(self):
        """"""
        debug("Auto Update")
        self.update_log()
        if self.update[1]:
            self.after(self.update[0]*1000, self.__auto_update_log)

    @staticmethod
    def theme(control):
        """"""
        item = str(type(control)).split("'")[1].split(".")[1]
        debug("Set {0} Theme".format(item))
        if type(control) == Button:
            control["fg"] = "#FFFFFF"
            control["bg"] = "#575552"
        elif type(control) == Scrollbar:
            control["bg"] = "#575552"
        elif type(control) in [LabelFrame, Label]:
            control["fg"] = "#A2A09C"
            control["bg"] = "#383635"
        elif type(control) in [Entry, Text]:
            control["fg"] = "#FFFFFF"
            control["bg"] = "#A2A09C"
        elif isinstance(control, Tk):
            control["bg"] = "#383635"
        return control

    def start_telnet(self):
        """"""
        debug("Start Telnet")
        self.telnet.read_until(b"login: ")
        self.telnet.write(self.entUsername.get().encode() + b"\n")
        self.telnet.read_until(b"Password: ")
        self.telnet.write(self.entPassword.get().encode() + b"\n")
        if b"# " in self.telnet.read_until(b"# ", 1):
            debug("Login Valid")
            self.lblfLogin.pack_forget()
            self.telnet.write(b"cd /var/tmp\n")
            self.__auto_update_log()
        else:
            debug("Login Invalid")

    def stop_telnet(self):
        """"""
        debug("Stop Telnet")
        if self.update[1]:
            time = self.update[0]
        else:
            time = 0
        sleep(SLEEPTIME + time)
        self.telnet.write(b"exit\n")

    def get_log(self):
        """"""
        debug("Get Log")
        sleep(SLEEPTIME)
        self.telnet.write(b"cat log_web_activity\n")
        sleep(SLEEPTIME)
        self.telnet.expect([b"cat log_web_activity\r\n"])
        output = self.telnet.read_very_eager()
        output = output.decode().replace('\r', '').replace('#', '')
        return output.replace("192.168.0.2   ", '')

    def update_ui(self):
        """"""
        debug("Update UI")
        if len(self.get_log()) > 1:
            self.btnDisable.pack()
            self.btnUpdate.pack()
            self.btnReset["text"] = "Clear Log"
            self.btnReset.pack()
            if "Log Is Empty!" in self.txtLog.get('1.0', 'end'):
                self.btnReset.pack_forget()
            else:
                self.btnReset["text"] = "Clear Log"
        else:
            self.btnReset["text"] = "Enable Log"
            self.btnReset.pack()
            self.btnDisable.pack_forget()
            self.btnUpdate.pack_forget()

    def update_log(self):
        """"""
        debug("Update Log")
        self.txtLog['state'] = 'normal'
        self.txtLog.delete(1.0, END)
        note = "No such file or directory"
        output = self.get_log()
        if note in output:
            output = "Log Is Empty!"
        elif ' ' == output:
            output = "Log Is Disabled!" 
        self.txtLog.insert(INSERT, output)
        self.update_ui()
        self.txtLog['state'] = 'disabled'

    def disable_log(self, update=True):
        """"""
        debug("Disable Log")
        self.reset_log(False)
        self.update[1] = False
        sleep(SLEEPTIME)
        self.telnet.write(b"ln -s /dev/null log_web_activity\n")
        if update:
            self.update_log()

    def reset_log(self, update=True):
        """"""
        sleep(SLEEPTIME)
        self.telnet.write(b"rm log_web_activity\n")
        if not self.update[1]:
            self.update[1] = True
        if update:
            debug(self.btnReset["text"].title())
            self.update_log()
        else:
            debug("Reset Log")

    def mainloop(self):
        """"""
        debug("Main Loop")
        super().mainloop()

if __name__ == "__main__":
    with MainGUI(10) as gui:
        gui.mainloop()
