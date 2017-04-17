#!/usr/bin/env python3

# MIT License
# 
# Copyright (c) 2017 Chase G. Eaton
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# TODO: switch over to shutil for directory removal, creation, and copying


import os
import sys
import argparse
import time
import datetime
import subprocess
import multiprocessing
import logging


loglev = logging.ERROR

num_processes = 1
num_tests = 1

test_dir = './race-testing'
pintos_dir = 'src'
project = 'threads'

processes = []
retvals = []


def run_tests(test_num, path, q):
    directory = os.path.join(path, project)
    os.chdir(directory)
    logging.debug('process {} in directory {}'.format(test_num, directory))

    b = open('raw-test-builds.output', 'a')
    c = open('raw-test-results.output', 'a')

    logging.debug('process {} starting tests'.format(test_num))

    fail_count = 0
    for i in range(num_tests):
        logging.debug('process {} test {} build'.format(test_num, i))
        stat = subprocess.run(['make', '--always-make'], stdout=b, stderr=b)
        if stat.returncode != 0:
            logging.error('pintos build error')
            sys.exit(1)

        logging.debug('process {} test {} check'.format(test_num, i))
        ret = subprocess.run(['make', '-C', 'build', 'check'],
                             stdout=c, stderr=c)
        fail_count = fail_count + ret.returncode

    b.close()
    c.close()

    q.put((test_num, fail_count))
    logging.debug('process {} finished'.format(test_num))


def main():
    q = multiprocessing.Queue()

    print("setting up testing directories");

    stat = subprocess.run(['rm', '-rf', test_dir])
    if stat.returncode != 0:
        logging.error('failed to remove old testing directory')
        sys.exit(1)

    stat = subprocess.run(['mkdir', test_dir])
    if stat.returncode != 0:
        logging.error('failed to make new testing directory')
        sys.exit(1)

    logging.debug('created testing directory {}'.format(test_dir))

    for i in range(num_processes):
        src_name = "{}{}".format(os.path.basename(pintos_dir), i)
        dest = os.path.join(test_dir, src_name)

        stat = subprocess.run(['cp', '-r', pintos_dir, dest])
        if stat.returncode != 0:
            logging.error('failed to copy pintos')
            sys.exit(1)

        logging.debug('created pintos directory {} at {}'.format(i, dest))

        p = multiprocessing.Process(target=run_tests, args=(i, dest, q),
                                    name=src_name)
        processes.append(p)

    print("running tests (this will take a while)")

    print('start time: {}'.format(datetime.datetime.now()))
    start = time.time()

    for i, p in enumerate(processes):
        p.start()
        logging.debug('process {} started'.format(i))

    for i, p in enumerate(processes):
        p.join()
        logging.debug('process {} joined'.format(i))

    delta = time.time() - start

    print("finished all tests")

    print('end time: {}'.format(datetime.datetime.now()))
    elapsed = datetime.timedelta(seconds=delta)

    time_taken = 'testing process took: {}'.format(str(elapsed))
    print(time_taken)

    while not q.empty():
        rval = q.get()
        retvals.append(rval)
        logging.debug('retval: {}'.format(rval))

    retvals.sort(key=lambda tp: tp[0])
    with open('result_summary.output', 'w') as f:
        for r in retvals:
            if r[1] == 0:
                res = 'process {}: passed'.format(r[0])
            else:
                res = 'process {}: FAILED with {} failed runs'.format(r[0], r[1])
            print(res)
            f.write(res)
        f.write(time_taken)


if __name__ == '__main__':
    logging.basicConfig(level=loglev)

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to your pintos directory',
                        metavar="PATH")
    parser.add_argument('project', help='name of the project you are testing',
                        choices=['threads', 'userprog', 'vm', 'filesys'],
                        metavar='PROJECT')
    parser.add_argument('-p', '--processes',
                        help='number of separate process to run tests in',
                        type=int, default=1, metavar='N')
    parser.add_argument('-t', '--times',
                        help='number of tests for process to run',
                        type=int, default=1, metavar='N')
    args = parser.parse_args()

    num_processes = args.processes
    num_tests = args.times
    project = args.project

    pintos_dir = os.path.relpath(args.path)
    if not (os.path.exists(pintos_dir) and os.path.isdir(pintos_dir)):
        logging.error('path to pintos does not exist')
        sys.exit(1)

    main()
