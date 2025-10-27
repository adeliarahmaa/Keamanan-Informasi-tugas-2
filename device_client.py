# device_client.py
# Jalankan di Terminal B (bertindak sebagai client)
import socket
import threading
import struct
from crypto_utils import encrypt_message, decrypt_message

# ----- Ganti KEY & SERVER_IP jika perlu (KEY harus sama dengan server) -----
KEY = bytes.fromhex("00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9000
# --------------------------------------------------------------------------

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

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to {SERVER_IP}:{SERVER_PORT}")
        def reader():
            try:
                while True:
                    pt = recv_encrypted(s, KEY)
                    print(f"[Remote] {pt.decode(errors='ignore')}")
            except Exception as e:
                print("[Reader] ended:", e)
        t = threading.Thread(target=reader, daemon=True)
        t.start()

        try:
            while True:
                line = input()
                if line.strip().lower() in ("exit", "quit"):
                    print("Closing...")
                    s.close()
                    break
                send_encrypted(s, KEY, line.encode())
        except Exception as e:
            print("[Sender] ended:", e)
            try:
                s.close()
            except:
                pass

if __name__ == "__main__":
    main()
