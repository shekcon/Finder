#!/usr/bin/python3

from hashlib import md5
import os
from argparse import ArgumentParser
import json
import time


def read_args():
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
    return [group for size, group in files_same_size.items() if len(group) > 1 and size]


def get_file_checksum(name_file):
    '''
    Task: return hash md5 of file passed
    '''
    with open(name_file, 'rb') as f:
        return md5(f.read()).hexdigest()


def group_files_by_checksum(file_path_names):
    files_same_checksum = {}
    for file in file_path_names:
        checksum = get_file_checksum(file)
        files_same_checksum.setdefault(checksum, []).append(file)
    return [group for group in files_same_checksum.values() if len(group) > 1]


def find_duplicate_files(file_path_names):
    duplicate_files = []
    for group_size in group_files_by_size(file_path_names):
        for group in group_files_by_checksum(group_size):
            duplicate_files.append(group)
    return duplicate_files


def main():
    args = read_args()
    files = scan_files(args.path)
    print(json.dumps(find_duplicate_files(files), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
