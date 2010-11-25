This is a suite of tools for automating 1D poisson and parsing the output for a multiple quantum well potential.

To use *batch_run.py*, execute

> python batch_run.py

in the directory containing 1D Poisson. I'll be adding configuration files later so this does not need to be in the same directory.

To use get_energies.py, execute

> python get_energies.py -f {PATH_TO_FILE} -n {WHICH_WELL}

PATH_TO_FILE is the path to the output from batch.py. So if you have a file
called ~/output/Qwell070.txt, then you would provide ~/output/Qwell070 (no .txt). WHICH_WELL specifies which of the several wells to look at.
