"""

IRC client exemplar.

"""

import sys
from ex3utils import Client
from Tkinter import *
import tkMessageBox
import mydialog

import time

class InitialDialog(mydialog.Dialog):
   def body(self, master):
      Label(master, text = "Server:").grid(row = 0, sticky = W)
      Label(master, text = "Port:").grid(row = 1, sticky = W)
      Label(master, text = "User name:").grid(row = 2, sticky = W)

      self._error    = Label(master).grid(row = 3, columnspan = 2, sticky = W)
      self._server   = Entry(master)
      self._port     = Entry(master)
      self._username = Entry(master)

      self._server.insert(0, "localhost")
      self._port.insert(0, "8090")

      # arrange them nicely in a grid
      self._server.grid(column = 1, row = 0)
      self._port.grid(column = 1, row = 1)
      self._username.grid(column = 1, row = 2)

      return self._username          # this will have initial focus

   def validate(self):
      illegalChars = [' ', ':', ',', ';']
      if any(char in self._username.get() for char in illegalChars):
         #self._error["text"] = "Illegal characters in username"
         return False
      return True


   def apply(self):
      self.result = (self._server.get(), int(self._port.get()), self._username.get())


class ClientGUI(Client):
   def __init__(self, master):
      Client.__init__(self)
      self.started = False
      self.parent = master
      master.resizable(0, 0)

      frame = Frame(master, height = 576, width = 768)
      frame.pack()

      result = InitialDialog(master, "Connection settings").result
      if not result:
         self.onExit()
         return

      self.started = True
      self.start(ip, port)
      master.protocol("WM_DELETE_WINDOW", self.onExit)

   def onMessage(self, socket, message):
      # *** process incoming messages here ***
      print message
      return True

   def onExit(self):
      if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
         self.parent.destroy()
         if self.started: self.stop()



# Parse the IP address and port you wish to connect to.
# ip = sys.argv[1]
# port = int(sys.argv[2])
#screenName = sys.argv[3]

root = Tk()
client = ClientGUI(root)
root.mainloop()

"""
# Create an IRC client.
client = IRCClient()

# Start server
client.start(ip, port)

# *** register your client here, e.g. ***
client.send('REG %s' % screenName)

while client.isRunning():
   try:
      command = raw_input("> ").strip()
      # *** process input from the user in a loop here ***
      # *** use client.send(someMessage) to send messages to the server
   except:
      client.stop();

client.stop()
"""

