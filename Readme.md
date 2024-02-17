# Distributed Messaging System with ZeroMQ

## Overview

This project implements a simple, distributed messaging system using ZeroMQ. The system comprises three main components: a central server, group servers, and user clients. The central server manages group registrations and listings, group servers handle specific group communications, and user clients interface with the system for interacting with groups and exchanging messages.

## Features

- Central server for group management
- Group servers for handling group-specific actions
- User clients for interacting with groups
- Join, leave, send, and fetch messages within groups

## Requirements

- Python 3
- ZeroMQ library

## Installation

Ensure Python 3 is installed on your system. Install the ZeroMQ library using pip:

```bash
pip install pika
```

## Usage
### Starting the Central Server
Run the central server script to manage group registrations and listings:
```bash
python3 server.py
```

### Starting a Group Server
Start a group server by specifying a group name:
```bash
python3 group.py <group_name>
```

### Using the User Client
Run the user client script with a user name:
```bash
python3 user_client.py <user_name>
```

## Components

### Central Server (`server.py`)
The central server manages groups. It supports registering new groups, listing all groups, and removing groups from the system.

### Group Server (`group_server.py`)
Each group server manages a specific group's communications, including adding users to the group, removing users, storing messages, and retrieving messages.

### User Client (`user_client.py`)
The user client allows users to interact with the system. Users can join groups, leave groups, send messages to a group, and fetch messages from a group.
