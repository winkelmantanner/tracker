#!/usr/bin/env python3
# Save as server.py 
# Message Receiver
import os
import sys
import traceback
import file_tree_loader
import diff
from diff import compute_dmp_patch_dict
import pickle
import server
from socket import *
import requests


TRACKER_FOLDER_NAME = 'trackerfiles'
CURRENT_STATE_POINTER_NAME = 'currentState'
INITIAL_STATE_NAME = "INITIAL"
STATES_FOLDER_NAME = 'states'

SERVER_URL = 'http://127.0.0.1:8000'

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


class ServerCommand:
    UPLOAD = b'u'
    DOWNLOAD = b'd'

def get_client_sock():
    host = ""
    port = 13000
    addr = (host, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind(addr)
    return UDPSock

def get_host_sock():
    host = ""
    port = 13000
    addr = (host, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.bind(addr)
    return UDPSock

def HostRepositories ( ) :
    buf = 1024
    sock = get_host_sock()
    print("Waiting to receive messages...")
    while True:
        (data, client_address) = sock.recvfrom(buf)
        if data[0] == ServerCommand.UPLOAD:
            python_data = pickle.loads(data[1:])
            new_state_name = python_data['new_state_name']
            previous_state_name = python_data['previous_state_name']
            data_dict = python_data['data_dict']
            result = file_tree_loader.save_dict(new_state_name, data_dict)
            print(result)
        # elif data[0] == ServerCommand.DOWNLOAD:


        # Message = data.decode()
        # print("Received message: " + Message)
        # DataArray = Message . split ( )
        # print(DataArray)
        # if data == "exit":
        #     break
        # if DataArray [ 0 ] == 'Copy':
        #     print('FOUND Copy')
        # if DataArray [ 0 ] == 'Retrieve':
        #     SendRepository ( DataArray [ 1 ] , client_address )
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
    print("Showing changes from saved state " + str(get_current_state_name()))
    context_diff = file_tree_loader.current_context_diff()
    if context_diff.strip() == '':
        print('No changes detected')
    else:
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

def handle_move():
    if len(sys.argv) != 3:
        print("Syntax: tracker move [name previously saved state]")
        return
    # do not move if there are unsaved changes
    current_context_diff = ''
    try:
        current_context_diff = file_tree_loader.current_context_diff().strip()
        if current_context_diff.strip() != '':
            print("Failed to move because there are unsaved changes.  You can see them with 'tracker show'."
                  "  Use 'tracker save [saved state name]' to save them before moving.")
            return
    except Exception as e:
        print("error while computing diff: " + str(e))
        print("attempting move anyway")
    requested_state_name = sys.argv[2]
    dict_at_requested_state = {}
    try:
        dict_at_requested_state = file_tree_loader.compute_file_system_state_from_history(requested_state_name)
    except IOError:
        print("Failed because unable to find state " + requested_state_name)
        return
    try:
        # first, delete all files in current state
        # then, create all files in destination state
        current_state_name = get_current_state_name()
        dict_at_current_state = file_tree_loader.compute_file_system_state_from_history(current_state_name)

        file_tree_loader.delete_files_in_dict(dict_at_current_state)

        file_tree_loader.create_files_in_dict(dict_at_requested_state)

        set_current_state_name(requested_state_name)

        print("Successfully set current state to " + str(requested_state_name) + " and made working directory match")
    except Exception as e:
        traceback.print_exc()
        print("EXCEPTION:" + str(e))

def handle_apply():
    if len(sys.argv) != 7 or sys.argv[2] != 'changes' or sys.argv[3] != 'from' or sys.argv[5] != 'to':
        print("Syntax: tracker apply changes from [state 1] to [state 2]")
    else:
        state_name_from = sys.argv[4]
        state_name_to = sys.argv[6]
        state_dict_from = {}
        try:
            state_dict_from = file_tree_loader.compute_file_system_state_from_history(state_name_from)
        except IOError as ioe:
            print("Could not load state " + state_name_from)
        state_dict_to = {}
        try:
            state_dict_to = file_tree_loader.compute_file_system_state_from_history(state_name_to)
        except IOError as ioe:
            print("Could not load state " + state_name_to)

        try:
            current_context_diff = file_tree_loader.current_context_diff().strip()
            if current_context_diff.strip() != '':
                print("Failed to apply because there are unsaved changes.  You can see them with 'tracker show'."
                      "  Use 'tracker save [saved state name]' to save them before applying changes.")
                return
        except Exception as e:
            print("error while computing diff: " + str(e))
            print("attempting apply anyway")

        dmp_diff_dict = diff.compute_dmp_diff_dict(state_dict_from, state_dict_to)
        current_state_name = get_current_state_name()
        dict_at_current_state = file_tree_loader.compute_file_system_state_from_history(current_state_name)
        patch_dict = diff.compute_dmp_patch_dict_from_dmp_diff_dict(dict_at_current_state, dmp_diff_dict)
        result_dict = diff.apply_dmp_patch_dict(dict_at_current_state, patch_dict)

        file_tree_loader.delete_files_in_dict(dict_at_current_state)
        file_tree_loader.create_files_in_dict(result_dict)

        print("Applied changes successfully")


def handle_upload():
    local_state_name = ''
    remote_state_name = ''
    if len(sys.argv) == 5:
        if sys.argv[3] != 'as':
            print("Syntax: tracker upload [state name] as [name on server]")
            return
        local_state_name = sys.argv[2]
        remote_state_name = sys.argv[4]
    elif len(sys.argv) == 3:
        local_state_name = sys.argv[2]
        remote_state_name = sys.argv[2]
    else:
        print("Syntax: tracker upload [state name] (as [name on server])?")
        print("Creates a state on the server.")
        print("The remote state will be called [name on server] if provided.")
        print("Otherwise it will be called [state name].")
        print("The remote state will be equivalent to the local state given by [state name].")
        return
    data_dict = file_tree_loader.compute_file_system_state_from_history(local_state_name)
    response = requests.post(SERVER_URL, data=pickle.dumps({
        server.STATE_NAME_KEY: remote_state_name,
        server.FILE_DICT_KEY: data_dict,
    }))
    # sock = get_client_sock()
    # host = ''
    # port = 13000
    # addr = (host, port)
    # data = {'state_name' : remote_state_name, 'data_dict' : data_dict}
    # sock.sendto(pickle.dumps(data), addr)
    result_string = str(response.content, encoding='utf-8')
    if result_string != '':
        print("Failed.  Server says: " + str(response.content, encoding='utf-8'))
    elif response.status_code != 200:
        print("Server responded with status code " + str(response.status_code) + ", which is not the expected value 200."
            "  However, server did not return an explanation")
    else:
        print("Server responded with success")






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
        elif sys.argv[1] == 'move':
            handle_move()
        elif sys.argv[1] == 'apply':
            handle_apply()
        elif sys.argv[1] == 'upload':
            handle_upload()
        else:
            printHelp()
    else:
        printHelp()

if __name__=='__main__':
    MainSwitch ( )
