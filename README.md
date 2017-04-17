
# Racing PintOS

This can be used to test for race conditions in a PintOS project.

Usage:

    ./racing-pintos.py [-p N] [-t N] PATH PROJECT

The -p flag specifies how many concurrent processes to spawn.

The -t flag specifies how many times each processes repeats the tests.

PATH is the path to the root PintOS directory that contains the source.

PROJECT is the PintOS project that is to be tested.

# Example:

    ./racing-pintos.py src threads

This will test the threads project with one process and run the tests only once.

    ./racing-pintos.py -p 5 -t 5 src vm

This will test the vm project with five processes and run the tests five times
for each process.
