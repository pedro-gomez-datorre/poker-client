import socket
import pickle
import struct
import threading

SERVER_IP = input("Enter server IP (default 127.0.0.1): ").strip() or "127.0.0.1"
PORT = 5555

def send_full(sock, obj):
    data = pickle.dumps(obj)
    sock.sendall(struct.pack(">I", len(data)) + data)

def recvall(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_full(sock):
    raw_len = recvall(sock, 4)
    if not raw_len:
        return None
    msg_len = struct.unpack(">I", raw_len)[0]
    return pickle.loads(recvall(sock, msg_len))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

my_name = input("Enter your name: ").strip() or "Player"
send_full(client, my_name)

def listener():
    while True:
        data = recv_full(client)
        if not data:
            print("Disconnected from server.")
            break
        print("\n--- GAME STATE ---")
        print(f"Message: {data['message']}")
        print(f"Round: {data['round']}")
        print(f"Table: {data['table']}")
        print("Players:")
        for p in data["players"]:
            hand = p["hand"] if p["name"] == my_name else ["?", "?"]
            print(f"  {p['name']}: Chips={p['chips']} Hand={hand}")
        print("------------------")

threading.Thread(target=listener, daemon=True).start()

while True:
    cmd = input("(press Enter to refresh / type quit): ").strip().lower()
    if cmd == "quit":
        break
