#!/usr/bin/python3

import select
import signal
import socket
import os.path
import sys

# create a socket with socket family IPV4 and socket_type TCP
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
def connectToServer(argv):
    try:
        PORT = sys.argv[2]
        PORT = int(PORT)
        # print("PORT: ", PORT)
    except os.error as errMsg:
        print("Input error: ", errMsg)
        sys.exit(1)

    # get the IP address of the local machine
    try:
        if argv[1] == "localhost":
            IP_ADDR = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET, socket.SOCK_DGRAM)[0][4][0]
        else:
            IP_ADDR = argv[1]
        # debug
        # print("IP address:", IP_ADDR)
    except socket.gaierror as errMsg:
        print("Error occurred in getting: ", errMsg)
    # tuple input for connection
    ADDR = (IP_ADDR, PORT)

    # connet to the server
    try:
        clientSocket.connect(ADDR)
        print("Sucessfully connected to server")
    except socket.error as errMsg:
        print("Failed to connect to the server: ", errMsg)
        sys.exit(1)
        
# send user information to server for authentication
def userAuthentication():
    while True: 
        username = input("Pleaae input your name:\n")
        password = input("Pleaae input your password:\n")
        authenticateUserInfo = f'/login {username} {password}'
        # debug
        # print("authenticateUserInfo from client: ", authenticateUserInfo)
        try:
            clientSocket.send(authenticateUserInfo.encode('utf-8'))
        except socket.error as errmsg:
            print("Failed to send ", authenticateUserInfo, errmsg)
            return
        try:    
            authMsgFromServer = clientSocket.recv(1024).decode()
        except socket.error as errmsg:
            print("Failed to receive: ", authMsgFromServer, errmsg)
            return
        if not authMsgFromServer:
            print("Server disconnected.")
            return
        print(authMsgFromServer)    
        if authMsgFromServer == "1001 Authentication successful":
            break
    return True

def receiveMessage():
    while True:
        readyReady, _, _ = select.select([clientSocket], [], [])
        if readyReady:
            return clientSocket.recv(1024).decode()
def clientLoop():
    while True:
        userInput = input()

        try:
            clientSocket.send(userInput.encode('utf-8'))
        except socket.error as errmsg:
            print("Failed to send: ", userInput, errmsg)
            return

        try:    
            message = receiveMessage()
            print(message)
        except socket.error as errmsg:
            print("Failed to receive: ", errmsg)
            return
        except KeyboardInterrupt:
            return
        
        if not message:
            print("Server disconnected.")
            break

        if message.startswith("4001"):
            print("Client ends")
            break
        if message.startswith("3011"):
            try:    
                message = receiveMessage()
                if not message:
                    print("Server disconnected.")
                    break
                print(message)
            except socket.error as errmsg:
                print("Failed to receive: ", errmsg)
                return

if __name__ == '__main__':
    # print("pid", os.getpid())
    if len(sys.argv) != 3:
        print("Usage: python3 FTClient.py <Server_addr> <Server_port>")
        sys.exit(1)
    try:
        connectToServer(sys.argv)
        if userAuthentication() is True:
            clientLoop()
    except KeyboardInterrupt:
        print("Client ends")
    finally:
        clientSocket.close()
