from astropy.io import fits
from astropy import wcs
import numpy as np

def fitscopy_astropy(filename_in,filename_out,index0,index1,index2,index3):
    try:
        hdu_list = fits.open(filename_in)
        w = wcs.WCS(hdu_list[0].header)
        for i in range(len(hdu_list)):
        #Needed to swap the indices around here as otherwise the cutout was made in the wrong place wrt the full tile (i.e. reflected along the diagonal)
            hdu_list[i].data = hdu_list[i].data[index2:index3,index0:index1]
    except:
       return None
    try:
        print(filename_in,filename_out,index0,index1,index2,index3)
        #Again, have swapped the indices round here:
        hdu_list[0].header.update(w[index2:index3,index0:index1].to_header())
        hdu_list.writeto(filename_out,overwrite=True)
    except Exception as ex:
       print('Exception in fitscopy_astropy.py')
       print(ex)
       return None
