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
      illegalChars = [' ', ':', ',', ';', ' ']
      if any(char in self._username.get() for char in illegalChars):
         self._error.set("Illegal characters in username")
         return False
      return True


   def apply(self):
      self.result = (self._server.get(), int(self._port.get()), self._username.get())


class ClientGUI(Client):
   def __init__(self, master):
      Client.__init__(self)
      self.started = False          # use it to not try stopping if didn't start
      self.parent = master          # used to distroy it on exit
      master.title("TomIRC")        # app's title
      master.resizable(0, 0)        # user cannot resize it
      # master.config(width = 720, height = 526)
      # master.grid_propagate(False)  # doesn't change size because of inner elements

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
      menu.add_command(label = "               ", state = DISABLED)
      menu.add_command(label = "Connected to %s:%s as %s" % (result[0], result[1],\
                       self.name), state = DISABLED, background = "gray", \
                       font = tkFont.Font(family = "Times", weight = tkFont.BOLD,\
                              size = 10))
      menu.add_command(label = "                                         ",\
                       state = DISABLED)
      menu.add_command(label = "          Connected users           ",\
                       state = DISABLED, background = "gray", \
                       font = tkFont.Font(family = "Times", weight = tkFont.BOLD, \
                                          size = 10))
      menu.config(disabledforeground = "#777")
      self.menu = menu

      # list of connected users
      self.connectedUsers = StringVar()         # used to update the userList
      self.userList = Listbox(master, height = 15, width = 21, selectmode = MULTIPLE, \
                              listvariable = self.connectedUsers)
      self.userList.bind('<<ListboxSelect>>', self.onListSelect)
      # self.connectedUsers.set("default_user\n" + self.name)

      # add widget for displaying incoming text
      text = ScrolledText(master, height = 20, width = 75, state = DISABLED)
      text.tag_config("a", background = "lightgray")        # set a tag for the author
      text.tag_config('s', background = "darkgray")         # set a tag for the server
      self.display = text

      # add the text input
      text = ScrolledText(master, height = 5, width = 75)
      text.bind('<KeyRelease-Return>', self.sendMessage)
      text.focus_set()
      self.input = text

      # add a label to state errors and warnings
      self.infoLabel = StringVar(value = "Registered successfully...")
      label = Label(master, textvariable = self.infoLabel, anchor = W, fg = "#555")

      label.grid(row = 2, column = 0, columnspan = 2, sticky = W)
      self.display.grid(row = 0, column = 0, sticky = N)
      self.input.grid(row = 1, column = 0)
      self.userList.grid(row = 0, column = 1, rowspan = 2, sticky = N + S)
      self.send("REG " + self.name)          # register the user
      self.populateList()


   def sendMessage(self, event):
      """ sends the stripped version of the input to the server"""
      message = self.input.get("1.0", END).strip()
      if message:                            # don't send empty messages
         self.send("MSG :" + message)
      self.input.delete("1.0", END)

   def populateList(self):
      """ makes a users request to the server (USR command), after which the
      variable associated with the userList is updated in onMessage() """
      self.send("USR ,")


   def onListSelect(self, event):
      print "new selection"
      # for property, value in vars(event).iteritems():
      #    print property, ": ", value

   def aboutBox(self):
      pass

   def changeName(self):
      pass


   def onMessage(self, socket, message):
      """ the method processes the incoming messages from the server;
      depending on the command, it updates the required widget """

      ##### SHOULD CHECK MESSAGES VALIDITY OR TRUST THE SERVER? #####
      ##### Trust the server for now

      (command, sep, args) = message.partition(' ')

      if command == "MSG":                            # show the message
         (author, sep, msg) = args.partition(':')     # get the author, msg
         tag = ''
         if not author:                               # empty author means SERVER
            author = "SERVER"
            tag = 's'
         elif author == self.name:                    # highlight your name
            tag = 'a'
         self.display["state"] = NORMAL;              # insert doesn't work if DISABLED
         self.display.insert(END, author + ":", tag)
         self.display.insert(END, ' ' + msg + '\n')
         self.display["state"] = DISABLED

         pos = self.display.vbar.get()[1]             # current scrollbar position
         if pos == 1.0:
            self.display.yview(END)                   # autoscroll if at end


      elif command == "USR":                          # update users list
         self.connectedUsers.set(args)

      elif command == "ERR":
         self.infoLabel.set("Error " + args)

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
