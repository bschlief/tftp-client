import socket
import sys
import struct
import logging

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger = logging.getLogger("tftp-client")
logger.addHandler(console)

PACKET_TIMEOUT = 1.0
OP_RRQ = 1
OP_WRQ = 2
OP_ACK = 3
OP_DATA = 4
OP_ERROR = 5

class FileReader:
    def __init__(self, filename, host, port):
        self.filename = filename
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(PACKET_TIMEOUT)
        self.host = host
        self.port = port
        self.mode = 'netascii'
        self.block_number = 114

    def send(self, data):
        self.sock.sendto(data, (self.host, self.port))

    def send_rrq(self):
        logger.warning("Making a request to {}:{} for file {}".format(self.host, str(self.port), self.filename))
        fmt = '!H{}sB{}sB'.format(len(self.filename), len(self.mode))
        data = struct.pack(fmt, OP_RRQ, self.filename, 0, self.mode, 0)
        self.send(data)

    def send_ack(self):
        fmt = '!HH'
        data = struct.pack(fmt, OP_ACK, self.block_number)
        self.send(data)


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    filename = sys.argv[1]

    reader = FileReader(filename, HOST, PORT)
    reader.send_rrq()
    reader.send_ack()


