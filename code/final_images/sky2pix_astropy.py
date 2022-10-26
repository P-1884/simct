from astropy.io import fits
from astropy.wcs.utils import skycoord_to_pixel
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy import wcs
import numpy as np


def sky2pix_astropy(filename,ra,dec):
#    print(filename)
    skycoord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
    WCS = wcs.WCS(fits.open(filename)[0].header)
    x,y = skycoord_to_pixel(skycoord,WCS)
    if np.isnan(x):
      x=-99.0
    if np.isnan(y):
      y=-99.0
    return x,y


    

