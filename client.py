import socket
import sys
import struct
import logging

logger = logging.getLogger("tftp-client")
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)

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

    def rrq(self):
        logger.debug("Making a request to {}:{} for file {}", self.host, self.port, self.filename)
        fmt = '!H{}sB{}sB'.format(len(self.filename), len(self.mode))
        data = struct.pack(fmt, OP_RRQ, self.filename, 0, self.mode, 0)
        self.sock.sendto(data, (self.host, self.port))

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    filename = sys.argv[1]

    reader = FileReader(filename, HOST, PORT)
    reader.rrq()

