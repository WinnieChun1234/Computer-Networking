#!/usr/bin/python3

import socket
import sys

def main(argv):
    # get port number from argv
    try:
        serverPort = sys.argv[1]
    except os.error as emsg:
        print("Input error: ", emsg)
        sys.exit(1)
        
    # create socket and bind
    try:
        sockfd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sockfd.bind(("", int(serverPort)))
    except socket.error as emsg:
        print("Socket error: ", emsg)
        sys.exit(1)
    
    sockfd.listen(5)
    
    print("The server is ready to receive")
    
    while True:
        
        # accept new connection
        try:
            conn, addr = sockfd.accept()
        except socket.error as emsg:
            print("Socket error: ", emsg)
            sys.exit(1)
        
        # receive file name/size message from client 
        msg = conn.recv(1024)
        file = msg.decode('ascii')

        
        #use Python string split function to retrieve file name and file size from the received message
        fname, filesize = file.split(':')
        
        print("Open a file with name \'%s\' with size %s bytes" % (fname, filesize))
        
        #create a new file with fname
        fd = open(fname, 'wb')
       
       
       
       
        
        remaining = int(filesize)

        conn.send(b"OK")

        print("Start receiving . . .")
        while remaining > 0:
        # receive the file content into rmsg and write into the file
            try:
                rmsg = conn.recv(1024)
                fd.write(rmsg)
            except socket.error as emsg:
                print("Socket sendall error: ", emsg)
                sys.exit(1)
                
            remaining -= len(rmsg)

        print("[Completed]")
        fd.close()
        conn.close()
        
    sockfd.close()
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 FTServer.py <Server_port>")
        sys.exit(1)
    main(sys.argv)
