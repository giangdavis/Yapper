import datetime

class Room:
    def __init__(self, name, password=""):
        self.users = []   # a list of sockets
        self.name = name
        self.password = password

    def __del__(self):
        print("deleted room: " + self.name + '\n')

    def addUser(self, user):
        self.users.append(user)

    def clean(self):
        for user in self.users:
            user.socket.sendall(b'The server has shut down :(')
            user.socket.close()

    def printUsers(self):  # for server use only
        print("Users in room: " + self.name + " ")
        for x in self.users:
            print(x.getName() + ' ')

    def broadcast(self, user, msg):
        time = datetime.datetime.now()
        timeStr = time.strftime("%I") + ":" + time.strftime("%M") + " " + time.strftime("%p ")
        for x in self.users:
            x.socket.sendall(b'From Room: ' + self.name.encode() + b'\n' + timeStr.encode() +
                             user.name.encode() + b': ' + msg.encode())

    def removeUser(self, user): # user leaving the room
        self.users.remove(user)
        if len(self.users) != 0:
            self.broadcast(user.name + " has left the room\n")
            return 1
        return 0

    def printMembers(self, user):  # to send the client users of room
        first = True
        for x in self.users:
            if first == True:
                msg = x.name
                first = False
            else:
                msg = msg + ", " + x.name
        user.socket.sendall(b'The users in the room ' + self.name.encode() + b' are: ' + msg.encode())