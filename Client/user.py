import datetime
import json
import socket
import sys
import threading
import uuid
import zmq

class UserClient:
    def __init__(self, user_name):
        self.user_name = user_name
        self.UUID = uuid.uuid4()  # Changed to uuid4 for uniqueness per instance
        self.context = zmq.Context()
        self.ip_address = self.get_ip_address()

    @staticmethod
    def get_ip_address():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception as e:
            return "127.0.0.1"

    def send_request(self, ip, data):
        req_socket = self.context.socket(zmq.REQ)
        req_socket.connect(f"tcp://{ip}")
        req_socket.send_json(data)
        response = req_socket.recv_json()
        req_socket.close()
        return response

    def fetch_groups(self):
        return self.send_request("localhost:5555", {"action": "list_groups", "ip_addr": self.ip_address})

    def join_group(self, group_name, group_port):
        response = self.send_request(group_port, {"action": "join", "uuid": str(self.UUID), "group_port": group_port})
        print(response['response'])

    def leave_group(self, group_name, group_port):
        response = self.send_request(group_port, {"action": "leave", "uuid": str(self.UUID), "group_port": group_port})
        print(response['response'])

    def send_msg(self, group_port, msg):
        response = self.send_request(group_port, {"action": "send", "uuid": str(self.UUID), "group_port": group_port, "messages": msg, "user_names": self.user_name})
        print(response.get("response", "FAILED"))

    def get_msgs(self, group_port, group_name, timestamp):
        data = {"action": "get", "group_name": group_name, "timestamp": str(timestamp) if timestamp else None, "user_uuid": str(self.UUID)}
        response = self.send_request(group_port, data)
        if response.get("response") == "SUCCESS":
            for x in response.get("mes", []):
                print(x[2], "-", x[0], x[1])
        else:
            print("FAILED")

    def run(self):
        print("\nWelcome", self.user_name)
        groups = self.fetch_groups()
        if not groups:
            print("No groups available.")
            return

        for group_name, group_port in groups.items():
            print(f"{group_name} -- {group_port}")
        print("\n")

        while True:
            print("\nMENU")
            print("1 FOR JOIN GROUP")
            print("2 FOR LEAVE GROUP")
            print("3 FOR SEND MSG")
            print("4 FOR GET MSG")
            option = input("What would you like to do? (eg 1,2,3,4 or exit): ")

            if option == "1":
                group_name = input("Enter group name to join: ")
                group_port = groups.get(group_name)
                if group_port:
                    self.join_group(group_name, group_port)
                else:
                    print("Group not found.")

            elif option == "2":
                group_name = input("Enter group name you want to leave: ")
                group_port = groups.get(group_name)
                if group_port:
                    self.leave_group(group_name, group_port)
                else:
                    print("Group not found.")

            elif option == "3":
                group_name = input("Enter group name to send a message: ")
                msg = input(f"{self.user_name}: ")
                group_port = groups.get(group_name)
                if group_port:
                    self.send_msg(group_port, msg)
                else:
                    print("Group not found.")

            elif option == "4":
                group_name = input("Enter group name to fetch messages: ")
                user_input = input("Enter the timestamp (YYYY-MM-DD HH:MM:SS) or press enter for all: ")
                timestamp = None
                if user_input:
                    try:
                        timestamp = datetime.datetime.strptime(user_input, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        print("Invalid timestamp format.")
                group_port = groups.get(group_name)
                if group_port:
                    self.get_msgs(group_port, group_name, timestamp)
                else:
                    print("Group not found.")

            elif option.lower() == "exit":
                break


if __name__ == "__main__":
    if len(sys.argv) != 2:
            print("Usage: python script.py <user_name>")
            sys.exit(1)
    user_name = sys.argv[1]
    client = UserClient(user_name)
    client.run()
