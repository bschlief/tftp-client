#!/usr/bin/env python
import unittest
import mock
import struct
from client import FileReader, OP_RRQ, OP_DATA, OP_ACK, OP_ERROR, TransferException
import subprocess


class TestFileReader(unittest.TestCase):

    def setUp(self):
        """
        Set up a file reader that wants to connect to localhost:69

        All communications are mocked.
        """
        self.file_reader = FileReader(
            filename='readme.txt',
            host='localhost',
            port='69'
        )
        self.file_reader.sock = mock.Mock()
        self.location_tuple = (self.file_reader.host, self.file_reader.port)

    def test_send_rrq(self):
        """
        Test sending a read request is formatted properly
        """
        self.file_reader.send_rrq()
        self.file_reader.sock.sendto.assert_called_once_with(
            struct.pack("!H10sB8sB", OP_RRQ, "readme.txt", 0, "netascii", 0),
            self.location_tuple
        )

    def test_send_ack(self):
        """
        Test sending an ACK is formatted properly.
        """
        self.file_reader.send_ack()
        self.file_reader.sock.sendto.assert_called_once_with(
            struct.pack("!HH", OP_ACK, self.file_reader.block_number),
            self.location_tuple
        )

    def test_recv_error(self):
        """
        Receving an error from the server raises a transfer exception
        """
        error_data = struct.pack("!H14s", OP_ERROR, "File not found")
        self.file_reader.sock.recvfrom.return_value = (error_data, self.location_tuple)
        self.assertRaises(TransferException, self.file_reader.recv)

    def test_recv_two_packets(self):
        """
        Receiving two packets concatenates their results together.
        """
        a_lot_of_ones = "1" * 512
        slightly_fewer_twos = "2" * 511

        good_data_block_1 = struct.pack("!HH512s", OP_DATA, 1, a_lot_of_ones)
        self.file_reader.sock.recvfrom.return_value = (good_data_block_1, self.location_tuple)
        self.file_reader.recv()
        self.assertEqual(self.file_reader.block_number, 1)
        self.assertEqual(self.file_reader.contents, a_lot_of_ones)

        good_data_block_2 = struct.pack("!HH511s", OP_DATA, 2, slightly_fewer_twos)
        self.file_reader.sock.recvfrom.return_value = (good_data_block_2, self.location_tuple)
        self.file_reader.recv()
        self.assertEqual(self.file_reader.block_number, 2)
        self.assertEqual(self.file_reader.contents, a_lot_of_ones + slightly_fewer_twos)

    def test_recv_duplicate_packet(self):
        """
        Verify that receiving data with a block ID already seen isn't added to the file twice.
        """
        a_lot_of_ones = "1" * 512
        slightly_fewer_twos = "2" * 511

        data_block_1 = struct.pack("!HH512s", OP_DATA, 1, a_lot_of_ones)
        data_block_2 = struct.pack("!HH511s", OP_DATA, 2, slightly_fewer_twos)

        self.file_reader.sock.recvfrom.return_value = (data_block_1, self.location_tuple)
        self.file_reader.recv()
        self.file_reader.recv()

        self.file_reader.sock.recvfrom.return_value = (data_block_2, self.location_tuple)
        self.file_reader.recv()

        self.assertEqual(len(self.file_reader.contents), len(a_lot_of_ones + slightly_fewer_twos))
        self.assertEqual(self.file_reader.contents, a_lot_of_ones + slightly_fewer_twos)


class TestExitCode(unittest.TestCase):

    def test_exit_code(self):
        """
        This test should fail either because
        (1) You don't have a tftp server running on port 6969
        (2) You don't have a file called 'thisfiledoesnotexist.txt' being
            served by the aforementioned tftp server
        """
        result = subprocess.call(["./client.py", "-H", "localhost", "-p", "6969", "thisfiledoesnotexist.txt"])
        self.assertEqual(result, 1)


if __name__ == "__main__":
    print unittest.main()