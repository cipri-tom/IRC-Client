"""

IRC client exemplar.

"""

import sys
from ex3utils import Client
from Tkinter import *
import tkMessageBox

import time

class ClientGUI(Client):
   def __init__(self, master):
      Client.__init__(self)
      self.parent = master
      master.resizable(0, 0)

      frame = Frame(master, height = 576, width = 768)
      frame.pack()

      master.protocol("WM_DELETE_WINDOW", self.onExit)

   def onMessage(self, socket, message):
      # *** process incoming messages here ***
      print message
      return True

   def onExit(self):
      if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
         self.parent.destroy()



# Parse the IP address and port you wish to connect to.
ip = sys.argv[1]
port = int(sys.argv[2])
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
