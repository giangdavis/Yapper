class Room:
    def __init__(self, name, password=""):
        self.users = []   # a list of sockets
        self.name = name
        self.password = password

    def addUser(self, user):
        self.users.append(user)

    def printUsers(self):  # for server use only
        print("Users in room: " + self.name + " ")
        for x in self.users:
            print(x.getName() + ' ')

    def broadcast(self, msg):
        for x in self.users:
            x.socket.sendall(msg.encode())

    def removeUser(self, user):
        self.users.remove(user)

    def printMembers(self, user):  # to send the client users of room
        for x in self.users:
            member = x.name
            user.socket.sendall(member.encode())