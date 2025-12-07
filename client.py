import socket
import pickle
import threading
import time
import os

server_ip = input("Enter server IP: ")
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((server_ip, PORT))
except:
    print("Could not connect to server.")
    exit()

my_name = input("Enter your name: ")
client.sendall(pickle.dumps(my_name))

game_state = {}
my_index = None

def receive_updates():
    global game_state,my_index
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            game_state = pickle.loads(data)
            if my_index is None and "players" in game_state:
                for i,p in enumerate(game_state["players"]):
                    if p["name"] == my_name:
                        my_index = i
                        break
            display_state()
        except:
            client.close()
            break

def display_state():
    os.system('cls' if os.name == 'nt' else 'clear')
    global game_state,my_index

    if not game_state.get("game_started", False):
        print("\nWaiting for players to join...")
        return

    print("\n=== Texas Hold'em ===")
    print("Pot:", game_state["pot"])
    print("Table (", game_state["round_stage"], "):", " ".join(game_state["table"]) if game_state["table"] else "Empty", "\n")

    print("Players:")
    for i,p in enumerate(game_state["players"]):
        status="Active" if p["active"] else "Folded"
        turn="-->" if i==game_state["turn_index"] else "  "
        me="(You)" if i==my_index else ""
        print(f"{turn} {p['name']} {me}: Chips {p['chips']}, {status}, Bet {p['current_bet']}")

    if my_index is not None:
        hand = game_state["players"][my_index].get("hand", [])
        if hand:
            print("\nYour hand:", " ".join(hand))

    if game_state.get("round_stage")=="showdown":
        w=game_state.get("winner")
        if w:
            print(f"\n*** {w} wins the pot! ***")
        print("\nPlayers' hands:")
        for p in game_state["players"]:
            h=" ".join(p['hand']) if p['hand'] else "N/A"
            print(p["name"]+":",h)

    if my_index is not None and game_state.get("turn_index")==my_index and game_state.get("round_stage")!="showdown":
        print("\nIt's YOUR turn!")
        take_action()
    else:
        i=game_state.get("turn_index")
        if i is not None and 0<=i<len(game_state.get("players",[])):
            print(f"\nWaiting for {game_state['players'][i]['name']}...")

def take_action():
    actions=["fold","call","raise","allin"]
    while True:
        a=input("Your turn (fold/call/raise/allin): ").lower()
        if a not in actions:
            print("Invalid.")
            continue
        amount=0
        if a=="raise":
            while True:
                try:
                    amount=int(input("Enter raise amount: "))
                    break
                except:
                    print("Enter a valid number")
        client.sendall(pickle.dumps({"player":my_name,"action":a,"amount":amount}))
        break

threading.Thread(target=receive_updates,daemon=True).start()

while True:
    time.sleep(1)
