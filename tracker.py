#!/usr/bin/env python3
# Save as server.py 
# Message Receiver
import os
import sys
from socket import *
for root, subdirs, files in os.walk(os.getcwd()):
    print ( root , subdirs , files )


def CreateRepository ( Folder ) :
    os . mkdir ( Folder )

def HostRepositories ( ) :
    host = ""
    port = 13000
    buf = 1024
    addr = (host, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind(addr)
    print("Waiting to receive messages...")
    while True:
        (data, client_address) = UDPSock.recvfrom(buf)
        print("Received message: " + data)
        DataArray = data . split()
        print(DataArray)
        if data == "exit":
            break
        if DataArray [ 0 ] == 'Copy':
            print('FOUND Copy')
        if DataArray [ 0 ] == 'Retrieve':
            SendRepository ( DataArray [ 1 ] , client_address )
    UDPSock.close()
    os._exit(0)

def SendRepository ( RootFolder , client_address ) :
    Buffer = ''
    for root, subdirs, files in os.walk(os.getcwd() + '/' + RootFolder):
        Buffer = Buffer + '[' + root + '] folder\n'
        for SubFile in files :
            FilePath = root + '/' + SubFile
            Size = os.path.getsize(FilePath)
            with open(SubFile, 'r') as content_file:
                content = content_file.read()
            Buffer = Buffer + '[' + root + '] file ' + Size + ' ' + Contents + '\n'
    print ( Buffer )
    

def RetrieveRemoteRepository ( Folder , RemoteAddress ) :
    host = RemoteAddress
    port = 13000
    addr = (host, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    data = 'Retrieve ' + Folder
    print ( data )
    UDPSock.sendto(data.encode(), addr)
    UDPSock.close()
    os._exit(0)

def MainSwitch ( ) :
    if len ( sys.argv ) > 1 :
        if sys.argv [ 1 ] == 'CreateRepo' :
            CreateRepository ( sys.argv [ 2 ] )
        if sys.argv [ 1 ] == 'Host' :
            HostRepositories ( )
        if sys.argv [ 1 ] == 'Retrieve' :
            RetrieveRemoteRepository ( sys.argv [ 2 ] , sys.argv [ 3 ] )

MainSwitch ( )
