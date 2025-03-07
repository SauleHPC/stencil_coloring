#!/bin/bash

#SBATCH --partition=Orion
#SBATCH --job-name=2dstencil_ilpcoloring_cyclic
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --mem=550GB
#SBATCH --time=48:00:00

usage() {
    echo "Usage: sbatch --export=SIZEX='3',SIZEY='3',TYPE='9pt_box'  run_arbitrary.sh"
}

if [ "$SIZEX" = "" ]; then
    usage
    exit
fi

if [ "$SIZEY" = "" ]; then
    usage
    exit
fi

if [ "$TYPE" = "" ]; then
    usage
    exit
fi


python3 -u stencil.py $SIZEX $SIZEY $TYPE $XCYCLIC $YCYCLIC

