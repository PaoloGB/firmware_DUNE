#!/bin/bash

echo "=========================="
CURRENT_DIR=${0%/*}
echo "CURRENT DIRECTORY: " $CURRENT_DIR

echo "============"
echo "SETTING PATHS"
#export PYTHONPATH=$CURRENT_DIR/../../../../Python_Scripts/PyChips_1_5_0_pre2A/src:$PYTHONPATH
#export PYTHONPATH=~/Python_Scripts/PyChips_1_5_0_preexport PYTHONPATH=../../packages:$PYTHONPATH2A/src:$PYTHONPATH
echo "PYTHON PATH= " $PYTHONPATH
export LD_LIBRARY_PATH=/opt/cactus/lib:$LD_LIBRARY_PATH
echo "LD_LIBRARY_PATH= " $LD_LIBRARY_PATH
export PATH=/usr/bin/:/opt/cactus/bin:$PATH
echo "PATH= " $PATH

cd $CURRENT_DIR

echo "============"


#python startEUDETdummy.py $@

