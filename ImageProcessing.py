import cv2
import socket
import pickle
import struct


def send(sock, message):
    data = pickle.dumps(message)
    sock.sendall(struct.pack("L", len(data)) + data)


def basic_recv(conn, size):
    size_left = size
    msg = ""
    while size_left > 0:
        if msg != "":
            msg = msg + conn.recv(size_left)
        else:
            msg = conn.recv(size_left)
        size_left = size - len(msg)
    return msg


def recv(conn):
    size_size = struct.calcsize("L")
    data_size = struct.unpack("L", basic_recv(conn, size_size))[0]
    data = basic_recv(conn, data_size)
    return pickle.loads(data)


local_host = "127.0.0.1"
port = 8083
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
is_server = False
while True:
    answer = input("S for Server, C for Client: ")
    if answer.capitalize() == "S":
        sock.bind((local_host, port))
        print("Waiting for a client...")
        sock.listen(1)
        conn, address = sock.accept()
        print("Successfully created the server!")
        while True:
            frame, stop = recv(conn)
            if frame is not None:
                cv2.imshow("Server Frame", frame)
            if stop:
                break
            cv2.waitKey(1)
        conn.close()
        break
    elif answer.capitalize() == "C":
        sock.connect((local_host, port))
        print("Successfully connected to the server!")
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            if ret:
                send(sock, (frame, False))
                cv2.imshow("Client Frame", frame)
            else:
                send(sock, (None, False))
            if ord("q") == cv2.waitKey(1) & 0xFF:
                send(sock, (None, True))
                break
        capture.release()
        break
cv2.destroyAllWindows()
sock.close()
