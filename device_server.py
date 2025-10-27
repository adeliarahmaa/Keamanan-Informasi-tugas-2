# device_server.py
# Jalankan di Terminal A (bertindak sebagai server/listener)
import socket
import threading
import struct
from crypto_utils import encrypt_message, decrypt_message
import sys

# ----- Ganti KEY ini jika mau (harus sama di client) -----
KEY = bytes.fromhex("00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
# ----------------------------------------------------------

HOST = "127.0.0.1"   # gunakan localhost untuk 1 laptop (2 terminal)
PORT = 9000

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket tertutup")
        data += chunk
    return data

def recv_encrypted(sock, key):
    raw_len = recv_exact(sock, 4)
    (length,) = struct.unpack(">I", raw_len)
    blob = recv_exact(sock, length)
    return decrypt_message(key, blob)

def send_encrypted(sock, key, plaintext):
    blob = encrypt_message(key, plaintext)
    sock.sendall(blob)

def handle_conn(conn, addr):
    print(f"[+] Connected: {addr}")
    def reader():
        try:
            while True:
                pt = recv_encrypted(conn, KEY)
                print(f"[Remote] {pt.decode(errors='ignore')}")
        except Exception as e:
            print("[Reader] ended:", e)
    t = threading.Thread(target=reader, daemon=True)
    t.start()

    try:
        while True:
            line = input()
            if line.strip().lower() in ("exit", "quit"):
                print("Closing connection...")
                conn.close()
                break
            send_encrypted(conn, KEY, line.encode())
    except Exception as e:
        print("[Sender] ended:", e)
        try:
            conn.close()
        except:
            pass

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Listening on {HOST}:{PORT} ...")
        conn, addr = s.accept()
        with conn:
            handle_conn(conn, addr)

if __name__ == "__main__":
    main()
