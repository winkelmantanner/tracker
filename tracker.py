#!/usr/bin/env python3
# Save as server.py 
# Message Receiver
import os
import sys
import traceback
import file_tree_loader
from diff import compute_dmp_patch_dict
import pickle
from socket import *


TRACKER_FOLDER_NAME = 'trackerfiles'
CURRENT_STATE_POINTER_NAME = 'currentState'
INITIAL_STATE_NAME = "INITIAL"
STATES_FOLDER_NAME = 'states'

def write_patch_data_for_state(state_name, previous_state_name, patch_dict):
    write_state(state_name, previous_state_name, patch_dict, get_states_folder_path())

def write_state(state_name, previous_state_name, patch_dict, state_path):
    o = {'previous_state_name': previous_state_name, 'patch_dict': patch_dict}
    with open(os.path.join(state_path, state_name), 'wb') as state_file:
        pickle.dump(o, state_file)

def read_previous_state_name_and_patch_data_from_file(state_name):
    with open(os.path.join(get_states_folder_path(), state_name), 'rb') as state_file:
        file_data = pickle.load(state_file)
    return file_data['previous_state_name'], file_data['patch_dict']

def get_current_state_name():
    current_state = ''
    with open(os.path.join(get_trackerfiles_path_or_empty_string(), CURRENT_STATE_POINTER_NAME), 'r') as currentStateFileIterable:
        current_state = currentStateFileIterable.read()
    return current_state.strip()

def set_current_state_name(new_current_state_name):
    with open(os.path.join(get_trackerfiles_path_or_empty_string(), CURRENT_STATE_POINTER_NAME), 'w') as currentStatePythonFile:
        currentStatePythonFile.write(new_current_state_name)


def CreateRepository ( Folder ) :
    patch_dict = compute_dmp_patch_dict({}, file_tree_loader.load_dict(Folder))
    if not os.path.exists(Folder):
        os . mkdir ( Folder )
    os.chdir(Folder) # CHANGE DIRECTORY
    if os.path.exists(os.path.join(TRACKER_FOLDER_NAME)):
        print(Folder + " is already a tracker repository")
    else:
        # now we are at the root of the repo
        print(os.getcwd())
        os.mkdir(TRACKER_FOLDER_NAME)
        with open(os.path.join(TRACKER_FOLDER_NAME, CURRENT_STATE_POINTER_NAME), 'w') as file:
            file.write(INITIAL_STATE_NAME)
        os.mkdir(os.path.join(TRACKER_FOLDER_NAME, STATES_FOLDER_NAME))
        write_patch_data_for_state(INITIAL_STATE_NAME, None, patch_dict)
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

def handle_show(args):
    print(file_tree_loader.current_context_diff())

def handle_save():
    if len(sys.argv) != 3:
        print("Syntax: tracker save [name of new tracker saved state]")
        return
    state_name = sys.argv[2]
    result = file_tree_loader.save(state_name)
    if result != None and result != '':
        print("Failed to save because " + result)
    else:
        print("Successful")

def get_current_abs_path():
    return os.path.abspath('.')

def get_trackerfiles_parent_path_or_empty_string():
    try:
        trackerfiles_path = '.'
        prevdirs = set()
        while not os.path.exists(TRACKER_FOLDER_NAME):
            os.chdir('..')
            trackerfiles_path = get_current_abs_path()
            if get_current_abs_path() in prevdirs:
                raise Exception("Reached root directory and did not find trackerfiles.  Not a tracker repository.")
            prevdirs.add(get_current_abs_path())
        return trackerfiles_path
    except Exception:
        return ''

def get_trackerfiles_path_or_empty_string():
    parent_path = get_trackerfiles_parent_path_or_empty_string()
    return os.path.join(parent_path, TRACKER_FOLDER_NAME)

def get_states_folder_path():
    trackerfiles_path = get_trackerfiles_path_or_empty_string()
    if trackerfiles_path != '':
        return os.path.join(trackerfiles_path, STATES_FOLDER_NAME)
    else:
        return ''

def get_current_state_name_or_none():
    trackerfiles_path = get_trackerfiles_path_or_empty_string()
    current_state_name = None
    if trackerfiles_path != '':
        with open(os.path.join(trackerfiles_path, CURRENT_STATE_POINTER_NAME), 'r') as currentStateFile:
            current_state_name = currentStateFile.read().strip()
    return current_state_name

def printHelp():
    print("Tracker - an easier to use program similar to git")
    print('tracker CreateRepo [folder]')
    print('tracker show')
    print('tracker save [name]')

def MainSwitch ( ) :
    if len ( sys.argv ) > 1 :
        if sys.argv [ 1 ] == 'CreateRepo' :
            CreateRepository ( sys.argv [ 2 ] )
        elif sys.argv [ 1 ] == 'Host' :
            HostRepositories ( )
        elif sys.argv [ 1 ] == 'Retrieve' :
            RetrieveRemoteRepository ( sys.argv [ 2 ] , sys.argv [ 3 ] )
        elif sys.argv [ 1 ] == 'show':
            handle_show(sys.argv[2:])
        elif sys.argv[1] == 'save':
            handle_save()
        else:
            printHelp()
    else:
        printHelp()

if __name__=='__main__':
    MainSwitch ( )
