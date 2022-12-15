#!/opt/local/bin/python2.7
from math import *
import numpy as np
import sys
from StringIO import StringIO
from subprocess import call
from fitscopy_astropy import fitscopy_astropy
import os
home_directory = os.getcwd().split('simct',1)[0]+'simct'
survey=survey_func()
sys.path.append(home_directory+'/code/gal_lens')
from filenames import bands,survey_func,filenames
c_prefix,t_prefix,t_affix=filenames(survey)
## Generate a file which upon running will make cutouts of given size and offsets for each tile in the input file
## Also, creates cutoutlist

## width of each cutout
wd=440;

## pixel offset for between neighbouring cutouts
## (since we would like to  have some overlapping region; hence dx!=wd)
dx=386;

## Total number of cutouts is Ntot**2
Ntotpix=19354; #WHAT IS THIS NUMBER?
Ntot=Ntotpix/dx;

if(len(sys.argv)!=5):
    print "./mkcutouts.py dirname width offset ntotpix \n dirname: path of the output\
    directory, width of each cutout in pixels, spatial offset in pixels between\
    neighbouring cutouts, total no. of pixels in a given parent tile";
    sys.exit(0);
else:
    dirname=sys.argv[1]; #had to change the indices here as adding 'python2' to the code line shifted all the other arguments up by one.
    wd=int(sys.argv[2]);
    dx=int(sys.argv[3]);
    Ntotpix=int(sys.argv[4]);

## Read the tile IDs and names
if survey=='CFHTLS':
    indxno,fldid=np.loadtxt('fieldid_sort',dtype={'names':('indxno','fldid'),'formats':('S9','S13')},usecols=(0,1),unpack=True);
if survey=='VIDEO':
    indxno,fldid=np.loadtxt('fieldid_sort_video',dtype={'names':('indxno','fldid'),'formats':('S9','S13')},usecols=(0,1),unpack=True);

band=bands(survey);
Ntotb=len(band);

## A combined executable file for all tiles
fp1=open('imdir/rcoutall','w');
fp1.write('#!/bin/bash \n');

## A catalog which has: "xmin,xmax,ymin,ymax,cutout_no." wrt the parent tile
#THE LENGTH OF THE CUTOUTLIST FILE IS CALCULATED AS FOLLOWS: It is the number of bands (i.e 5) times the length of the fieldid_sort table (=171 here) which is equal to the the number of tiles.
fp2=open('cutoutlist','w');
from tqdm import tqdm
for kk in tqdm(range(fldid.size)):
    ## Executable file for each tile
    fp=open('imdir/rcutout_'+indxno[kk],'w');
    fp.write('#!/bin/bash \n');
    for ii in tqdm(range(Ntot)):
        for jj in range(Ntot):
            for ll in range(Ntotb):
                fp.write('fitscopy.out fitsfiles/'+t_prefix+'_%s_%s'%(band[ll],fldid[kk])+t_affix+'.fits[%d:%d,%d:%d] %s/'%((ii*dx)+1,(ii*dx)+wd,(jj*dx)+1,(jj*dx)+wd,dirname)+c_prefix+'_%s_%04d_%s.fits \n' %(indxno[kk],jj+1+(Ntot*ii),band[ll]));
#                if 'CFHTLS_%s_%04d_%s.fits'%(indxno[kk],jj+1+(Ntot*ii),band[ll])=='CFHTLS_078_2491_g.fits':
#                        print('fitsfiles/CFHTLS_W_%s_%s_T0007_MEDIAN.fits'%(band[ll],fldid[kk]))
                fitscopy_astropy('fitsfiles/'+t_prefix+'_%s_%s'%(band[ll],fldid[kk])+t_affix+'.fits','%s/'%(dirname)+c_prefix+'_%s_%04d_%s.fits'%(indxno[kk],jj+1+(Ntot*ii),band[ll]),(ii*dx)+1,(ii*dx)+wd, (jj*dx)+1,(jj*dx)+wd)
                fp2.write('%d %d %d %d %04d \n'%((ii*dx)+1,(ii*dx)+wd, (jj*dx)+1,(jj*dx)+wd,jj+1+(Ntot*ii)));
    fp.close();
    fp1.write('imdir/rcutout_%s \n'%(indxno[kk]));

fp1.close();
fp2.close();

call("chmod +x imdir/rcutout_* imdir/rcoutall",shell=1);

'''
f=open(home_directory+'/code/final_images/cutoutlist')
i=0
for line in f:
  i+=1
  if i>100:
    break
  print(line)
'''
