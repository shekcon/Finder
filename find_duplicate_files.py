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
    print(directory)
    for root, dirs, files in os.walk(directory):
        for name in files:
            print(os.path.join(root, name))
        for name in dirs:
            print(os.path.join(root, name))


def main():
    args = handle_args()
    path = args.path
    scan_files(path)

if __name__ == "__main__":
    main()