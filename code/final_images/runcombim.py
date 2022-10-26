#!/usr/bin/env python
from math import *
import numpy as np
import sys
from StringIO import StringIO
from subprocess import call
import multiprocessing
import time
import glob
import os;
from astropy.io import fits
import pandas as pd
from fimgmerge_astropy import fimgmerge_astropy
print "Deleting blanksims/*fits outfits/*fits outfits1/*fits imdir/LOG*.dat PH TEMPORARILY REMOVING";
sys.stdout.flush();
'''call("rm ../blanksims/CF*fits",shell=1);
call("rm ../outfits/CF*fits",shell=1); 
call("rm ../outfits1/CF*fits",shell=1); 
call("rm LOG*.dat",shell=1); '''
from tqdm import tqdm
#NEEDT TO BE IN IMDIR DIRECTORY TO RUN THIS CODE:
os.chdir('/Users/hollowayp/simct/code/final_images/imdir')
def worker(num,nproc):
    files=glob.glob("rmgcpy_*") #e.g. cp dirfitsname/CFHTLS_079_1608_u.fits ../outfits/CFHTLS_079_1608_u_t.fits
    files1=glob.glob("rmrg_*") #e.g. fimgmerge ../outfits/CFHTLS_095_1278_u_t.fits  @lstfile_095_1278_u ../outfits1/CFHTLS_095_1278_u.fits
    files2=glob.glob("rmrgb_*") #e.g. fimgmerge blnkcutout.fits  @lstfile_079_1608_g ../blanksims/CFHTLS_079_1608_g.fits
    files3=glob.glob("rimst_*") #e.g. ./getimstat.py ../outfits1/CFHTLS_093_0157_u.fits
    iimin=np.int(len(files)*num/nproc);
    iimax=np.int(len(files)*(num+1)/nproc);
    if(num==nproc-1):
        iimax=len(files);
    for ii in range(iimin,iimax):
        print "Running copy %s"%(files[ii]);
        sys.stdout.flush();
        call("./%s 2>&1"%(files[ii]),shell=1); #The 2>&1 means it redirects the 'standard error' (by default denoted by 2) to a file called 1. Think this redirection is probably neglectable.
    fid,gid=np.loadtxt("/Users/hollowayp/simct/code/final_images/imdir/idpxlst",dtype={'names':('fid','gid'),'formats':('S8','d')},usecols=([0,1]),unpack=1);
    done=False;
    cntloop=0;
    while(not done):
#        time.sleep(3);
        done=True;
        for ii in (range(fid.size)):
            for col in ['u','g','r','i','z']:
#                if col=='g' and fid[ii]=='078_2491':
#                    print('here!')
                ff="../outfits/CFHTLS_%s_%s_t.fits"%(fid[ii],col);
                if(not os.path.isfile(ff)):
                    if(cntloop%1000==0):
                        pass
#                        print "File",ff," does not exist"
                    done=False;
#                else:
#                    print('FILE FOUND!')
        cntloop=cntloop+1;
        if(cntloop>1000):
            print "Some files missing in outfits1, PH: moving on temporarily anyway";
            done=True
#            exit(0);
    for ii in range(iimin,iimax):
#        print "Running merge %s"%(files[ii]);
        sys.stdout.flush();
#        call("./%s > LOG.%s.dat 2>&1 "%(files1[ii],files1[ii]),shell=1);
        file_i =open('/Users/hollowayp/simct/code/final_images/imdir/'+files1[ii])
        #file_i = open('/Users/hollowayp/simct/code/final_images/imdir/rmrg_082')
        for line in file_i:
            if line[0:4]=='fimg':
                line_i = line.split()
                input_file_i = line_i[1];superimposed_images_file_i = line_i[2];output_file_i = line_i[3]
                superimposed_images_file_i=superimposed_images_file_i.replace('@','')
                if input_file_i=='../outfits/CFHTLS_073_0904_g_t.fits':
                    print('HERE',input_file_i,superimposed_images_file_i,output_file_i)
                fimgmerge_astropy(input_file_i,superimposed_images_file_i,output_file_i)
                print('done')
    for ii in range(iimin,iimax):
#        print "Running mergeblank%s"%(files[ii]);
        sys.stdout.flush();
        call("./%s > LOG.%s.dat 2>&1"%(files2[ii],files2[ii]),shell=1);
    for ii in range(iimin,iimax):
        print "Running imstat %s"%(files[ii]);
        sys.stdout.flush();
        call("./%s > LOG.%s.dat 2>&1"%(files3[ii],files3[ii]),shell=1);

jobs=[];
Nproc=4;
for i in range(Nproc):
    p = multiprocessing.Process(target=worker,args=(i,Nproc))
    jobs.append(p);
    p.start();


#fimgmerge_astropy('../outfits/CFHTLS_078_2051_g_t.fits',superimposed_images_file_i,'testfile_can_be_deleted')

#Checking if anything has been added to the files:
import glob
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as pl
from tqdm import tqdm
from matplotlib import colors
f_names_1 = glob.glob('/Users/hollowayp/simct/code/final_images/outfits1/*')
f_names_0 = glob.glob('/Users/hollowayp/simct/code/final_images/outfits1/*') #i.e. identical to previous line
f_names_0 = [f_names_0[i].replace('.fits','_t.fits') for i in range(len(f_names_0))]
f_names_0 = [f_names_0[i].replace('outfits1','outfits') for i in range(len(f_names_0))]
#summing to 0 means they are identical (which is not what's supposed to happen):
print('starting test')
n=0
for i in tqdm(range(len(f_names_0))):
    a = fits.open(f_names_0[i])[0].data
    b = fits.open(f_names_1[i])[0].data
    if np.sum(a-b)!=0:
        print(f_names_0[i],np.sum(a-b))
        fig,ax = pl.subplots(1,3,figsize = (15,5))
        ax[0].imshow(a,origin='lower',norm=colors.LogNorm())
        ax[1].imshow(b,origin='lower',norm=colors.LogNorm())
        ax[2].imshow(a-b,origin='lower')
        pl.show()
        n+=1
    if n>=10:
        break
