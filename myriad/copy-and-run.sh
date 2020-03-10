cp -R /home/zcabyih/Scratch/orbs $TMPDIR/orbs
chmod 700 $TMPDIR/orbs

python3 $TMPDIR/orbs/slice.py -o if >> /home/zcabyih/Scratch/out.txt
# stdout should go to .o file in output directory

rm -R $TMPDIR/orbs