import socket
import sys

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    filename = sys.argv[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(filename + "\n", (HOST, PORT))

    received = sock.recv(1024)

    print "Sent:     {}".format(filename)
    print "Received: {}".format(received)