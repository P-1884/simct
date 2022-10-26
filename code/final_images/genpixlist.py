#!/usr/bin/python
from math import *
import numpy as np
import pandas as pd
import sys
#from StringIO import StringIO
from cphead_astropy import cphead_astropy
from sky2pix_astropy import sky2pix_astropy
import glob
from subprocess import call;

## Extract the x,y pixel position for each lens center
## Copy exposure time from the parent tile to each image cutout

gid,gra,gdec,fldid,indxno=np.loadtxt('finalpar_srt.txt',dtype={'names': ('gid','gra', 'gdec','fldid','indxno'), 'formats': ('d', 'f', 'f', 'S13', 'S3',)}, usecols=(0,1,2,3,4),unpack=True);

#PH: If using python3, fldid and indxno are stored in some 'byte' format which adds a 'b' to the beginning of the elements. This checks if the 'b' is there and removes it.
if str(fldid[0])[0]=='b':
    fldid=fldid.astype('str')

if str(indxno[0])[0]=='b':
    indxno=indxno.astype('str')

## Create pxlst files with ra,dec list for each tile separately
## Create rgetpix which will run the sky2xy command for all tiles
## Copies exptime from the parent tile to those cutouts which will be finally added to the same parent tile
arr1=np.lexsort((gid,indxno));
gid=gid[arr1];
gra=gra[arr1];
gdec=gdec[arr1];
fldid=fldid[arr1];
indxno=indxno[arr1];

def savet(a,fmt):
    fmt=fmt.split();
    for i in range(len(a)):
        a[i]=np.char.mod(fmt[i],a[i]);
        np.savetxt("inpgal0",np.transpose(a),fmt="%s");

savet([gid,gra,gdec,fldid,indxno],'%d %f %f %s %s');
band=['u','g','r','i','z'];
#band = ['g'] #PH: NEED TO CHANGE THIS TO ALL BANDS, NOT JUST G
Ntot=len(band);
from tqdm import tqdm
flag=1;
fp1=open('rgetpix','w');
#fp2=open('rchd1','w');

import os
os.chdir('/Users/hollowayp/simct/code/final_images/imdir')
call("rm pxlst*",shell=1) #need to remove any previously made as otherwise the loop 'for filename_i_0 in filename_list_0' below is dependent on how many files there are originally.
os.chdir('/Users/hollowayp/simct/code/final_images')
run_sky2pix = []
indx_for_running_sky2pix = []
for ii in tqdm(range(gra.size)):
    if(flag==1):
        fp=open('imdir/pxlst%s'%(indxno[ii]),'w');
        indx_for_running_sky2pix.append(ii)
#        fp1.write("sky2xy fitsfiles/CFHTLS_W_g_%s_T0007_MEDIAN.fits @imdir/pxlst%s | awk '{print $5,$6}' >> fpxlst\n"%(fldid[ii],indxno[ii]));#TEMPORARILY REPLACING
        for kk in range(Ntot):
            filename_list = glob.glob('gout/imoutp_%s_*_%s.fits'%(indxno[ii],band[kk]))
            for filename_i in filename_list:
                try:
                    cphead_astropy('fitsfiles/CFHTLS_W_%s_%s_T0007_MEDIAN.fits'%(band[kk],fldid[ii]),filename_i,['exptime'])
                except OSError as ex:
                    print('ERROR HERE: genpixlist.py:',ex)
#                    print('fitsfiles/CFHTLS_W_%s_%s_T0007_MEDIAN.fits'%(band[kk],fldid[ii]),filename_i,['exptime'])
                    continue
                except Exception as ex:
                    print('ERROR HERE, in genpixlist.py',ex)
#                    print(filename_i)
                    continue
        flag=0
    fp.write("%f %f \n"%(gra[ii],gdec[ii]));
    if(ii==(gra.size-1) or indxno[ii]!=indxno[ii+1]):
        fp.close();
        flag=1;

fp1.close();
#fp2.close();

call("rm fpxlst",shell=1) #removing so doesn't just add to original file, but makes a new one afresh.
#PH: Adding in fp3 to write the pixel coordinates:
fp3=open('fpxlst','w');

#Now running the sky2pix code:
counts=0
stop=0
for ii in indx_for_running_sky2pix:
    filename_i_0 = 'imdir/pxlst%s'%(indxno[ii])
    coord_table = pd.read_csv(filename_i_0,header=None,sep=' ',names = ['ra','dec','nan'])
    ra_list,dec_list = coord_table['ra'],coord_table['dec']
    for p in (range(len(ra_list))):
        if stop==1:
            break
        try:
#            print(fldid[ii],ra_list[p],dec_list[p])
            x_i,y_i = sky2pix_astropy('fitsfiles/CFHTLS_W_g_%s_T0007_MEDIAN.fits'%(fldid[ii]),ra_list[p],dec_list[p])
#            stop=1
        except:
            x_i,y_i=-99.0,-99.0 #Adding this in for all the CFHTLS files I don't have
        fp3.write(str(x_i)+' '+str(y_i)+' \n');
        counts+=1

fp3.close()
#To ensure fpxlst and inpgal0 are the same length (they are concatenated to make inpgal.txt), need counts (i.e. len(fpxlst))==len(gra) (i.e len(inpgal.txt)
assert counts==len(gra)
