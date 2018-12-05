#!/usr/bin/env python3

"""
  _______ _____            _____ _  ________ _____
 |__   __|  __ \     /\   / ____| |/ /  ____|  __ \
    | |  | |__) |   /  \ | |    | ' /| |__  | |__) |
    | |  |  _  /   / /\ \| |    |  < |  __| |  _  /
    | |  | | \ \  / ____ \ |____| . \| |____| | \ \
    |_|  |_|  \_\/_/    \_\_____|_|\_\______|_|  \_\

A simple version control tool.

https://docs.google.com/document/d/1SUu2x6x-LrqnmmYJEgI1G2Ys-1FhmdwBmxoz39Atu8g/edit
"""

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
import shutil
import zipfile
import tarfile


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
    buf = 99999
    sock = get_host_sock()
    print("Waiting to receive messages...")
    while True:
        (data, client_address) = sock.recvfrom(buf)
        python_data = pickle.loads(data)
        if python_data[server.REMOTE_REPO_KEY] == os.path.basename(os.getcwd()) :
            if python_data[server.OPERATION_KEY] == server.UPLOAD:
                f = open('tmp.zip', 'wb')
                f.write(python_data[server.FILE_DICT_KEY])
                f.close()
                zip = zipfile.ZipFile('tmp.zip')
                with zipfile.ZipFile('tmp.zip', 'r') as zip_ref:
                    zip_ref.extractall(os.getcwd())
                os.remove('tmp.zip')
                print ( 'Received' , len ( python_data[server.FILE_DICT_KEY] ) , 'bytes' )


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
            elif python_data[server.OPERATION_KEY] == server.DOWNLOAD:
                print('Received download request')
                fantasy_zip = zipfile.ZipFile('tmp.zip', 'w')
                for folder, subfolders, files in os.walk(os.getcwd()):
                    for file in files:
                        fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file)), compress_type = zipfile.ZIP_DEFLATED)
                fantasy_zip.close()
                fileContent = ''
                zip = zipfile.ZipFile('tmp.zip')
                with open('tmp.zip', mode='rb') as file:
                    fileContent = file.read()
                #f = open('tmp2.zip', 'wb')
                #f.write(fileContent)
                # sock = get_client_sock()
                # host = ''
                data = pickle.dumps({
                    server.LOCAL_REPO_KEY: python_data[server.LOCAL_REPO_KEY],
                    server.OPERATION_KEY: server.DOWNLOAD,
                    server.FILE_DICT_KEY: fileContent,
                })
                port = 8000
                addr = (client_address[0], 8000)
                UDPSock = socket(AF_INET, SOCK_DGRAM)
                UDPSock.sendto(data, addr)
                print ( client_address , addr )
                print('fileContent = ' , fileContent)
                os.remove('tmp.zip')
    sock.close()
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
        for file_path in dict_at_current_state:
            if os.path.isfile(file_path):
                # delete the file
                os.remove(file_path)

                # delete empty containing folders
                if file_path[0] != '.':
                    raise Exception("prevented deleting non-relative path " + str(file_path))
                iterating_path = file_path
                count = 0
                while iterating_path.find(os.sep) >= 0 and count < 5000:
                    iterating_path, file_name = os.path.split(iterating_path)
                    if os.listdir(iterating_path) == []:
                        os.rmdir(iterating_path)
                if count >= 5000:
                    raise Exception("Infinite loop broken when processing path " + str(file_path))

        for file_path in dict_at_requested_state:
            containing_folder_path, file_name = os.path.split(file_path)
            my_makedirs(containing_folder_path)
            with open(file_path, 'wb') as file:
                file.write(diff.str_to_file_type(dict_at_requested_state[file_path]))

        set_current_state_name(requested_state_name)

        print("Successfully set current state to " + str(requested_state_name) + " and made working directory match")
    except Exception as e:
        traceback.print_exc()
        print("EXCEPTION:" + str(e))

def my_makedirs(path):
    if path.find(os.sep) < 0:
        return
    parent_path, child_name = os.path.split(path)
    my_makedirs(parent_path)
    if not os.path.exists(path):
        os.mkdir(path)

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


def handle_upload(RemoteRepo , IPAddress):
    local_state_name = ''
    remote_state_name = ''
    if len(sys.argv) != 4:
        print("Syntax: tracker upload [repo name] [ip addr]")
        return

    fantasy_zip = zipfile.ZipFile('tmp.zip', 'w')
    for folder, subfolders, files in os.walk(os.getcwd()):
        for file in files:
            fantasy_zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file)), compress_type = zipfile.ZIP_DEFLATED)
    fantasy_zip.close()
    fileContent = ''
    zip = zipfile.ZipFile('tmp.zip')
    with open('tmp.zip', mode='rb') as file:
        fileContent = file.read()
    #f = open('tmp2.zip', 'wb')
    #f.write(fileContent)
    # sock = get_client_sock()
    # host = ''
    data = pickle.dumps({
        server.REMOTE_REPO_KEY: RemoteRepo,
        server.OPERATION_KEY: server.UPLOAD,
        server.FILE_DICT_KEY: fileContent,
    })


    port = int(13000)
    addr = (IPAddress, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    print('fileContent = ' , fileContent)
    UDPSock.sendto(data, addr)
    os.remove('tmp.zip')
    # data = {'state_name' : remote_state_name, 'data_dict' : data_dict}
    # sock.sendto(pickle.dumps(data), addr)



def handle_download(RemoteRepo , IPAddress):
    if len(sys.argv) != 4:
        print("Syntax: tracker download [repo name] [ip addr]")
        return
    data = pickle.dumps({
        server.REMOTE_REPO_KEY: RemoteRepo,
        server.LOCAL_REPO_KEY: os.path.basename(os.getcwd()),
        server.OPERATION_KEY: server.DOWNLOAD,
    })
    port = int(13000)
    addr = (IPAddress, port)
    UDPSock = socket(AF_INET, SOCK_DGRAM)
    UDPSock.sendto(data, addr)
    print ( 'Download request sent' )

    buf = 99999
    UDPSock2 = socket(AF_INET, SOCK_DGRAM)
    addr2 = (IPAddress, 8000)
    UDPSock2.bind(addr2)
    (data, client_address) = UDPSock2.recvfrom(buf)
    python_data = pickle.loads(data)
    if python_data[server.LOCAL_REPO_KEY] == os.path.basename(os.getcwd()) :
        if python_data[server.OPERATION_KEY] == server.DOWNLOAD:
            f = open('tmp.zip', 'wb')
            f.write(python_data[server.FILE_DICT_KEY])
            f.close()
            zip = zipfile.ZipFile('tmp.zip')
            with zipfile.ZipFile('tmp.zip', 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
            os.remove('tmp.zip')
            print ( 'Received' , len ( python_data[server.FILE_DICT_KEY] ) , ' bytes' )


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
    print('tracker CreateRepo [folderpath]')
    print('tracker show')
    print('tracker save [statename]')
    print('tracker move [statename]')
    print('tracker Host')
    print('tracker upload [remotereponame] [remoteip]')
    print('tracker download [remotereponame] [remoteip]')

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
            handle_upload(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == 'download':
            handle_download(sys.argv[2], sys.argv[3])
        else:
            printHelp()
    else:
        printHelp()

if __name__=='__main__':
    MainSwitch ( )
