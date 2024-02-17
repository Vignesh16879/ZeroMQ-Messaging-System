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
- Starting the Central Server
- Run the central server script to manage group registrations and listings:
