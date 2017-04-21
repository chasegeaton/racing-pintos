
# Racing PintOS

This can be used to test for race conditions in a PintOS project.

## Usage

    ./racing-pintos.py [-p N] [-t N] PATH PROJECT

The `-p` flag specifies how many concurrent processes to spawn.

The `-t` flag specifies how many times each processes repeats the tests.

`PATH` is the path to the root PintOS directory that contains the source.

`PROJECT` is the PintOS project that is to be tested.

## Example

    ./racing-pintos.py src threads

This will test the threads project from the PintOS directory called `src` with one
process and each process will run the tests only once.

    ./racing-pintos.py -p 5 -t 5 pintos vm

This will test the vm project from the PintOS directory `pintos` using five
processes and each process will run the tests five times.

## Results

### `result_summary.output`

This file contains a summary of the results for each process. It is stored in
the same directory as where the script is run.

### `raw-test-results.output` and `raw-test-builds.output`

These files contain the raw build output and the raw test output for every run
of the tests.
