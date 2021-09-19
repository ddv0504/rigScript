bifrostBatchSim

bifrostBatchSim.mel

----------------------

These two scripts (the first Python, the second MEL) work together to help you run a simulation from the command line. To use these scripts, you’ll have to be able to run Python from the command line. On Linux and Mac this is built-in, but on Windows you will have to install Python, as well as a terminal in which to run the script, such as Cygwin.

Place bifrostBatchSim in your $HOME/bin folder, and bifrostBatchSim.mel in your $HOME/maya/scripts folder (or Documents/maya/scripts, if on Windows).

Once installed (and your $PATH includes your $HOME/bin folder), you can run bifrostBatchSim from anywhere. If you provide the -h/--help argument, you will get a usage message:

% bifrostBatchSim -h
Using MAYA_LOCATION: /Applications/autodesk/maya2016
usage: bifrostBatchSim [-h] --start START --end END --out_dir OUT_DIR filename

A simple wrapper to run a Bifrost simulation in batch. This enables us to cache data from the command line, without the overhead of the Maya UI.

positional arguments:

  filename              Name of file to cache.

optional arguments:

  -h, --help            show this help message and exit
  --start START, -s START
                        The start frame of the simulation.
  --end END, -e END     The end frame of the simulation.
  --out_dir OUT_DIR, -o OUT_DIR
                        Path to output directory for caches.

There are four required arguments:

•	-s/--start: the start frame (usually equal to the bifrostContainer’s startFrame)
•	-e/--end: the end frame of your simulation
•	-o/--out_dir: the destination for the output cache files (preferably a local path with plenty of storage)
•	filename: the name of the file to compute

An example command line is:

bifrostBatchSim -s 1001 -e 1150 --output_dir /usr/tmp/bifrost_sims/mySim scenes/mySim.ma

A number of things happen when you launch the script:

•	the destination directory will be created if it doesn’t already exist
•	within this directory, a ‘log’ directory will be created
•	the stdout of the running process will be written to a file in this log directory
•	you can read this file to view the progress of your simulation (hint: use ‘tail -f <filename>’ to watch the output live)

NOTES 

This Python script simply performs a number of checks and runs a mayabatch command with the correct arguments, which is why you have to have bifrostBatchSim.mel in place for this to work.

This script looks for the environment variable MAYA_LOCATION, and will report an error if not found. Make sure this is set properly in your environment prior to running the script.

This script automatically adds an expression to your scene that runs bifrostMemUsage() (see above) every frame, so you don’t need to add it yourself.
