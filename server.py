import socket
import sys
import select
import serverClass

arguments = len(sys.argv) - 1
if arguments == 1:
    hostAddr = sys.argv[1]
else:
    hostAddr = '127.0.0.1'  # if no argument, default to local host

s = serverClass.Server()
s.run(hostAddr)
