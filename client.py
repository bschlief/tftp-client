import socket
import struct
import argparse

PACKET_TIMEOUT = 1.0
OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5

DATA_SIZE = 512


class TransferException(Exception):
    pass


class FileReader:
    """
    Retrieve a given filename from a tftp server on the given host and port in netascii mode.
    """

    def __init__(self, filename, host, port):
        self.filename = filename
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(PACKET_TIMEOUT)
        self.host = host
        self.port = port
        self.mode = 'netascii'
        self.block_number = 0
        self.contents = ''

    def send(self, data):
        """
        Convenience method to send data to our socket
        """
        self.sock.sendto(data, (self.host, self.port))

    def send_rrq(self):
        """
        Send a read request for this file reader's filename.
        """
        fmt = '!H{}sB{}sB'.format(len(self.filename), len(self.mode))
        data = struct.pack(fmt, OP_RRQ, self.filename, 0, self.mode, 0)
        self.send(data)

    def send_ack(self):
        """
        Send an ACK to the tftp-server.
        """
        fmt = '!HH'
        data = struct.pack(fmt, OP_ACK, self.block_number)
        self.send(data)

    def get_opcode(self, packed_opcode):
        """
        Gets an op code out of a packed string.
        """
        opcode = struct.unpack("!H", packed_opcode)
        return opcode[0]

    def get_block_number(self, packed_block_number):
        """
        Gets an op code out of a packed string.
        """
        opcode = struct.unpack("!H", packed_block_number)
        return opcode[0]

    def append_data_to_contents(self, raw_data):
        """
        Receive a chunk of raw udp data, and append it to the internal string buffer

        Returns True if this data received was 512 byes long. That indicates that more packets are to come.
        Returns False if the packet was 511 or fewer bytes. That signals that the transfer is complete.
        """
        fmt = '!HH{}s'.format(len(raw_data)-4)
        opcode, block_number, data = struct.unpack(fmt, raw_data)
        self.contents += data
        self.block_number += 1
        if len(data) == DATA_SIZE:
            return True
        return False

    def recv(self):
        """
        Get the raw data from the server. Change over to the tftp-server's
        requested port upon receiving the new address.

        Returns True if more data is expected, otherwise returns False.
        """
        raw_data, (self.host, self.port) = self.sock.recvfrom(516)

        opcode = self.get_opcode(raw_data[0:2])
        if opcode == OP_ERROR:
            raise TransferException(raw_data)

        if opcode == OP_DATA:
            block_number = self.get_block_number(raw_data[2:4])

            # If this block isn't the expected one, go back to listening
            if block_number != self.block_number+1:
                return True

        return self.append_data_to_contents(raw_data)

    def write_contents_to_file(self):
        """
        Write the stored contents to a file.
        """
        with open(self.filename, "w") as f:
            f.write(self.contents)

    def perform_transfer(self):
        """
        Initiate the transfer, and while we still have data yet to come, send acknowledgments back.
        Write file contents to disk after we've received all data.
        """
        self.send_rrq()
        try:
            while self.recv():
                self.send_ack()
            self.write_contents_to_file()
        except TransferException, te:
            print te


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A simple netascii-only tftp client')
    parser.add_argument('-H', '--host', type=str, default='localhost', help='TFTP server hostname. Defaults to localhost.')
    parser.add_argument('-p', '--port', type=int, default=69, help='TFTP server port. Defaults to 69.')
    parser.add_argument('filename', type=str)
    args = parser.parse_args()

    reader = FileReader(args.filename, args.host, args.port)
    reader.perform_transfer()
