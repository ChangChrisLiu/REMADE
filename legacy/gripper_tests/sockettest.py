import socket
import struct

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("10.125.144.125",31001))
serversocket.listen(5)

HOST = "169.254.99.10"
PORT = 30002
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))