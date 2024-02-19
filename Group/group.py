import json
import socket
import sys
from datetime import datetime
import zmq


group_memberships = {}


def get_ip_address():
    """Get the local IP address used to connect to the outside world."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return "127.0.0.1"  
    

def get_free_port():    
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_socket.bind(('localhost', 0))  
    _, port = temp_socket.getsockname()  
    temp_socket.close()  
    
    return port


def store_message(group_name,user_name, message_text):
        message = {
            "user_name": user_name,
            "message_text": message_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open(f'messages_{group_name}.json', 'r') as file:
                messages = json.load(file)
        except FileNotFoundError:
            messages = []
    
        messages.append(message)
    
        with open(f'messages_{group_name}.json', 'w') as file:
            json.dump(messages, file, indent=4)


def fetch_messages(group_name, after_timestamp):
    try:
        with open(f'messages_{group_name}.json', 'r') as file:
            groups_messages = json.load(file)

        filtered_messages = []
        
        if after_timestamp:
            after_time = datetime.strptime(after_timestamp, "%Y-%m-%d %H:%M:%S")
            filtered_messages = [(msg["user_name"], msg["message_text"], msg["timestamp"]) for msg in groups_messages if datetime.strptime(msg["timestamp"], "%Y-%m-%d %H:%M:%S") >= after_time]
        else:
            filtered_messages = [(msg["user_name"], msg["message_text"], msg["timestamp"]) for msg in groups_messages]

        return filtered_messages     
    except FileNotFoundError:        
        return []
    except json.JSONDecodeError as e:        
        return []


def add_user_to_group(group_name, user_uuid):
    """Add a user to a group and update the JSON file."""
    if group_name not in group_memberships:
        group_memberships[group_name] = set()
    group_memberships[group_name].add(user_uuid)
 

def remove_user_from_group(group_name, user_uuid):
    """Remove a user from a group and update the JSON file."""
    if group_name in group_memberships and user_uuid in group_memberships[group_name]:
        group_memberships[group_name].remove(user_uuid)
        if len(group_memberships[group_name]) == 0:
            
            del group_memberships[group_name]
      

def send_server_group_live(name, port):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    socket.send_json({"action": "register", "group_name": group_name, "address": f"{get_ip_address()}:{port}"})
    response = socket.recv_json()
    print(response['status'])


def group_server(group_name):
    port = get_free_port()
    context = zmq.Context()
    print("Starting Server.")
    send_server_group_live(group_name, port)
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind(f"tcp://*:{port}")
    print(f"Group '{group_name}' is broadcasting on port {port}")
    
    while True:
        message = rep_socket.recv_json()

        if message['action'] == 'join':
            user_uuid = message['uuid']
            add_user_to_group(group_name, user_uuid)
            print(f"JOIN REQUEST FROM {user_uuid}")
            rep_socket.send_json({"response": "SUCCESS"})
        elif message['action'] == 'leave':
            user_uuid = message['uuid']
            remove_user_from_group(group_name, user_uuid)
            print(f"LEAVE REQUEST FROM {user_uuid}")
            rep_socket.send_json({"response": "SUCCESS"})
        elif message['action'] == 'send':
            user_uuid = message['uuid']
            user_name = message['user_names']
            msg = message['messages']
            store_message(group_name, user_name,msg)
            print(f"MESSAGE SEND FROM {user_uuid}")
            rep_socket.send_json({"response": "SUCCESS"})
        elif message['action'] == 'get':
            timestamp = message['timestamp']
            UUID = message['user_uuid']
            print(f"MESSAGE REQUEST FROM {UUID}")
            mess=fetch_messages(group_name,timestamp)
            rep_socket.send_json({"response": "SUCCESS","mes":mess})

             

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <group_name> <port_no>")
        sys.exit(1)
        
    group_name = sys.argv[1]
    group_server(group_name)