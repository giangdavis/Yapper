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
    
    def openFile(self, path, username): 
        filename = path
        print(filename)
        try:
            f = open(filename.strip('\n'))
            a = f.readlines()
            contents = "$file " + username 
            for line in a:
                contents = contents + line
            print(contents)
            f.close()
        except FileNotFoundError:
            print('File does not exist.\n')
        
        return contents 

    def runChat(self):
        first = False
        try:
            while True:
                readables, _, _ = select.select(self.connectionList, [], [])
                for notifiedSocket in readables:
                    if notifiedSocket is self.socket:  # new msg
                        encodedMsg = notifiedSocket.recv(MAX_MESSAGE_LENGTH)
                        msg = encodedMsg.decode()
                        if msg:  # incoming message
                            #try:
                            if msg == '$$exit':
                                sys.stdout.write("Successfully disconnected from the server.\n")
                                self.socket.close()
                                sys.exit()  # successful termination
                            elif "You have successfully connected to the Lobby!!! What is your name?" in msg:
                                first = True
                            elif msg == "Username setting unsuccessful. Connect Again!":
                                #sys.stdout.write(msg)
                                self.socket.close()
                                sys.exit(2)
                                #raise Exception("Username setting unsuccessful")
                            msg = msg + '\n\n'
                            sys.stdout.write(msg)
                            sys.stdout.flush()
                        else:  # msg contained 0 bytes, disconnected
                            print('Connection closed!')
                            self.socket.close()
                            sys.exit()  # find error code
                        #except Exception as fuk:
                        #    print(fuk)
                    else:  # std in detected, send msg to server
                        if first == True:
                            newMsg = '$newuser ' + sys.stdin.readline()
                            first = False
                        else:
                            newMsg = sys.stdin.readline()
                            if newMsg[0:5] == "$file":
                                print("\033[A                             \033[A")
                                msgArr = newMsg.split(" ")
                                newMsg = self.openFile(msgArr[1], msgArr[2])
                        newMsg = newMsg.rstrip()
                        self.socket.sendall(newMsg.encode())
                        print("\033[A                             \033[A")
                        # sys.stdout.flush()
        except SystemExit as fuk:
            if fuk.code == 2:
                print("Username setting unsuccessful")

    def start(self, ip):
        try:
            self.socket.connect((ip, PORT))
        except Exception as e:
            sys.stdout.write("Failed to connect to the server.")
            sys.exit()

        self.runChat()