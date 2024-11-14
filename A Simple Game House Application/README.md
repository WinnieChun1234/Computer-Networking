# A Simple Game house application

This project consists of a server and a client application for a networked game. This is individual implementation.

## System Requirements

- Python 3.9.6
- macOS (tested on M2 Mac)

## Installation

1. Download the folder containing GameServer.py and GameClient.py

2. Navigate to the project directory

## Usage

### Server

To run the server, execute the following command:

```Usage: python3 GameServer.py <Server_port> <Path_to_UserInfo.txt> ```

example:

```python3 GameServer.py 12345 ~/Desktop/UserInfo.txt```

### Client

To run the client, execute the following command:

```Usage: python3 FTClient.py localhost <Server_port>```

example:

```python3 GameServer.py localhost 12345```
