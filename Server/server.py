import json
import sqlite3
import socket
import zmq


def get_ip_address():
    """Get the local IP address used to connect to the outside world."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Using Google's DNS server to find the connection interface
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return "127.0.0.1"  # Fallback to localhost in case of any issue
    
groups_all = {}#STORE THE GROUP WITH UNIQUE IP

def server():
    context = zmq.Context()
    print(get_ip_address())
    print("Starting Server.")
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
            print(group_addr)
            print(groups)
            #print("SUCCESS")
            socket.send_json({"status": "SUCCESS"})\
            #print(groups)
            
        

        elif action == "list_groups":
            print(f"GROUP LIST REQUEST FROM {message['ip_addr']}")
            socket.send_json(groups)

        


if __name__ == "__main__":
    server()
