import json
import socket
import sys
from datetime import datetime
import zmq

#group.py - json
ALL_USERS = {}
group_memberships = {}

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
    

def get_free_port():
    # Create a socket to find a free port
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temp_socket.bind(('localhost', 0))  # Bind to an available port on localhost
    _, port = temp_socket.getsockname()  # Get the assigned port
    temp_socket.close()  # Close the temporary socket
    return port

def store_message(group_name,user_name, message_text):
        message = {
            "user_name": user_name,
            "message_text": message_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
        # Try to read the existing messages from msg.json
            with open(f'messages_{group_name}.json', 'r') as file:
                messages = json.load(file)
        except FileNotFoundError:
        # If msg.json doesn't exist, start with an empty list
            messages = []
    
    # Append the new message to the list of messages
        messages.append(message)
    
    # Write the updated list back to msg.json
        with open(f'messages_{group_name}.json', 'w') as file:

            json.dump(messages, file, indent=4)

def fetch_messages(group_name, after_timestamp=None):
        try:
            with open(f'messages_{group_name}.json', 'r') as file:
                messages = json.load(file)

            # Filter messages if after_timestamp is specified
            if after_timestamp:
                filtered_messages = []
                after_time = datetime.strptime(after_timestamp, "%Y-%m-%d %H:%M:%S")
                for msg in messages:
                    msg_time = datetime.strptime(msg["timestamp"], "%Y-%m-%d %H:%M:%S")
                    if msg_time > after_time:
                        filtered_messages.append(msg)
                return filtered_messages
            else:
                return messages  # Return all messages if no timestamp is specified
        except FileNotFoundError:
            print(f"No messages file found for group: {group_name}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding messages file for group: {group_name}: {e}")
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
            # Optionally remove the group if it becomes empty
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
            #print(group_memberships)
            rep_socket.send_json({"response": "SUCCESS"})
            #print(group_memberships)

        elif message['action'] == 'leave':
            user_uuid = message['uuid']
            #add_user_to_group(group_name, user_uuid)
            remove_user_from_group(group_name, user_uuid)
            #print(group_memberships)
            print(f"LEAVE REQUEST FROM {user_uuid}")
            rep_socket.send_json({"response": "SUCCESS"})
            #print(group_memberships)

        elif message['action'] == 'send':
            user_uuid = message['uuid']
            user_name = message['user_names']
            msg = message['messages']
            store_message(group_name, user_name,msg)
            # print(msg)
            print(f"MESSAGE SEND FROM {user_uuid}")
            rep_socket.send_json({"response": "SUCCESS"})

        elif message['action'] == 'get':
            timestamp = message['timestamp']
            UUID = message['user_uuid']
            print(f"MESSAGE REQUEST FROM {UUID}")
            mes=fetch_messages(group_name,timestamp)
            print(mes)
            rep_socket.send_json({"response": "SUCCESS","mes":mes})

             


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <group_name> <port_no>")
        sys.exit(1)
    group_name = sys.argv[1]  # Group name from command line

    group_server(group_name)
