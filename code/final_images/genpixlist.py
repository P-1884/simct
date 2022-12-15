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
import os
home_directory = os.getcwd().split('simct',1)[0]+'simct'
sys.path.append(home_directory+'/code/gal_lens')
from filenames import filenames,bands,survey_func

survey=survey_func()
c_prefix,t_prefix,t_affix=filenames(survey)
## Extract the x,y pixel position for each lens center
## Copy exposure time from the parent tile to each image cutout

gid,gra,gdec,fldid,indxno=np.loadtxt('finalpar_srt.txt',dtype={'names': ('gid','gra', 'gdec','fldid','indxno'), 'formats': ('d', 'f', 'f', 'S13', 'S3',)}, usecols=(0,1,2,3,4),unpack=True);
print(gra,gdec,fldid,indxno)
fldid=fldid.astype('float64') #Have to make the tile-id a float first before I can make it an integer (for some reason?!)
fldid=fldid.astype('int') #Making the tile-id an integer
#PH: If using python3, fldid and indxno are stored in some 'byte' format which adds a 'b' to the beginning of the elements. This checks if the 'b' is there and removes it.
abc=0
try:
    if str(fldid[0])[0]=='b':
        fldid=fldid.astype('str')
        abc=1
    if str(indxno[0])[0]=='b':
        indxno=indxno.astype('str')
except:
    if str(fldid)[0]=='b':
        fldid=fldid.astype('str')
        abc=1
    if str(indxno)[0]=='b':
        indxno=indxno.astype('str')
#fldid=np.array([str(fldid[i]).zfill(3) for i in range(len(fldid))])
indxno=np.array([str(int(float(indxno[i]))).zfill(3) for i in range(len(indxno))]) #Converting to include leading zeros
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
band=bands(survey)
Ntot=len(band);
from tqdm import tqdm
flag=1;
fp1=open('rgetpix','w');
#fp2=open('rchd1','w');

import os
os.chdir(home_directory+'/code/final_images/imdir')
call("rm pxlst*",shell=1) #need to remove any previously made as otherwise the loop 'for filename_i_0 in filename_list_0' below is dependent on how many files there are originally.
os.chdir(home_directory+'/code/final_images')
run_sky2pix = []
indx_for_running_sky2pix = []
print(gra.size,Ntot)
for ii in tqdm(range(gra.size)):
    if(flag==1):
        fp=open('imdir/pxlst%s'%(indxno[ii]),'w');
        indx_for_running_sky2pix.append(ii)
#        fp1.write('sky2xy fitsfiles/'+t_prefix+'_g_%s_'+t_affix+'.fits @imdir/pxlst%s | awk '{print $5,$6}' >> 
#fpxlst\n'%(fldid[ii],indxno[ii]));# TEMPORARILY REPLACING
        for kk in range(Ntot):
            print(indxno[ii],band[kk])
            filename_list = glob.glob('gout/imoutp_%s_*_%s.fits'%(indxno[ii],band[kk]))
            print(filename_list)
            for filename_i in filename_list:
                try:
                    print('fitsfiles/'+t_prefix+'_%s_%s'%(band[kk],fldid[ii])+t_affix+'.fits')
                    cphead_astropy('fitsfiles/'+t_prefix+'_%s_%s'%(band[kk],fldid[ii])+t_affix+'.fits',filename_i,['exptime'])
                except OSError as ex:
                    print('ERROR HERE: genpixlist.py:')
                    print(ex)
                    print(band[kk],fldid[ii])
                    print('fitsfiles/'+t_prefix+'_%s_%s'%(band[kk],fldid[ii])+t_affix+'.fits',filename_i,['exptime'])
                    continue
                except Exception as ex:
                    print(band[kk],fldid[ii])
                    print('ERROR HERE, in genpixlist.py')
                    print(ex)
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
for iii in tqdm(range(len(indx_for_running_sky2pix))):
    ii=indx_for_running_sky2pix[iii]
    filename_i_0 = 'imdir/pxlst%s'%(indxno[ii])
    coord_table = pd.read_csv(filename_i_0,header=None,sep=' ',names = ['ra','dec','nan'])
    ra_list,dec_list = coord_table['ra'],coord_table['dec']
    for p in tqdm(range(len(ra_list))):
        if p>100:
            stop=1
        if stop==1:
            print('NOT PROCESSING ALL OF THE IMAGES HERE, in genpixlist.py')
            break
        try:
            if survey=='CFHTLS':
                x_i,y_i = sky2pix_astropy('fitsfiles/'+t_prefix+'_g_%s'%(fldid[ii])+t_affix+'.fits',ra_list[p],dec_list[p])
            if survey=='VIDEO':
                x_i,y_i = sky2pix_astropy('fitsfiles/'+t_prefix+'_k_v_%s'%(fldid[ii])+t_affix+'.fits',ra_list[p],dec_list[p])
        except Exception as ex:
            print(ex)
            x_i,y_i=-99.0,-99.0 #Adding this in for all the CFHTLS files I don't have
        fp3.write(str(x_i)+' '+str(y_i)+' \n');
        counts+=1

fp3.close()
#To ensure fpxlst and inpgal0 are the same length (they are concatenated to make inpgal.txt), need counts (i.e. len(fpxlst))==len(gra) (i.e len(inpgal.txt)
assert counts==len(gra)
