class User:
    def __init__(self, socket, name):
        socket.setblocking(0)
        self.socket = socket
        self.name = name
        self.rooms = {}  # {RoomName : Bool} Bool = user is sending msgs to room

    def setName(self, newName):
        self.name = newName

    def fileno(self):
        return self.socket.fileno()

    def getName(self):
        return self.name

    def addRoom(self, room):
        self.rooms[room] = False

    def printRooms(self):
        for x in self.rooms:
            print(x.name)

    def leaveRoom(self, roomName):
        self.rooms.pop(roomName)
