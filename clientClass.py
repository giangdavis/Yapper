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
            contents = "$file " + filename +  " " + username 
            for line in a:
                contents = contents + line
            # print(contents)
            return contents
            f.close()
        except FileNotFoundError:
            print("\033[A                             \033[A")
            print('File does not exist.\n')
        return "" 

    def receiveFile(self, msg):
        msg = msg.split('\n', 1) # splits the message into two, header to the left  and contents to the right  
        header =  msg[0] # header
        contents =  msg[1] # contents 
        header = header.split(' ')
        sender  = header[0].lstrip('$')  #  get the senders name
        filename =  header[2] # get  the file name 
        #print('sender=  ' +  sender)
        # print('\nfilename: ' +  filename)
        # print('\ncontents:' + contents)
        try:
            f = open(filename, "x")
            f.write(contents)
            f.close()
            print(sender + " just sent you the file: " + filename + '\n')
        except FileExistsError:
            print(sender + " tried to send you a file, but you already have it. \n")
        return ""

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
                                sys.stdout.write("Disconnected from the server.\n")
                                self.socket.close()
                                sys.exit()  # successful termination
                            elif "$file" in msg:
                                fileCheck =  msg.split(" ")
                                if fileCheck[1] == '$file':
                                    msg = self.receiveFile(msg)
                            elif "You have successfully connected to the Lobby!!! What is your name?" in msg:
                                first = True
                            elif msg == "Username setting unsuccessful. Connect Again!":
                                #sys.stdout.write(msg)
                                self.socket.close()
                                sys.exit(2)
                                #raise Exception("Username setting unsuccessful")
                            msg = msg + '\n'
                            sys.stdout.write(msg)
                            sys.stdout.flush()
                        else:  # msg contained 0 bytes, disconnected
                            print('Connection closed!')
                            self.socket.close()
                            sys.exit()  # find error code
                    else:  # std in detected, send msg to server
                        if first == True:
                            newMsg = '$newuser ' + sys.stdin.readline()
                            first = False
                        else:
                            newMsg = sys.stdin.readline()
                            if newMsg[0:5] == "$file":
                                msgArr = newMsg.split(" ")
                                if len(msgArr) == 3:
                                    new =  self.openFile(msgArr[1], msgArr[2])
                                    if new != "": 
                                        newMsg = new
                        newMsg = newMsg.rstrip()
                        self.socket.sendall(newMsg.encode())
                        print("\033[A                                                                                                                                                           \033[A")
                        # sys.stdout.flush()
        except SystemExit as usernameError:
            if usernameError.code == 2:
                print("Username setting unsuccessful")

    def start(self, ip):
        try:
            self.socket.connect((ip, PORT))
        except Exception as e:
            sys.stdout.write("Failed to connect to the server.")
            sys.exit()

        self.runChat()