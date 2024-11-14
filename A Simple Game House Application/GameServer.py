import socket 
import socketserver
import sys
import os.path
from enum import Enum
import random

class GameState(Enum):
    INIT = 0
    GAMEHALL = 1
    WAITING = 2
    PLAY = 3
    GUESSED = 4


# create a socket with socket family IPV4 and socket_type TCP   
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# create a list to represent a list of 10 game room 
roomList = [[] for _ in range(10)]
roomPlayGuess = [[] for _ in range(10)]
threadStates = {}
threadRooms = {}

            
# authenticate users
def authenticateUser(msg):
    # Extract the username and name from the string
    try:
        cmd, username, password = msg.split(None, 2)
    except ValueError:
        return "1002 Authentication failed"
    if cmd != "/login":
        return "4002 Unrecognized message"

    # Format the string as "user:name"
    msgFormatted = f"{username}:{password}"

    filename = sys.argv[2]
    authMsg = "1002 Authentication failed"

    with open(filename, 'r') as file:
        for line in file:
            if line.find(msgFormatted) != -1:
                authMsg = "1001 Authentication successful"
    return authMsg
    
# gamehall
def gameHall(msg):
    if msg == "/list":
        print(roomList)
        list = f"3001 {len(roomList)} {' '.join(str(len(r)) for r in roomList)}"
        return list
    elif msg.startswith("/enter"):
        words = msg.split()
        if len(words) == 2 and words[1].isdigit() and int(words[1]) < 11 and int(words[1]) > 0:
            words = msg.split()
            gameroom = int(words[1]) - 1
            return gameroom
        else:
            return False
    elif msg == "/exit":
        byebye = f"4001 Bye Bye"
        return byebye
    return False

def playGame(msg, rm, conn):
    if msg.startswith("/guess"):
        words = msg.split()
        if len(words) == 2 and (words[1] == "true" or words[1] == "false"):
            value = words[1] == "true"
            state = [value, conn]
        else:
            return False
    else:
        return False

    roomPlayGuess[rm].append(state)
    return True

def resetRoom(rm):
    for p in roomList[rm]:
        threadStates[p.client_address] = GameState.GAMEHALL
        threadRooms[p.client_address] = -1

    roomList[rm] = []
    roomPlayGuess[rm] = []

def checkGameResult(rm):
    r = bool(random.randint(0, 1))
    win = f"3021 You are the winner"
    loss = f"3022 You lost this game"
    guess: list[tuple[bool, GameHandler]] = roomPlayGuess[rm]
    players: list[GameHandler] = roomList[rm]
    if len(guess) < len(players):
        return

    if len(players) < 2:
        for p in players:
            if p.getState() == GameState.GUESSED:
                p.send(win)
        resetRoom(rm)
        return 
    
    p1, p2 = guess
    print("Random value:", r)
    if p1[0] == p2[0]:
        result = f"3023 The result is a tie"
        p1[1].send(result.encode('utf-8'))
        p2[1].send(result.encode('utf-8'))
    elif p1[0] == r:
        p1[1].send(win.encode('utf-8'))
        p2[1].send(loss.encode('utf-8'))
    elif p2[0] == r:
        p2[1].send(win.encode('utf-8'))
        p1[1].send(loss.encode('utf-8'))
    resetRoom(rm)


class GameServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

class GameHandler(socketserver.StreamRequestHandler):
    def recv(self):
        try:
            msg = self.connection.recv(1024).decode('utf-8')
        except socket.error as errmsg:
            print("Failed to receive: ", errmsg)
            return None
        return msg
    
    def send(self, message):
        self.wfile.write(message.encode('utf-8'))
        print(message, self.client_address)

    def setState(self, state):
            threadStates[self.client_address] = state
            return state
            
    def getState(self):
        return threadStates[self.client_address]
    
    def setRoom(self, room):
        threadRooms[self.client_address] = room
        return room
        
    def getRoom(self):
        return threadRooms[self.client_address]
    
    def checkInactivePlayerInRoom(self, rooms):
        print([x.connection for r in rooms for x in r])
        for i in range(10):
            for player in rooms[i].copy():
                if player.connection.fileno() == -1:
                    rooms[i].remove(player)
        return
        
    def handle(self):
        conn = self.connection
        addr = self.client_address
        
        self.setState(GameState.INIT)
        print(addr, " is nowconnected to the server")
        rm = self.setRoom(-1)
        while True:
            # Start communication
            print("Wait for client message", self.client_address)
            msg = self.recv()
            if msg is None:
                return
            current_state = self.getState()
            rm = self.getRoom()
            print(f"{self.client_address} <{msg}> {current_state}")
            if not msg:
                print("Client disconnected")
                return

            if current_state == GameState.INIT:
                authMsg = authenticateUser(msg)
                self.send(authMsg)
                if authMsg == "1001 Authentication successful":
                    self.setState(GameState.GAMEHALL)
            elif current_state == GameState.GAMEHALL:
                rmsg = gameHall(msg)
                if type(rmsg) == int:
                    self.checkInactivePlayerInRoom(roomList)
                    rm = self.setRoom(rmsg)
                    if len(roomList[rm]) == 0:
                        state =  f"3011 Wait"
                        self.send(state)
                        roomList[rm].append(self)
                    elif len(roomList[rm]) == 1:
                        roomList[rm].append(self)
                        for p in roomList[rm]:
                            state = f"3012 Game started. Please guess true or false"
                            p.send(state)
                            p.setState(GameState.PLAY)
                    else:
                        state = f"The room is full"
                        self.send(state)
                elif rmsg is False:
                    error = f"4002 Unrecognized message"
                    self.send(error)
                elif rmsg.startswith("4001 "):
                    self.send(rmsg)
                    break
                else:
                    self.send(rmsg)
            elif current_state == GameState.PLAY:
                isValidInput = playGame(msg, rm, conn)
                if not isValidInput:
                    error = f"4002 Unrecognized message"
                    self.send(error)
                    continue
                self.setState(GameState.GUESSED)
                checkGameResult(rm)
            else:
                error = f"4002 Unrecognized message"
                self.send(error)

    def finish(self):
        rm = self.getRoom()
        if rm != -1:
            roomList[rm] = [x for x in roomList[rm] if x != self]
            roomPlayGuess[rm] = [x for x in roomPlayGuess[rm] if x[1] != self]
            if any(x.getState() == GameState.GUESSED for x in roomList[rm]):
                checkGameResult(rm)

        print("Client disconnected")
        return super().finish()

if __name__ == "__main__":
    print("pid", os.getpid())
    if len(sys.argv) != 3:
        print("Usage: python3 GameServer.py <Server_port> <Path_to_UserInfo.txt>")
        sys.exit(1)
        
    HOST, PORT = "", int(sys.argv[1])

    try:
        with GameServer((HOST, PORT), GameHandler) as server:
            print("Accepting connections")
            server.serve_forever()
    except KeyboardInterrupt:
        print("Server disconnected")

