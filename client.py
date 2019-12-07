from clientClass import Client
import sys

client = Client()

# AWS
# client.start('54.88.160.21')

arguments = len(sys.argv) - 1
if arguments == 1:
    hostAddr = sys.argv[1]
else:
    hostAddr = '127.0.0.1'  # if no argument, default to local hos

client.start(hostAddr)