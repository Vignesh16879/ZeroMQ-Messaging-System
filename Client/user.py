import socket
import sys
import uuid
import zmq
from datetime import datetime


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
  
    
def send_join_request(ip, user_uuid):
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)  
    req_socket.connect(f"tcp://{ip}")  
    req_socket.send_json({"action": "join", "uuid": str(user_uuid),"group_port":ip})
    response = req_socket.recv_json()
    print(response['response'])


def send_leave_request(ip, user_uuid):
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)  
    req_socket.connect(f"tcp://{ip}")  
    req_socket.send_json({"action": "leave", "uuid": str(user_uuid),"group_port":ip})
    response = req_socket.recv_json()
    print(response['response'])


def send_msg_request(ip, user_uuid, msg,user_name):
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)
    req_socket.connect(f"tcp://{ip}")
    req_socket.send_json({"action": "send","uuid": str(user_uuid),"group_port": ip,"messages":msg,"user_names":user_name})
    response = req_socket.recv_json()
    print(response.get("response"))
    
        
def get_msgs(ip, group_name, timestamp,UUID):
    context = zmq.Context()
    req_socket = context.socket(zmq.REQ)
    req_socket.connect(f"tcp://{ip}")
    
    if(timestamp):
        req_socket.send_json({"action": "get","group_name": group_name,"timestamp": str(timestamp),"user_uuid":str(UUID)})
    else:
         req_socket.send_json({"action": "get","group_name": group_name,"timestamp": timestamp,"user_uuid":str(UUID)})
    
    response = req_socket.recv_json()
    
    if response.get("response") == "SUCCESS":
        for x in response["mes"]:
            print(x[2], "-", x[0], x[1])
    else:
        print("FAILED")


def fetch_groups(context):
    req_socket = context.socket(zmq.REQ)
    req_socket.connect("tcp://localhost:5555")  
    req_socket.send_json({"action": "list_groups","ip_addr":get_ip_address()})
    groups = req_socket.recv_json()
    req_socket.close()
    
    return groups


users = {}
def user(user_name,UUID):
    context = zmq.Context()
    groups = fetch_groups(context)
    
    if not groups:
        print("No groups available.")
        sys.exit(1)
    
    for group_name, group_port in groups.items():
        print(f"{group_name} -- {group_port}")

    while True:        
        print("\nMENU")
        print("1 FOR JOIN GROUP")
        print("2 FOR LEAVE GROUP")
        print("3 FOR SEND MSG")
        print("4 FOR GET MSG")
        option = input("What would you like to do? (eg 1,2,3,4): ")

        if option == "1":
            group_name = input("Enter group name to join: ")
            group_port = groups.get(group_name)  
            
            if group_port:
                send_join_request(group_port, UUID)    
            else:
                print("Group not found.")

        elif option == "2":
            group_name = input("Enter group name you want to leave: ")
            group_port = groups.get(group_name)  
            
            if group_port:
                send_leave_request(group_port, UUID)
            else:
                print("Group not found.")
        elif option == "3":
            group_name = input("Enter group name to send a message: ")
            group_port = groups.get(group_name)  
            
            if group_port:
                messages = []
                msg = input(f"{user_name}:")
                send_msg_request(group_port, UUID,msg,user_name)
            else:
                print("Group not found.")
        elif option == "4":
            group_port = groups.get(group_name)  
            group_name = input("Enter group name to fetch messages: ")
            user_input = input("Enter the timestamp (YYYY-MM-DD HH:MM:SS): ")
            
            try:
                timestamp = datetime.strptime(user_input, '%m/%d/%y %H:%M:%S')    
            except :
                timestamp=None

            if group_port:
                get_msgs(group_port, group_name, timestamp,UUID)
            else:
                print("Group not found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <user_name>")
        sys.exit(1)
        
    user_name = sys.argv[1]
    UUID = uuid.uuid()
    user(user_name,UUID)