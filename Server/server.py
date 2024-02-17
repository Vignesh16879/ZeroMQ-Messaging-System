import json
import sqlite3
import socket
import zmq

class Server:
    def __init__(self, port=5200):
        self.port = port
        self.groups = {}
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")

    @staticmethod
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

    def register_group(self, group_name, group_addr):
        self.groups[group_name] = group_addr
        print(f"JOIN REQUEST FROM {group_addr}")
        print(group_addr)
        print(self.groups)
        self.socket.send_json({"status": "SUCCESS"})

    def list_groups(self, requestor_ip):
        print(f"GROUP LIST REQUEST FROM {requestor_ip}")
        self.socket.send_json(self.groups)

    def remove_group(self, group_name):
        if group_name in self.groups:
            del self.groups[group_name]
            print(f"GROUP REMOVED: {group_name}")
            self.socket.send_json({"status": "SUCCESS"})
        else:
            self.socket.send_json({"status": "GROUP_NOT_FOUND"})

    def run(self):
        print(self.get_ip_address())
        print("Starting Server.")
        while True:
            message = self.socket.recv_json()
            action = message['action']

            if action == "register":
                self.register_group(message['group_name'], message['address'])
                
            elif action == "list_groups":
                self.list_groups(message.get('ip_addr', 'Unknown'))
                
            elif action == "remove":
                self.remove_group(message['group_name'])

if __name__ == "__main__":
    server = Server()
    server.run()
