#!/usr/bin/python3

from hashlib import md5
import os
from argparse import ArgumentParser

def handle_args():
    finder = ArgumentParser()
    finder.add_argument('-p', '--path',
                       help="directories want to find duplicate",)
    return finder.parse_args()
    

def scan_files(directory):
    base_path = os.path.abspath(directory)
    all_files = []
    for root, dirs, files in os.walk(base_path):
        for name in files:
            all_files.append(os.path.join(root, name))
    return all_files


def group_files_by_size(file_path_names):
    files_same_size = {}
    for file in file_path_names:
        files_same_size.setdefault(os.stat(file).st_size, []).append(file)
    return [same_size for size, same_size in files_same_size.items() if len(same_size) > 1 and size]


def get_file_checksum(name_file):
    '''
    Task: return hash md5 of file passed
    '''
    with open(file, 'rb') as f:
        return md5(f.read()).hexdigest()
    

def group_files_by_checksum(file_path_names):
    files_same_checksum = {}
    for file in file_path_names:
        checksum = get_file_checksum(file)
        files_same_size.setdefault(checksum, []).append(file)
    return [same_checksum for _, same_checksum in files_same_checksum.items() if len(same_checksum) > 1]


def main():
    args = handle_args()
    files = scan_files(args.path)
    group_files_by_size()

if __name__ == "__main__":
    main()