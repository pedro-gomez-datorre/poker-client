import socket
import pickle
import threading
import time
import os

# CONFIG
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

# RECEIVE UPDATES
def receive_updates():
    global game_state, my_index
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            game_state = pickle.loads(data)
            if my_index is None and "players" in game_state:
                for i, p in enumerate(game_state["players"]):
                    if p["name"] == my_name:
                        my_index = i
                        break
            display_state()
        except:
            print("Disconnected from server.")
            client.close()
            break

# DISPLAY STATE
def display_state():
    os.system('cls' if os.name == 'nt' else 'clear')
    global game_state, my_index
    if not game_state.get("game_started", False):
        print("\nWaiting for players...")
        return

    print("\n=== Game ===")
    print(f"Pot: {game_state['pot']}")
    print(f"Table: {game_state['table']} [{game_state['round_stage']}]")
    print("Players:")
    for i, p in enumerate(game_state["players"]):
        status = "Active" if p["active"] else "Folded"
        turn_marker = "-->" if i == game_state["turn_index"] else "  "
        me_marker = "(You)" if i == my_index else ""
        print(f"{turn_marker} {p['name']} {me_marker}: Chips: {p['chips']}, Status: {status}, Bet: {p['current_bet']}")

    if my_index is not None:
        hand = game_state["players"][my_index].get("hand", [])
        if hand:
            print(f"Your hand: {' '.join(hand)}")

    if game_state["turn_index"] == my_index:
        print("\nIt's YOUR turn!")
        take_action()
    else:
        current = game_state["players"][game_state["turn_index"]]["name"] if 0 <= game_state["turn_index"] < len(game_state["players"]) else "None"
        print(f"\nWaiting for {current} to act...")

# PLAYER ACTION
def take_action():
    actions = ["fold", "call", "raise", "allin"]
    while True:
        action = input("Your turn (fold/call/raise/allin): ").lower()
        if action not in actions:
            print("Invalid action. Try again.")
            continue
        amount = 0
        if action == "raise":
            while True:
                try:
                    amount = int(input("Enter raise amount: "))
                    break
                except:
                    print("Enter a valid number")
        client.sendall(pickle.dumps({"player": my_name, "action": action, "amount": amount}))
        break

# MAIN LOOP
threading.Thread(target=receive_updates, daemon=True).start()
while True:
    time.sleep(1)
