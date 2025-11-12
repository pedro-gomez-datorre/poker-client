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
        print("\nWaiting for players to join...")
        return

    print("\n=== Texas Hold'em ===")
    print(f"Pot: {game_state['pot']}")
    print(f"Table ({game_state['round_stage']}): {' '.join(game_state['table']) if game_state['table'] else 'Empty'}\n")

    print("Players:")
    for i, p in enumerate(game_state["players"]):
        status = "Active" if p["active"] else "Folded"
        turn_marker = "-->" if i == game_state["turn_index"] else "  "
        me_marker = "(You)" if i == my_index else ""
        print(f"{turn_marker} {p['name']} {me_marker}: Chips: {p['chips']}, Status: {status}, Bet: {p['current_bet']}")

    # Show your hand
    if my_index is not None:
        hand = game_state["players"][my_index].get("hand", [])
        if hand:
            print(f"\nYour hand: {' '.join(hand)}")

    # Show winner if round ended
    if game_state.get("round_stage") == "showdown":
        winner = game_state.get("winner")
        if winner:
            print(f"\n*** {winner} wins the pot of {game_state['pot']} chips! ***")
        print("\nPlayers' hands:")
        for p in game_state["players"]:
            hand_display = ' '.join(p['hand']) if p['hand'] else 'N/A'
            print(f"{p['name']}: {hand_display}")

    # Prompt for action if it's your turn
    if my_index is not None and game_state.get("turn_index") == my_index and game_state.get("round_stage") != "showdown":
        print("\nIt's YOUR turn!")
        take_action()
    else:
        current_index = game_state.get("turn_index")
        if current_index is not None and 0 <= current_index < len(game_state.get("players", [])):
            current_name = game_state["players"][current_index]["name"]
            print(f"\nWaiting for {current_name} to act...")

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
