#!/usr/bin/env python
from math import *
import numpy as np
import sys
from subprocess import call
from astropy.io import fits
from cphead_astropy import cphead_astropy
import glob
from tqdm import tqdm
import os
home_directory = os.getcwd().split('simct',1)[0]+'simct'
sys.path.append(home_directory+'/code/gal_lens/')
from filenames import bands,survey_func,filenames
survey=survey_func()
c_prefix,t_prefix,t_affix=filenames(survey)

if survey=='CFHTLS':
    fldid,indxno=np.loadtxt('fieldid_sort',dtype={'names': ('fldid','indxno'), 'formats': ('S13', 'S3',)}, usecols=(1,0),unpack=True);
if survey=='VIDEO':
    fldid,indxno=np.loadtxt('fieldid_sort_video',dtype={'names': ('fldid','indxno'), 'formats': ('S13', 'S3',)}, usecols=(1,0),unpack=True);

indxno=np.array([str(indxno[i]).zfill(3) for i in range(len(indxno))])

for ii in tqdm(range(fldid.size)):
    for band in bands(survey):
        filename_list = glob.glob('gout/imoutp_%s_*_%s.fits'%(indxno[ii],band))
        for filename_i in filename_list:
            try:
                cphead_astropy('fitsfiles/'+t_prefix+'_%s_%s'%(band,fldid[ii])+t_affix+'.fits',filename_i,['exptime'])
            except IOError as ex:
                print('ERROR HERE: copyhdr.py')
                print(ex)
                print('fitsfiles/'+t_prefix+'_%s_%s'%(band,fldid[ii])+t_affix+'.fits',filename_i)
                exit()
#        cphead_astropy('fitsfiles/CFHTLS_W_%s_%s_T0007_MEDIAN.fits'%(band,fldid[ii]),'gout/imoutp_%s_*_%s.fits'%(indxno[ii],band),['exptime'])
#	command="cphead fitsfiles/CFHTLS_W_%s_%s_T0007_MEDIAN.fits gout/imoutp_%s_*_%s.fits exptime"%(band,fldid[ii],indxno[ii],band);
#	print command;
#	call(command,shell=1);
