from astropy.convolution import Gaussian2DKernel, convolve
from astropy.io import fits
from filenames import pixel_scale_func,seeing_func,bands
import numpy as np
import os
home_directory = os.getcwd().split('simct',1)[0]+'simct'
pixsc = pixel_scale_func('VIDEO')
sig = seeing_func('VIDEO') #FWHM, arcsec
bands = bands('VIDEO')
#VISTA:
#seeing FWHM is 0.8
#From https://ned.ipac.caltech.edu/level5/Leo/Stats2_3.html,for a gaussian, FWHM = 2.35*sigma. Therefore sigma = FWHM/2.35.
# define normalized 2D gaussian
def gaus2d(x=0, y=0, mx=0, my=0, sx=1, sy=1):
    return 1. / (2. * np.pi * sx * sy) * np.exp(-((x - mx)**2. / (2. * sx**2.) + (y - my)**2. / (2. * sy**2.)))

x = np.linspace(-25, 25)
y = np.linspace(-25, 25)
x, y = np.meshgrid(x, y) # get 2D variables instead of 1D
sigma = sig/2.35 #Converting from FWHM to standard deviation, as above
for i in range(len(bands)):
    z = gaus2d(x,y,sx=sigma[i]/pixsc,sy=sigma[i]/pixsc) #Converting to pixel units
    hdul = fits.HDUList()
    hdul.append(fits.PrimaryHDU(data=z))
#    hdul.append(fits.ImageHDU()
    hdul.writeto(home_directory+'/code/gal_lens/gout/psfcfh_'+bands[i]+'.fits',overwrite=True)
qq
