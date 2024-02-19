import zmq


def server():
    print("Starting Server.")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    groups = {}

    while True:
        message = socket.recv_json()
        action = message['action']

        if action == "register":
            group_name = message['group_name']
            group_addr = message['address']
            groups[group_name] = group_addr
            print(f"JOIN REQUEST FROM {group_addr}")
            socket.send_json({"status": "SUCCESS"})
        elif action == "list_groups":
            print(f"GROUP LIST REQUEST FROM {message['ip_addr']}")
            socket.send_json(groups)
     

if __name__ == "__main__":
    server()