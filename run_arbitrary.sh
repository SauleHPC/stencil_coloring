#!/bin/bash

#SBATCH --partition=Orion
#SBATCH --job-name=2dstencil_ilpcoloring
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=36
#SBATCH --mem=350GB
#SBATCH --time=24:00:00

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


python3 stencil.py $SIZEX $SIZEY $TYPE

