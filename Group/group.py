import json
import socket
import sys
import zmq
import requests
from datetime import datetime


class GroupServer:
    def __init__(self, group_name):
        self.group_name = group_name
        self.group_memberships = {}
        self.context = zmq.Context()
        self.server_address = "10.160.0.2"
        self.address = self.get_ip_address()
        self.port = self.get_free_port()
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_socket.bind(f"tcp://0.0.0.0:{self.port}")
        print(f"Group '{self.group_name}' is broadcasting on port {self.port}")

    @staticmethod
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


    @staticmethod
    def get_free_port():
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.bind(('localhost', 0))
        _, port = temp_socket.getsockname()
        temp_socket.close()
        return port

    def add_user_to_group(self, user_uuid):
        if self.group_name not in self.group_memberships:
            self.group_memberships[self.group_name] = set()
        self.group_memberships[self.group_name].add(user_uuid)

    def remove_user_from_group(self, user_uuid):
        if self.group_name in self.group_memberships and user_uuid in self.group_memberships[self.group_name]:
            self.group_memberships[self.group_name].remove(user_uuid)
            if len(self.group_memberships[self.group_name]) == 0:
                del self.group_memberships[self.group_name]

    @staticmethod
    def store_message(group_name, user_name, message_text):
        message = {
            "user_name": user_name,
            "message_text": message_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Similar to the original function, handling file operations

    @staticmethod
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
    

    def send_server_group_remove(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.server_address}:5200")
        socket.send_json({"action": "remove", "group_name": self.group_name})
        response = socket.recv_json()
        print(response['status'])

    def send_server_group_live(self):
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5200")
        socket.send_json({"action": "register", "group_name": self.group_name, "address": f"{self.get_ip_address()}:{self.port}"})
        response = socket.recv_json()
        print(response['status'])

    def run(self):
        print("Starting Server.")
        self.send_server_group_live()
        try:
            while True:
                message = self.rep_socket.recv_json()
                # Similar handling for 'join', 'leave', 'send', and 'get' actions
                if message['action'] == 'join':
                    user_uuid = message['uuid']
                    self.add_user_to_group(group_name, user_uuid)
                    print(f"JOIN REQUEST FROM {user_uuid}")
                    #print(group_memberships)
                    self.rep_socket.send_json({"response": "SUCCESS"})
                    #print(group_memberships)

                elif message['action'] == 'leave':
                    user_uuid = message['uuid']
                    #add_user_to_group(group_name, user_uuid)
                    self.remove_user_from_group(group_name, user_uuid)
                    #print(group_memberships)
                    print(f"LEAVE REQUEST FROM {user_uuid}")
                    self.rep_socket.send_json({"response": "SUCCESS"})
                    #print(group_memberships)

                elif message['action'] == 'send':
                    user_uuid = message['uuid']
                    user_name = message['user_names']
                    msg = message['messages']
                    self.store_message(group_name, user_name,msg)
                    # print(msg)
                    print(f"MESSAGE SEND FROM {user_uuid}")
                    self.rep_socket.send_json({"response": "SUCCESS"})

                elif message['action'] == 'get':
                    timestamp = message['timestamp']
                    UUID = message['user_uuid']
                    print(f"MESSAGE REQUEST FROM {UUID}")
                    mes=self.fetch_messages(group_name, timestamp)
                    
                    self.rep_socket.send_json({"response": "SUCCESS","mes":mes})



        except KeyboardInterrupt:
            print("Shutting down group server...")
            self.send_server_group_remove()
            self.rep_socket.close()
            self.context.term()
            sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <group_name>")
        sys.exit(1)
    group_name = sys.argv[1]
    server = GroupServer(group_name)
    server.run()
