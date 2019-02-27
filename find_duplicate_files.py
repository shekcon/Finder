#!/usr/bin/python3

import hashlib
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
        size = os.stat(file).st_size
        if size:
            files_same_size.setdefault(size, []).append(file)
    return [same_size for _, same_size in files_same_size.items() if len(same_size) > 1]


def main():
    args = handle_args()
    files = scan_files(args.path)
    group_files_by_size()

if __name__ == "__main__":
    main()