#!/usr/bin/env python
# reads ra,dec, field name and id
# calculates in which cutout the candidate is located and writes the file for making color png
#===============
        
import numpy as np;
from math import *;
from subprocess import call;
import sys
import pandas as pd
import os
from tqdm import tqdm
home_directory = os.getcwd().split('simct',1)[0]+'simct'
sys.path.append(home_directory+'/code/gal_lens')
from filenames import filenames,bands,survey_func
survey=survey_func()
c_prefix,t_prefix,t_affix=filenames(survey)
if(len(sys.argv)!=3):
        print "./gencombim2.py dirname inpcat";
        sys.exit(0);
else:
#dirname=home_directory+'/code/final_images/Final_Output/'
#inpcat = 'inpgal.txt'
        dirname=sys.argv[1];
        inpcat=sys.argv[2];#had to move these up by one as needed to add 'python2' to the code line.

## Input Catalog
#id, ra, dec, tile, tile_id, pixel position 1, pixel position 2
gid,gra,gdec,fld,fldid,gxpx,gypx=np.loadtxt(inpcat,dtype={'names': ('gid','gra', 'gdec','fld','fldid','gxpx','gypx'), 'formats': ('d', 'f', 'f', 'S13', 'S3','f','f')},unpack=True);
print(gid,gra,gdec,fld,fldid,gxpx,gypx)
fldid=np.array([str(int(float(fldid[i]))).zfill(3) for i in range(len(fldid))]) #Adds in leading zeros where necessary:
print('dirname',dirname)
## List with xmin,xmax,ymin,ymax of the contiguous cutouts made for each survey
## tile
#offsetx,offsety,l1,l3,l4=np.loadtxt("cutoutlist",usecols=(0,2,1,3,4),unpack=True);
cutout_table=pd.DataFrame(np.loadtxt("cutoutlist",usecols=(0,1,2,3,4),unpack=True).T,columns=['offset1','l1','offset2','l3','cutoutn'])
print(cutout_table)
################

band=bands(survey)
Ntot=len(band);

call("rm imdir/lstfile* imdir/rm*_* imdir/rimst_*",shell=1);

def writefiles(dirname,var,var1,fldid,gid,ofstx,ofsty):
        print('Writing:',dirname,var,var1,fldid,gid,ofstx,ofsty)
        for kk in range(Ntot):
#                print('fimgmerge ../outfits/%s_%s_t.fits  @lstfile_%s_%s ../outfits1/%s_%s.fits \n'%(var,band[kk],var1,band[kk],var,band[kk]))
                #Had to change this here as the cutouts weren't put into subfolders?
                print('cp %s/%s_%s.fits ../outfits/%s_%s_t.fits \n'%(dirname,var,band[kk],var,band[kk]))
                fp1.write('cp %s/%s_%s.fits ../outfits/%s_%s_t.fits \n'%(dirname,var,band[kk],var,band[kk]));
#                print("{ printf(\"../gout/imoutp_'%s'_'%d'_'%s'.fits,'%f','%f' \\n \" );}\' gg >> imdir/lstfile_'%s'_'%s'"%(fldid,gid,band[kk],ofstx,ofsty,var1,band[kk]))
#                f_i = "../gout/imoutp_'%s'_'%d'_'%s'.fits"%(fldid,gid,band[kk])
                #Have re-written the awk function below, using open(),close() instead, as the awk function just seemed to make empty files?
                f_i = open("imdir/lstfile_%s_%s"%(var1,band[kk]),'a') #opening file in 'append' mode so text is added to the end of it and not overwritten.
                f_i.write("../gout/imoutp_%s_%d_%s.fits,%f,%f\n"%(fldid,gid,band[kk],ofstx,ofsty))
                f_i.close()
                #This writes name of the file as well as the lensed-image position into a file imdir/lstfile_....
                #Think this function prints a file name and two coordinates (within the {} bit) into an lstfile:
#                call("awk \'{ printf(\"../gout/imoutp_'%s'_'%d'_'%s'.fits,'%f','%f' \\n \" );}\' gg >> imdir/lstfile_'%s'_'%s'"%(fldid,gid,band[kk],ofstx,ofsty,var1,band[kk]),shell=1);
                #This writes a programme to merge this onto a background image
                fp.write('fimgmerge ../outfits/%s_%s_t.fits  @lstfile_%s_%s ../outfits1/%s_%s.fits \n'%(var,band[kk],var1,band[kk],var,band[kk]));
                fp2.write('fimgmerge blnkcutout.fits  @lstfile_%s_%s ../blanksims/%s_%s.fits \n'%(var1,band[kk],var,band[kk]));
                fp3.write('python2 '+ home_directory+'/code/final_images/getimstat.py ../outfits1/%s_%s.fits\n'%(var,band[kk]));


fpw=open('imdir/rmrgall','w');
fpw1=open('imdir/rcpyall','w');
fpw2=open('imdir/rmrgball','w');
fpw3=open('imdir/rimsall','w');
fpw4=open('imdir/idpxlst','w');

fpw.write('#!/bin/bash \n');
fpw1.write('#!/bin/bash \n');
fpw2.write('#!/bin/bash \n');
fpw3.write('#!/bin/bash \n');

flag=1;
for ii in tqdm(range(gid.size)):
        if (gxpx[ii]==-99.0)or(gypx[ii]==-99.0): #i.e. if they are not defined
            continue
        ix=int((gxpx[ii]+0.5)/386.0); #the 386 might be something to do with the cutoutlist file? columns 0 and 2 go up in 386's. Update: The 386 value is from mkcutouts.py, where 386 = 'the pixel offset between neighbouring cutouts, since we would like to  have some overlapping region'. The width of each cutout is 440pixels, also set in mkcutouts.py
        iy=int((gypx[ii]+0.5)/386.0);
        cutoutno=(ix-1)*50+iy; #doesn't seem to be needed anywhere
        modx=(gxpx[ii])%386.+1.;
        mody=(gypx[ii])%386.+1.;
        dgx=(gxpx[ii]-101); #gxpx and gypx are pixel positions wrt the whole tile from ingal.txt. Why subtract 101? The lensed images to be pasted on are 201 pixels in diameter (=> ~101 radius?)
        dgy=(gypx[ii]-101);
        ptx1=-9e5;
        ptx2=-9e5;
        pty1=-9e5;
        pty2=-9e5;
        if (modx>54): #The 54 probably comes from 440 (cutout size) - 386 (offset) = 54
                ptx1=(ix)*50; #where does 50 come from? Perhaps from within run.sh? last entry into pximtag: 50*int(($6-1)/386)+int(($7-1)/386)+1) i.e. {50*int[(pix1-1)/386]}+int[((pix2-1)/386)+1)]. This entry gives the cutout id (e.g. 0904).
                ptx2=-9e5;
    
        if (mody>54):
                pty1=iy+1
                pty2=-9e5;
    
        if (ix>0 and (modx<=54 and modx>=1.) and ix<50):
                ptx1=(ix-1)*50;
                ptx2=ix*50;
    
        if (iy>0 and (mody<=54 and mody>=1.) and iy<50):
                pty1=iy
                pty2=iy+1;
    
        if (ix==50 and (modx<=54 and modx>=1.)):
                ptx1=(ix-1)*50;
                ptx2=-9e5;
    
        if (iy==50 and (mody<=54 and mody>=1.)):
                pty1=iy
                pty2=-9e5;
    
        ctn1=ptx1+pty1; #The ctn (probably stands for cutout number) just gives the cutout value (e.g. 904 for cutout 0904).
        ctn2=ptx1+pty2;
        ctn3=ptx2+pty1;
        ctn4=ptx2+pty2;
        if(flag==1):
                fp=open('imdir/rmrg_%s'%(fldid[ii]),'w');
                fp1=open('imdir/rmgcpy_%s'%(fldid[ii]),'w');
                fp2=open('imdir/rmrgb_%s'%(fldid[ii]),'w');
                fp3=open('imdir/rimst_%s'%(fldid[ii]),'w');
#
                fp.write('#!/bin/bash \n');
                fp1.write('#!/bin/bash \n');
                fp2.write('#!/bin/bash \n');
                fp3.write('#!/bin/bash \n');
#
                fpw.write('./rmrg_%s \n'%(fldid[ii]));
                fpw1.write('./rmgcpy_%s \n'%(fldid[ii]));
                fpw2.write('./rmrgb_%s \n'%(fldid[ii]));
                fpw3.write('./rimst_%s \n'%(fldid[ii]));
#
                flag=0;
#
        if(fldid[ii]==fldid[ii-1] or flag==0):
                print(ctn1,ctn2,ctn3,ctn4)
 #               print "Writing:",ii+1,int(gid[ii]),fldid[ii];
                if(ctn1>0):
                        var=c_prefix+"_%s_%04d"%(fldid[ii],ctn1);
                        var1="%s_%04d"%(fldid[ii],ctn1);
                        try:
                            ofstx=dgx-float(np.array(cutout_table[cutout_table['cutoutn']==ctn1]['offset1'])[0])
                            ofsty=dgy-float(np.array(cutout_table[cutout_table['cutoutn']==ctn1]['offset2'])[0])
                        except Exception as ex:
                            print("Error here, probably because of cutout number (ctn) exceeding the max cutout-number in cutoutlist. Probably caused by not processing all the elements in a previous table.")
                            print(ex)
                            break
#                        ofstx=dgx-offsetx[ctn1-1];
#                        ofsty=dgy-offsety[ctn1-1];
                        #if the ofstx or ofsty are =-200, it is because the inpgal.txt file has -99's in it (i.e. blank entries).
                        print(' %s %d %f %f \n'%(var1,gid[ii],ofstx+102,ofsty+102))
                        fpw4.write(' %s %d %f %f \n'%(var1,gid[ii],ofstx+102,ofsty+102));
                        writefiles(dirname,var,var1,fldid[ii],gid[ii],ofstx,ofsty)#modx-101,mody-101);
        #
                if(ctn2>0):
                        var=c_prefix+"_%s_%04d"%(fldid[ii],ctn2);
                        var1="%s_%04d"%(fldid[ii],ctn2);
#                        ofstx=dgx-offsetx[ctn2-1];
#                        ofsty=dgy-offsety[ctn2-1];
                        ofstx=dgx-float(np.array(cutout_table[cutout_table['cutoutn']==ctn2]['offset1'])[0])
                        ofsty=dgy-float(np.array(cutout_table[cutout_table['cutoutn']==ctn2]['offset2'])[0])
                        fpw4.write(' %s %d %f %f \n'%(var1,gid[ii],ofstx+102,ofsty+102));
                        writefiles(dirname,var,var1,fldid[ii],gid[ii],ofstx,ofsty);
        #
                if(ctn3>0):
                        var=c_prefix+"_%s_%04d"%(fldid[ii],ctn3);
                        var1="%s_%04d"%(fldid[ii],ctn3);
#                        ofstx=dgx-offsetx[ctn3-1];
#                        ofsty=dgy-offsety[ctn3-1];
                        ofstx=dgx-float(np.array(cutout_table[cutout_table['cutoutn']==ctn3]['offset1'])[0])
                        ofsty=dgy-float(np.array(cutout_table[cutout_table['cutoutn']==ctn3]['offset2'])[0])
                        fpw4.write(' %s %d %f %f \n'%(var1,gid[ii],ofstx+102,ofsty+102));
                        writefiles(dirname,var,var1,fldid[ii],gid[ii],ofstx,ofsty);
        #
                if(ctn4>0):
                        var=c_prefix+"_%s_%04d"%(fldid[ii],ctn4);
                        var1="%s_%04d"%(fldid[ii],ctn4);
#                        ofstx=dgx-offsetx[ctn4-1];
#                        ofsty=dgy-offsety[ctn4-1];
                        ofstx=dgx-float(np.array(cutout_table[cutout_table['cutoutn']==ctn4]['offset1'])[0])
                        ofsty=dgy-float(np.array(cutout_table[cutout_table['cutoutn']==ctn4]['offset2'])[0])
                        fpw4.write(' %s %d %f %f \n'%(var1,gid[ii],ofstx+102,ofsty+102));
                        writefiles(dirname,var,var1,fldid[ii],gid[ii],ofstx,ofsty);
                fp.write("echo \"Done: %d %d \" \n"%(ii+1,gid[ii]));
                fp1.write("echo \"Done: %d %d \" \n"%(ii+1,gid[ii]));
                fp2.write("echo \"Done: %d %d \" \n"%(ii+1,gid[ii]));
                fp3.write("echo \"Done: %d %d  \"\n"%(ii+1,gid[ii]));
#
        if (ii==gid.size-1 or fldid[ii]!=fldid[ii+1] ):
                fp.write("echo \"Done:rmrg_%s \" \n"%(fldid[ii]));
                fp1.write("echo \"Done:rmrgcpy_%s \" \n"%(fldid[ii]));
                fp2.write("echo \"Done:rmrgb_%s \" \n"%(fldid[ii]));
                fp3.write("echo \"Done:rimst_%s  \"\n"%(fldid[ii]));
                fp.close();
                fp1.close();
                fp2.close();
                fp3.close();
                flag=1;

fpw.close();
fpw1.close();
fpw2.close();
fpw3.close();
fpw4.close();
call("chmod +x imdir/rmrg_* imdir/rmrgb_* imdir/rmgcpy_* imdir/rimst_* imdir/rmrgall imdir/rcpyall imdir/rmrgball imdir/rimsall",shell=1);
#changing the formatting a bit here as Xcode seems to display the tabs/spaces incorrectly. They are correctly displayed in github so have adjusted it to match this.
