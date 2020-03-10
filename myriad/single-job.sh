#!/bin/bash -l

# Batch script to run a serial job under SGE.

# Request ten minutes of wallclock time (format hours:minutes:seconds).
#$ -l h_rt=0:10:0

# Request 1 gigabyte of RAM (must be an integer followed by M, G, or T)
#$ -l mem=1G

# Request 10 gigabyte of TMPDIR space (default is 10 GB)
#$ -l tmpfs=10G

# Set the name of the job.
#$ -N Serial_Job

# Set the working directory to somewhere in your scratch space.  
#  This is a necessary step as compute nodes cannot write to $HOME.
#$ -wd /home/zcabyih/Scratch/workspace

# Your work should be done in $TMPDIR 
cd $TMPDIR

# Run the application and put the output into a file called date.txt
# /bin/date > date.txt
/home/zcabyih/Scratch/orbs/myriad/copy-and-run.sh

# Preferably, tar-up (archive) all output files onto the shared scratch area
tar -zcvf /home/zcabyih/Scratch/files_from_job_$JOB_ID.tar.gz $TMPDIR

# Make sure you have given enough time for the copy to complete!