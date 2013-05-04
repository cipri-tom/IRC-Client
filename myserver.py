import sys
from ex3utils import Server

class MyServer(Server):

   def onStart(self):
      print "MyServer has started..."
      self.clientsNo = 0
      self.users = {}
      self.illegalChars = [' ', ':', ',', ';', ' ']
      self.commands = "REG MSG USR".split();
      self.errorMsg = {
         010 : "Illegal username",
         012 : "Username already exists",
         401 : "Unauthorized",
         400 : "Bad request",
         501 : "Not implemented"
      }

   def onStop(self):
      print "MyServer has stopped..."

   def onConnect(self, socket):
      self.clientsNo += 1
      socket.name = ''
      print "A new client has connected. Total connected clients:", \
            self.clientsNo

   def sendError(self, socket, errNo):
      socket.send("ERR %s: %s" % (str(errNo), self.errorMsg[errNo]))

   def onMessage(self, socket, message):
      #print "A new message has been received..."
      (command, sep, args) = message.strip().partition(' ')
      command = command.upper()

      #validate the command
      if not command in self.commands:
         self.sendError(socket, 501)
      elif args == '':
         self.sendError(socket, 400)

      elif command == "REG":
         #validate the username
         if any(char in args for char in self.illegalChars):
            self.sendError(socket, 010)

         #verify for duplicates
         elif args in self.users.keys():
            self.sendError(socket, 012)

         #already registered, change previous value
         elif socket.name != "":
            oldName = socket.name
            del self.users[oldName]
            socket.name = args
            self.users[args] = socket
            for user in self.users.values():
               user.send("MSG :User " + oldName + " is now known as " \
                         + args + ".")

         else:
            #store the username both on the socket and server
            socket.name = args
            self.users[args] = socket
            for user in self.users.values():
               user.send("MSG :User " + args + " has connected.")
               user.send("USR " + ' '.join(self.users.keys()))

      #user has not registered yet
      elif not socket in self.users.values():
         self.sendError(socket, 401)

      elif command == "MSG":
         (destinations, sep, msg) = args.strip().partition(':')

         #no user specified, send to all of them
         if destinations == '':
            for user in self.users.values():
               user.send("MSG %s:%s" % (socket.name, msg))

         #send just to specified users and to self
         else:
            destinations = destinations.split(',')
            reached = 0;
            failedDest = []
            for dest in destinations:
               if dest in self.users.keys():
                  self.users[dest].send("PM %s (to %s):%s" % (socket.name, \
                                                 ', '.join(destinations), msg))
                  reached += 1
               else:
                  failedDest.append(dest)

            #give feedback
            if len(failedDest) > 0:
               socket.send("PM :Oops, the following users don't exist: %s" % \
                           ', '.join(failedDest))
            if reached > 0:
               socket.send("PM %s (to %s):%s" % (socket.name, \
                                                 ', '.join(destinations), msg))

      elif command == "USR":
         #no argument, send the whole list
         if args == ',':
            socket.send("USR " + ' '.join(self.users.keys()))
         else:
            self.sendError(socket, 501)

      return True

   def onDisconnect(self, socket):
      self.clientsNo -= 1
      if socket in self.users.values():
         del self.users[socket.name]
      for user in self.users.values():
         user.send("MSG :User %s has left the conversation..." % socket.name)
         user.send("USR " + ' '.join(self.users.keys()))


if len(sys.argv) != 3:
   print "Not enough arguments ..."
   print "Usage: python myserver.py ip port"
   exit()


ip = sys.argv[1]
port = int(sys.argv[2])

server = MyServer()

server.start(ip, port)
