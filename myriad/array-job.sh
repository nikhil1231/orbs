#!/bin/bash -l

# Batch script to run an array job with parameter file

# Request ten minutes of wallclock time (format hours:minutes:seconds).
# needs to be updated depending how long the slice takes
#$ -l h_rt=0:10:0

# Request 1 gigabyte of RAM (must be an integer followed by M, G, or T)
#$ -l mem=1G

# Request 10 gigabyte of TMPDIR space (default is 10 GB)
#$ -l tmpfs=10G

# Set up the job array.  In this instance we have requested 4 tasks
# numbered 1 to 4.
#$ -t 1-4

# Set the name of the job.
#$ -N array-params

# Set the working directory to somewhere in your scratch space.
#$ -wd ~/Scratch/work-dir

# copy repo to scratch dir
rm -R ~/Scratch/work-dir
cp -R ~/orbs ~/Scratch/work-dir

# Parse parameter file to get variables.
number=$SGE_TASK_ID
paramfile=~/Scratch/work-dir/params.txt

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

# python3 ./myriad/myriad-slice.py "$variable1" "$variable2" "$variable3" "$variable4" "$variable5" "$variable6" >> ~/Scratch/out.txt
python3 ~/Scratch/work-dir/myriad/myriad-slice.py "$variable1" "$variable2" "$variable3" "$variable4" "$variable5" "$variable6" >> ~/Scratch/work-dir/out.txt

cp ~/Scratch/work-dir/out.txt ~/orbs/results.txt