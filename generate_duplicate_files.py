#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Intek Institute.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Intek Institute or one of its subsidiaries.  You shall not disclose
# this confidential information and shall use it only in accordance
# with the terms of the license agreement or other applicable
# agreement you entered into with Intek Institute.
#
# INTEK INSTITUTE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.  INTEK
# INSTITUTE SHALL NOT BE LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY
# LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THIS
# SOFTWARE OR ITS DERIVATIVES.

import argparse
import errno
import io
import json
import os
import random
import shutil
import string


ONE_KB = 1024
ONE_MB = ONE_KB * 1024
ONE_GB = ONE_MB * 1024

# List of allowed characters that can be used to randomly generate the
# name of a sub-directory.
DIRECTORY_NAME_CHARACTERS = ''.join(['%x' % i for i in range(16)])

# List of allowed characters that can be used to randomly generate the
# name of a file, and its extension.
FILE_NAME_CHARACTERS = '-_%s%s' % (string.ascii_letters, string.digits)

# Default minimum size of a file to randomly generate.
FILE_MIN_SIZE = ONE_KB

# Default maximum size of a file to randomly generate.
FILE_MAX_SIZE = ONE_GB


def build_tree_pathname(file_name, directory_depth=8, pathname_separator_character=os.sep):
    """
    Return a pathname built of the specified number of sub-directories,
    and where each directory is named after the nth letter of the filename
    corresponding to the directory depth.

    Examples::

      >>> build_tree_pathname('foo.txt', 2, '/')
      'f/o/'
      >>> build_tree_pathname('0123456789abcdef')
      '0/1/2/3/4/5/6/7/'


    @param file_name: name of a file, with or without extension.

    @param directory_depth: number of sub-directories to be generated.

    @param pathname_separator_character: character to be used to separate
           pathname components, such as '/' for POSIX and '\\' for
           Windows.  If not defined, the default is the character used by
           the operating system ``os.sep``.


    @return: a file pathname.
    """
    (filename_without_extension, _file_extension_) = os.path.splitext(file_name)

    assert directory_depth <= len(filename_without_extension), 'The number of sub-directories to be generated is above the length of the file name'

    return ''.join(['%s%s' % (filename_without_extension[i], pathname_separator_character)
        for i in range(min(directory_depth, len(filename_without_extension)))])


def duplicate_file(source_file_path_name, destination_file_path_name):
    """
    Duplicate a source file to another path.


    @param source_file_path_name: absolute path and name of a file to
        duplicate (copy).

    @param destination_file_path_name: absolute path and name of the
        destination of this source file.
    """
    shutil.copyfile(source_file_path_name, destination_file_path_name)


def generate_files(file_count,
        directory_max_depth=8,
        directory_min_depth=None,
        duplicate_file_ratio=0.2,
        file_extensions=None,
        file_extension_max_length=3,
        file_extension_min_length=3,
        file_name_characters=FILE_NAME_CHARACTERS,
        file_name_max_length=8,
        file_name_min_length=1,
        file_min_size=FILE_MIN_SIZE,
        file_max_size=FILE_MAX_SIZE,
        root_path=None):
    """
    Generate random files with a certain ratio of duplicate files.


    @param file_count: number of file to generate.

    @param directory_max_depth: maximum number of sub-directories to
        generate a file from the specified root path.

    @param directory_min_depth: minimal number of sub-directories to
        generate a file from the specified root path.

    @param duplicate_file_ratio: ratio of duplicate files to be generated.

    @param file_extensions: list of allowed file extensions to be used
        when generate files (e.g., ``['gif', 'jpg', 'mp3']``).

    @param file_extension_max_length: maximum length of a file extension
        to randomly generate.

    @param file_extension_min_length: minimum length of a file extension
        to randomly generate.

    @param file_name_characters: allowed characters that can be used to
        randomly generate a file name.

    @param file_name_max_length: maximum length of a file name to randomly
        generate.

    @param file_name_min_length: minimum length of a file name to randomly
        generate.

    @param file_max_size: maximum size of a file to randomly generate.

    @param file_min_size: minimum size of a file to randomly generate.

    @param root_path: absolute root path where to generate files.


    @return: the list of `(file_path_name, file_size)` of files that have
        been generated.
    """
    file_path_name_sizes = []
    duplicate_file_path_names = []

    for i in range(file_count):
        path = os.path.join(root_path if root_path else '.', generate_random_path(
            directory_max_depth=directory_max_depth,
            directory_min_depth=directory_min_depth))
        make_directory_if_not_exists(path)

        file_name = generate_random_file_name(
            file_extensions=file_extensions,
            file_extension_min_length=file_extension_min_length,
            file_extension_max_length=file_extension_max_length,
            file_name_characters=file_name_characters,
            file_name_min_length=file_name_min_length,
            file_name_max_length=file_name_max_length)

        file_path_name = os.path.join(path, file_name)

        if len(file_path_name_sizes) * duplicate_file_ratio > len(duplicate_file_path_names):
            duplicate_file(file_path_name_sizes[random.randint(0, len(file_path_name_sizes) - 1)][0], file_path_name)
            duplicate_file_path_names.append(file_path_name)

        else:
            file_size = generate_random_file(file_path_name,
                file_min_size=file_min_size,
                file_max_size=file_max_size)

        file_path_name_sizes.append((file_path_name, file_size))

    return file_path_name_sizes


def generate_random_file(file_path_name,
        file_min_size=FILE_MIN_SIZE,
        file_max_size=FILE_MAX_SIZE):
    """
    Create a binary file of a random size of bytes.


    @param file_path_name: absolute path name of the file to be created.

    @param file_min_size: minimum size in bytes of the file to randomly
        generate.

    @param file_max_size: maximum size in bytes of the file to randomly
        generate.


    @return: the size of the file that has been created.
    """
    # Choose a random size for this file.
    file_required_size = random.randint(file_min_size, file_max_size)
    file_current_size = 0

    # Preferred file system block size.
    preferred_block_size = os.statvfs('/').f_bsize

    # Reduce the size of the block if the chosen size of the file to be
    # generated is below.
    block_size = min(file_required_size, preferred_block_size)

    # Create the file with random binary blocks up to the chosen size of
    # this file.
    with io.open(file_path_name, mode='wb') as fd:
        while block_size:
            fd.write(bytes([random.randint(0, 255) for i in range(block_size)]))

            file_current_size += block_size

            if file_current_size + block_size > file_required_size:
                block_size = file_required_size - file_current_size

    return file_required_size


def generate_random_file_name(
        file_extensions=None,
        file_extension_min_length=3,
        file_extension_max_length=3,
        file_name_characters=FILE_NAME_CHARACTERS,
        file_name_min_length=1,
        file_name_max_length=8):
    """
    Generate a random name of a file.


    @param file_extensions: list of allowed file extensions.

    @param file_extension_min_length: minimum length of a file extension
        to randomly generate, if the argument ``file_extensions`` is not
         passed to this function.

    @param file_extension_max_length: maximum length of a file extension
        to randomly generate, if the argument ``file_extensions`` is not
        passed to this function.

    @param file_name_characters: list of characters that are allowed to
        generate the file name.

    @param file_name_min_length: minimal length of a file name to randomly
        generate.

    @param file_name_max_length: maximum length of a file name to randomly
        generate.


    @return: a file name.
    """
    base_file_name = ''.join([file_name_characters[random.randint(0, len(file_name_characters) - 1)]
        for _ in range(random.randint(file_name_min_length, file_name_max_length))])

    if file_extension_max_length == 0:
        return base_file_name

    file_name_extension = file_extensions[random.randint(0, len(file_extensions) - 1)] if file_extensions \
        else ''.join([file_name_characters[random.randint(0, len(file_name_characters) - 1)]
            for _ in range(random.randint(file_extension_min_length, file_extension_max_length))])

    return ''.join([base_file_name, os.path.extsep, file_name_extension])



def generate_random_path(directory_max_depth,
        directory_min_depth=None,
        directory_name_characters=DIRECTORY_NAME_CHARACTERS):
    """
    Generate a random path.


    @note: the function does not create any path on the disk, it just
        generates a string.


    @param directory_max_depth: maximum number of sub-directories to
        generate a file from the specified root path.

    @param directory_min_depth: minimal number of sub-directories to
        generate a file from the specified root path.

    @param directory_name_characters: list of characters that are allowed
        to use to generate each path component.


    @return: a random relative path.
    """
    return os.path.join(*[directory_name_characters[random.randint(0, len(directory_name_characters) - 1)]
        for _ in range(directory_max_depth if directory_min_depth is None \
            else random.randint(directory_min_depth, directory_max_depth))])


def main():
    """
    Entry point of the script.
    """
    arguments = parse_arguments()

    print(json.dumps(generate_files(arguments.file_count,
        directory_max_depth=arguments.directory_max_depth,
        directory_min_depth=arguments.directory_min_depth,
        duplicate_file_ratio=arguments.duplicate_file_ratio,
        file_extensions=arguments.file_extensions and arguments.file_extensions.split(','),
        file_extension_max_length=arguments.file_extension_max_length,
        file_extension_min_length=arguments.file_extension_min_length,
        file_name_characters=FILE_NAME_CHARACTERS,
        file_name_max_length=arguments.file_name_max_length,
        file_name_min_length=arguments.file_name_min_length,
        file_min_size=arguments.file_min_size,
        file_max_size=arguments.file_max_size,
        root_path=arguments.root_path)))


def make_directory_if_not_exists(path):
    """
    Create the specified path, making all intermediate-level directories
    needed to contain the leaf directory.  Ignore any error that would
    occur if the leaf directory already exists.


    @note: all the intermediate-level directories are created with the
        default mode is 0777 (octal).


    @param path: the path to create.


    @raise OSError: an error that would occur if the path cannot be
        created.
    """
    try:
        os.makedirs(path)
    except OSError as error: # Ignore if the directory has been already created.
        if error.errno != errno.EEXIST:
            raise error


def parse_arguments():
    """
    Convert argument strings to objects and assign them as attributes of
    the namespace.


    @return: an instance ``argparse.Namespace`` corresponding to the
        populated namespace.
    """
    parser = argparse.ArgumentParser(description='Duplicate Files Generator')
    parser.add_argument('--file-count', type=int, required=True,
        help='specify the number of files to generate')

    parser.add_argument('-p', '--path', dest='root_path', metavar='filename', required=False, default='.',
        help='specify the absolute path where to generate files')

    parser.add_argument('--directory-min-depth', type=int, required=False,
        help='specify the maximum number of sub-directories to generate a file from the specified root path')
    parser.add_argument('--directory-max-depth', type=int, required=False, default=8,
        help='specify the maximum number of sub-directories to generate a file from the specified root path')

    parser.add_argument('--duplicate-file-ratio', type=float, required=False, default=0.2,
        help='specify the ratio of duplicate files to be generated')

    parser.add_argument('--file-extensions', required=False,
        help='specify a comma-separated values of file extension to be used when generate files (e.g., "gif,jpg,mp3")')

    parser.add_argument('--file-extension-min-length', type=int, required=False, default=3,
        help='specify the minimum length of a file extension to randomly generate')
    parser.add_argument('--file-extension-max-length', type=int, required=False, default=3,
        help='specify the maximum length of a file extension to randomly generate')

    parser.add_argument('--file-name-min-length', type=int, required=False, default=3,
        help='specify the minimum length of a file name to randomly generate')
    parser.add_argument('--file-name-max-length', type=int, required=False, default=3,
        help='specify the maximum length of a file name to randomly generate')

    parser.add_argument('--file-min-size', type=int, required=False, default=FILE_MIN_SIZE,
        help='specify the minimum size of a file to randomly generate')
    parser.add_argument('--file-max-size', type=int, required=False, default=FILE_MAX_SIZE,
        help='specify the maximum size of a file to randomly generate')

    return parser.parse_args()


if __name__ == '__main__':
    main()
