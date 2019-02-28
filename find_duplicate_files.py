#!/usr/bin/python3

from hashlib import md5
from os import path, walk
from argparse import ArgumentParser
from json import dumps


def read_args():
    finder = ArgumentParser()
    finder.add_argument('-p', '--path',
                        help="directory want to find duplicate",)
    return finder.parse_args()


def scan_files(directory):
    '''
    Task:   - First get absolutely path passed
            - Scan file in dir, subdirs
    '''
    base_path = path.abspath(directory)
    all_files = []
    for root, _, files in walk(base_path):
        for name in files:
            path_name = path.join(root, name)
            if not path.islink(path_name):
                all_files.append(path_name)
    return all_files


def group_files_by_size(file_path_names):
    '''
    Task:   - Read size each file, size will be key and file append in list
            - Take group have more than 1 file and size not equal zero
    '''
    files_same_size = {}
    for file in file_path_names:
        files_same_size.setdefault(path.getsize(file), []).append(file)
    return [group for size, group in files_same_size.items()
            if len(group) > 1 and size]


def get_file_checksum(name_file):
    '''
    Task:   - Return hash md5 of file passed
    '''
    with open(name_file, 'rb') as f:
        return md5(f.read()).hexdigest()


def group_files_by_checksum(file_path_names):
    '''
    Task:   - Checksum each file, checksum will be key and file append in list
            - If don't have permisson to read then ignore that file
            - Take group have more than 1 file
    '''
    files_same_checksum = {}
    for file in file_path_names:
        try:
            checksum = get_file_checksum(file)
            files_same_checksum.setdefault(checksum, []).append(file)
        except PermissionError:
            pass
    return [group for group in files_same_checksum.values() if len(group) > 1]


def find_duplicate_files(file_path_names):
    '''
    Task:   - Fist take each group in same size
            - Then group them in same checksum
            - Afterward add group have more than 1 file into duplicate
    '''
    duplicate_files = []
    for group_size in group_files_by_size(file_path_names):
        for group in group_files_by_checksum(group_size):
            duplicate_files.append(group)
    return duplicate_files


def main():
    '''
    Task:   - Get argument passed from user then check input is valid
            - Scan all of file inside that directory
            - Find duplicate files
            - Ouput a format expression json for duplicate files
    '''
    args = read_args()
    if args.path and not path.isdir(args.path):
        print("Invalid path")
        exit(1)
    files = scan_files(args.path or ".")
    duplicates = find_duplicate_files(files)
    print(dumps(duplicates, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
