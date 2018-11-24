#!/usr/bin/env python3
# Save as server.py 
# Message Receiver
import os
import sys
import file_tree_loader
from diff import compute_dmp_patch_dict
import pickle
from socket import *


TRACKER_FOLDER_NAME = 'trackerfiles'
CURRENT_STATE_POINTER_NAME = 'currentState'
INITIAL_STATE_NAME = "INITIAL"
STATES_FOLDER_NAME = 'states'

def write_patch_data_to_file(state_name, patch_dict, python_writable_file):
    o = {'name': state_name, 'patch_dict': patch_dict}
    pickle.dump(o, python_writable_file)

# def read_patch_data_from_file(python_readable_file):
#     file_data = json.loads(python_readable_file.read())
#     return file_data.patch_dict


def create_basic_trackerfiles(trackerfiles_path, initial_patch_dict):
    with open(os.path.join(trackerfiles_path, CURRENT_STATE_POINTER_NAME), 'w') as file:
        file.write(INITIAL_STATE_NAME)
    os.mkdir(os.path.join(trackerfiles_path, STATES_FOLDER_NAME))
    with open(os.path.join(trackerfiles_path, STATES_FOLDER_NAME, INITIAL_STATE_NAME), 'wb') as initial_state_file:
        write_patch_data_to_file(INITIAL_STATE_NAME, initial_patch_dict, initial_state_file)


def CreateRepository ( Folder ) :
    patch_dict = compute_dmp_patch_dict({}, file_tree_loader.load_dict(os.path.abspath('.')))
    if not os.path.exists(Folder):
        os . mkdir ( Folder )
    if os.path.exists(os.path.join(Folder, TRACKER_FOLDER_NAME)):
        print(Folder + " is already a tracker repository")
    else:
        trackerfiles_path = os.path.join(Folder, TRACKER_FOLDER_NAME)
        os.mkdir(trackerfiles_path)
        create_basic_trackerfiles(trackerfiles_path, patch_dict)
        print("Repository " + Folder + " initialized successfully")


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
        Message = data.decode()
        print("Received message: " + Message)
        DataArray = Message . split ( )
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
    print('Sending repository \'' + RootFolder + '\' to ' + str ( client_address ) )
    Buffer = ''
    for root, subdirs, files in os.walk(os.getcwd() + '/' + RootFolder):
        Buffer = Buffer + '[' + root + '] folder\n'
        print ( Buffer )
        for SubFile in files :
            FilePath = root + '/' + SubFile
            Size = os.path.getsize(FilePath)
            with open(FilePath, 'r') as content_file:
                content = content_file.read()
            Buffer = Buffer + '[' + FilePath + '] file ' + Size + ' ' + Contents + '\n'
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

def diff_compute(args):
    if len(args) == 2:
        if args[0] == 'unsaved' and args[1] == 'changes':
            file_tree_loader.main()

def handle_save():
    if len(sys.argv) < 3:
        print("Syntax: tracker save [name of new tracker saved state]")
        return
    state_name = sys.argv[2]
    result = file_tree_loader.save(state_name)
    if result != '':
        print("Failed to save because " + result)

def get_current_abs_path():
    return os.path.abspath('.')

def get_trackerfiles_path_or_empty_string():
    try:
        trackerfiles_path = get_current_abs_path()
        prevdirs = set()
        while not os.path.exists(TRACKER_FOLDER_NAME):
            os.chdir('..')
            trackerfiles_path = get_current_abs_path()
            print(trackerfiles_path)
            if get_current_abs_path() in prevdirs:
                raise Exception("Reached root directory and did not find trackerfiles.  Not a tracker repository.")
            prevdirs.add(get_current_abs_path())
        return os.path.join(trackerfiles_path, TRACKER_FOLDER_NAME)
    except Exception:
        return ''

def get_current_state_name_or_none():
    trackerfiles_path = get_trackerfiles_path_or_empty_string()
    current_state_name = None
    if trackerfiles_path != '':
        with open(os.path.join(trackerfiles_path, CURRENT_STATE_POINTER_NAME), 'r') as currentStateFile:
            current_state_name = currentStateFile.read().strip()
    return current_state_name


def MainSwitch ( ) :
    if len ( sys.argv ) > 1 :
        if sys.argv [ 1 ] == 'CreateRepo' :
            CreateRepository ( sys.argv [ 2 ] )
        if sys.argv [ 1 ] == 'Host' :
            HostRepositories ( )
        if sys.argv [ 1 ] == 'Retrieve' :
            RetrieveRemoteRepository ( sys.argv [ 2 ] , sys.argv [ 3 ] )
        if sys.argv [ 1 ] == 'show':
            diff_compute(sys.argv[2:])
        if sys.argv[1] == 'save':
            handle_save()

if __name__=='__main__':
    MainSwitch ( )
