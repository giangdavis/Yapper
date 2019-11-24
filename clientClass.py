import socket, select, sys

PORT = 50000
MAX_MESSAGE_LENGTH = 4096

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connectionList = [sys.stdin, self.socket]

    def __del__(self):
        self.name = ""

    def runChat(self):
        first = False
        while True:
            readables, _, _ = select.select(self.connectionList, [], [])
            for notifiedSocket in readables:
                if notifiedSocket is self.socket: # new msg
                    encodedMsg = notifiedSocket.recv(MAX_MESSAGE_LENGTH)
                    msg = encodedMsg.decode()
                    if msg: # incoming message
                        if msg == '$$exit':
                            sys.stdout.write("Successfully disconnected from the server.\n")
                            self.socket.close()
                            sys.exit() # successful termination
                        elif "You have successfully connected to the Lobby!!! What is your name?" in msg:
                            first = True
                        sys.stdout.write(msg)
                        sys.stdout.flush()
                    elif msg == "Username setting unsuccessful. Connect Again!":
                        sys.stdout.write(msg)
                        self.socket.close()
                        sys.exit(2)
                    else: # msg contained 0 bytes, disconnected
                        print('Connection closed!')
                        self.socket.close()
                        sys.exit() # find error code
                else: #std in detected, send msg to server
                    if first == True:
                        newMsg = '$newuser ' + sys.stdin.readline()
                        first = False
                    else:
                        newMsg = sys.stdin.readline()
                    self.socket.sendall(newMsg.encode())
                    sys.stdout.flush()

    def start(self, ip):
        try:
            self.socket.connect((ip, PORT))
        except Exception as e:
            sys.stdout.write("Failed to connect to the server.")
            sys.exit()

        self.runChat()