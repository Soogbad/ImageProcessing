import cv2
import socket
import pickle
import struct


def send(sock, message):
    data = pickle.dumps(message)
    sock.sendall(struct.pack("L", len(data)) + data)


def basic_recv(conn, size):
    size_left = size
    msg = conn.recv(size_left)
    while size_left > 0:
        size_left = size - len(msg)
        msg += conn.recv(size_left)
    return msg


def recv(conn):
    data_size = struct.unpack("L", basic_recv(conn, LONG_SIZE))[0]
    data = basic_recv(conn, data_size)
    return pickle.loads(data)


LONG_SIZE = struct.calcsize("L")
LOCAL_HOST = "192.168.6.76"
PORT = 8083
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
while True:
    answer = input("S for Server, C for Client: ")
    if answer.capitalize() == "S":
        sock.bind((LOCAL_HOST, PORT))
        print("Waiting for a client...")
        sock.listen(1)
        conn, address = sock.accept()
        print("Successfully created the server!")
        while True:
            stop, frame = recv(conn)
            if frame is not None:
                cv2.imshow("Server Frame", frame)
            if stop:
                break
            cv2.waitKey(1)
        conn.close()
        break
    elif answer.capitalize() == "C":
        sock.connect((LOCAL_HOST, PORT))
        print("Successfully connected to the server!")
        capture = cv2.VideoCapture(0)
        while True:
            ret, frame = capture.read()
            if ret:
                send(sock, (False, frame))
                cv2.imshow("Client Frame", frame)
            else:
                send(sock, (False, None))
            if ord("q") == cv2.waitKey(1) & 0xFF:
                send(sock, (True, None))
                break
        capture.release()
        break
cv2.destroyAllWindows()
sock.close()
