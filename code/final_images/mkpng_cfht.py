#!/usr/bin/env python
import numpy as np
from math import *;
from subprocess import call;
import sys
from glob import glob;
import multiprocessing
import time
import os
home_directory = os.getcwd().split('simct',1)[0]+'simct'
sys.path.append(home_directory+'/code/gal_lens')
from filenames import filenames,survey_func,png_colours
survey=survey_func()
png_colours=png_colours(survey)
print(png_colours)
## Creates final color PNG images of the real survey images combined with the
## simulated lensed images

## Needs compose.py from HumVI package
#call("rm outfits1/*png",shell=1);

def worker(num,Nproc):
    if survey=='CFHTLS':
        fname=glob("outfits1/CFHTLS_*_g.fits");
    if survey=='VIDEO':
        fname=glob("outfits1/VIDEO_*_k_v.fits");
    iimin=np.int(len(fname)*num/Nproc);
    iimax=np.int(len(fname)*(num+1)/Nproc);
    if(num==Nproc-1):
        iimax=len(fname);
    for ii in range(iimin,iimax):#REMOVED TEMPORARILY
#    for ii in range(iimin,iimin+2):
        fil=fname[ii];
        if survey=='CFHTLS':
            subst=fil[0:len(fil)-7];
        if survey=='VIDEO':
            subst=fil[0:len(fil)-9];#Have to change this so it gets the filenames its looking for correct (the cfhtls one has a longer name than VIDEO)
        print(subst)
#        print("python2 ./compose2.py -s 0.4,0.6,1.7 -z 0.0 -p 1.0,0.09 -m -1.0  -o %s_o_gri.png %s_i.fits %s_r.fits %s_g.fits"%(subst,subst,subst,subst))
        command='python2 '+home_directory+'/code/final_images/HumVI/HumVI.py -s 0.4,0.6,1.7 -z 0.0 -p 1.0,0.09 -m -1.0  -o %s_o_gri.png %s_%s.fits %s_%s.fits %s_%s.fits'%(subst,subst,png_colours[2],subst,png_colours[1],subst,png_colours[0]);
        call(command,shell=1);


jobs=[];
## Adjust Nproc according to no. of processors on your machine
Nproc=4;
for i in range(Nproc):
    print('starting jobs')
    p = multiprocessing.Process(target=worker,args=(i,Nproc))
    jobs.append(p);
    p.start();

