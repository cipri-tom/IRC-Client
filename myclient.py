"""

IRC client exemplar.

"""

import sys
from ex3utils import Client
from Tkinter import *
import tkMessageBox
from ScrolledText import ScrolledText
import mydialog
import tkFont

import time

class InitialDialog(mydialog.Dialog):
   def body(self, master):
      Label(master, text = "Server:").grid(row = 0, sticky = W)
      Label(master, text = "Port:").grid(row = 1, sticky = W)
      Label(master, text = "User name:").grid(row = 2, sticky = W)

      self._error = StringVar()
      Label(master, text = "Please fill all the fields", textvariable = \
            self._error).grid(row = 3, sticky = EW, columnspan = 2)
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
      if not self._username.get() or not self._server.get() or not self._port.get():
         self._error.set("Please fill all fields")
         return False
      illegalChars = [' ', ':', ',', ';']
      if any(char in self._username.get() for char in illegalChars):
         self._error.set("Illegal characters in username")
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
      frame.grid()

      result = InitialDialog(master, "Connection settings").result
      if not result:
         self.onExit()
         return

      self.started = True
      self.start(result[0], result[1])
      self.name = result[2]

      master.protocol("WM_DELETE_WINDOW", self.onExit)

      # add a menu
      menu = Menu(master)
      master.config(menu = menu)

      filemenu = Menu(menu)
      menu.add_cascade(label = "File", menu = filemenu)
      filemenu.add_command(label = "Change your username", command = self.changeName)
      filemenu.add_separator()
      filemenu.add_command(label = "Quit", command = self.onExit)
      menu.add_command(label = "About", command = self.aboutBox)

      # use a menu entry as an information bar
      menu.add_command(label = "               ", state = DISABLED, columnbreak = 5)
      menu.add_command(label = "Connected to %s:%s as %s" % (result[0], result[1], self.name),\
                       state = DISABLED, background = "gray", foreground = "red",\
                       font = tkFont.Font(family = "Times", weight = tkFont.BOLD, \
                       size = 10))
      menu.config(disabledforeground = "#777")
      self.menu = menu

      # frame for connected users
      self.userList = Listbox(master)
      self.userList.grid(row = 0, column = 1, sticky = "NEWS")
      self.userList.bind('<<ListboxSelect>>', self.onSelect)
      self.userList.insert(END, "defaultUser")
      self.userList.insert(END, self.name)

      #add the text display
      text = ScrolledText(master, state = DISABLED)
      text.insert
      text.grid(row = 0, column = 0, sticky = "NEWS")

   def onSelect(self, event):
      for property, value in vars(event).iteritems():
         print property, ": ", value

   def aboutBox(self):
      pass

   def changeName(self):
      pass


   def onMessage(self, socket, message):
      # *** process incoming messages here ***
      print message
      return True

   def onExit(self):
      if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
         self.parent.destroy()
         if self.started: self.stop()

try:
   root = Tk()
   client = ClientGUI(root)
   root.mainloop()
except:
   root.destroy()
   raise


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

