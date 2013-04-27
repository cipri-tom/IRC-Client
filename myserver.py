import sys
from ex3utils import Server

class MyServer(Server):
   
   def onStart(self):
      print "MyServer has started..."
      self.clientsNo = 0
      self.users = {}
      self.illegalChars = [' ', ':', ',', ';']
      self.commands = "REG MSG USR".split();
   
   def onStop(self):
      print "MyServer has stopped..."
   
   def onConnect(self, socket):
      self.clientsNo += 1
      socket.name = ''
      print "A new client has connected. Total connected clients:", \
            self.clientsNo
      
   
   def onMessage(self, socket, message):
      #print "A new message has been received..."
      (command, sep, args) = message.strip().partition(' ')
      command = command.upper()
      
      #validate the command
      if not command in self.commands:
         socket.send("ERR 501")
      elif args == '':
         socket.send("ERR 400")

      elif command == "REG":
         #validate the username
         if any(char in args for char in self.illegalChars):
            socket.send("ERR 010");

         #verify for duplicates
         elif args in self.users.keys():
            socket.send("ERR 012")

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
      
      #user has not registered yet
      elif not socket in self.users.values():
         socket.send("ERR 401")

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
            socket.send("USR " + ','.join(self.users.keys()))
         else:
            socket.send("ERR 501")
      
      return True
   
   def onDisconnect(self, socket):
      self.clientsNo -= 1
      if socket in self.users.values():
         del self.users[socket.name]
      print "A client has disconnected. Total connected clients:", \
            self.clientsNo

      
ip = sys.argv[1]
port = int(sys.argv[2])

server = MyServer()

server.start(ip, port)
