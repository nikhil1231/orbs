#!/bin/bash -l

# Batch script to run an array job with parameter file

# Request ten minutes of wallclock time (format hours:minutes:seconds).
# needs to be updated depending how long the slice takes
#$ -l h_rt=0:10:0

# Request 1 gigabyte of RAM (must be an integer followed by M, G, or T)
#$ -l mem=1G

# Request 10 gigabyte of TMPDIR space (default is 10 GB)
#$ -l tmpfs=2G
# ^^ $tmpdir (look at documentation)
# remember to chmod 700 so only we can rwx in this dir

# Set up the job array, request tasks 1-n
#$ -t 1-2

# Set the name of the job.
#$ -N mg-orbs

# Set the working directory to somewhere in your scratch space.
#$ -wd /home/zcabyih/Scratch/work-dir


# Parse parameter file to get variables.
number=$SGE_TASK_ID
# SGE_JOB is another unique identifier
paramfile=/home/zcabyih/Scratch/work-dir/params.txt

# number=1
# paramfile=./params.txt


# params structure
# must always have 6 items in a line
# first param = index
# second param = -o
# rest = node orderings
# 6th (optionally) = --slice-all-nodes
# empty ordering elements can be substituted with _
index="`sed -n ${number}p $paramfile | awk '{print $1}'`"
variable1="`sed -n ${number}p $paramfile | awk '{print $2}'`"
variable2="`sed -n ${number}p $paramfile | awk '{print $3}'`"
variable3="`sed -n ${number}p $paramfile | awk '{print $4}'`"
variable4="`sed -n ${number}p $paramfile | awk '{print $5}'`"
variable5="`sed -n ${number}p $paramfile | awk '{print $6}'`"
variable6="`sed -n ${number}p $paramfile | awk '{print $7}'`"

echo "$index" "$variable1" "$variable2" "$variable3" "$variable4" "$variable5" "$variable6"
# Run the program (replace echo with your binary and options).

# execute script:
# # copy repo to scratch dir
rm -R /home/zcabyih/Scratch/work-dir_"$SGE_JOB_ID"_"$SGE_TASK_ID"_timestamp
mkdir /home/zcabyih/Scratch/work-dir
cp -R /home/zcabyih/orbs /home/zcabyih/Scratch/work-dir

# python3 ./myriad/myriad-slice.py "$variable1" "$variable2" "$variable3" "$variable4" "$variable5" "$variable6" >> ~/Scratch/out.txt
python3 /home/zcabyih/Scratch/work-dir/myriad/myriad-slice.py "$variable1" "$variable2" "$variable3" "$variable4" "$variable5" "$variable6" >> /home/zcabyih/Scratch/work-dir/out.txt
# stdout should go to .o file in output directory

cp /home/zcabyih/Scratch/work-dir/out.txt /home/zcabyih/orbs/results.txt
# jobs sometimes work in parallel, sometimes work in sequence
# work-dir_id_timestamp

# start with a single job rather than array, then work up to array
# dont have to clean up scratch directory
# clean up home directory eventually
# make a script to extract relevant stuff from a directory and save to local

# find interesting stuff locally and then try it on myriad for consistencys sake