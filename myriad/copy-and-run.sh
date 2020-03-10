cp -R /home/zcabyih/orbs $TMPDIR/orbs
chmod 700 $TMPDIR/orbs

python3 $TMPDIR/orbs/myriad/myriad-slice.py "$variable1" "$variable2" "$variable3" "$variable4" "$variable5" "$variable6" >> /home/zcabyih/Scratch/out.txt
# stdout should go to .o file in output directory

rm -R $TMPDIR/orbs