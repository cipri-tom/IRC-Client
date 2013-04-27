from Tkinter import *

class Dialog(Toplevel):
   """ Class template to wrap any type of modal dialog, which doesn't create confusion
   for the user because it makes the parent window wait for it. """
   def __init__(self, parent, title = None):
      Toplevel.__init__(self, parent)
      self.transient(parent)        # associate with parent window;
                                    # won't show up as icon in Window manager

      if title:
         self.title(title)

      self.parent = parent
      self.result = None

      body = Frame(self)
      self.initial_focus = self.body(body)      # set the element with initial focus
      if not self.initial_focus:                # or the frame itself if none is set
         self.initial_focus = self
      self.initial_focus.focus_set()

      body.pack(padx = 5, pady = 5)

      self.buttonbox()              # add default buttons; override for different behaviour
      self.grab_set()               # make the dialog modal

      self.protocol("WM_DELETE_WINDOW", self.cancel)

                                    # set geometry relative to parent
      self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, \
                                parent.winfo_rooty() + 50))

      self.wait_window(self)
   #  ~constructor

   def body(self, master):
      """ creates dialog body. return widget that should have initial focus
          this method should be overridden """
      pass

   def buttonbox(self):
      """ add a standard button box. override if they are not wanted """
      box = Frame(self)

      okButton = Button(box, text = "OK", width = 10, command = self.ok, \
                        default = ACTIVE)       # make ok button default
      cancelButton = Button(box, text = "Cancel", width = 10, command = self.cancel)
      okButton.pack(side = LEFT, padx = 5, pady = 5)
      cancelButton.pack(side = LEFT, padx = 5, pady = 5)

      self.bind("<Return>", self.ok)          # add functionality for ENTER
      self.bind("<Escape>", self.cancel)      # and ESCAPE keys

      box.pack()
   #  ~buttonbox

   def ok(self, event = None):
      """ behaviour for okButton """
      if not self.validate():
         self.initial_focus.focus_set()         # put focus back
         return

      self.withdraw()
      self.update_idletasks()
      self.apply()                 # extract the results
      self.cancel()                # close the windows

   def cancel(self, event = None):
      """ behaviour for cancelButton """
      self.parent.focus_set()      # put focus back to parent
      self.destroy()               # close the window

   def validate(self):
      """ should be overriden to carry out validation """

   def apply(self):
      """ should be overriden to do something with the information
          like storing it for access"""
      pass
