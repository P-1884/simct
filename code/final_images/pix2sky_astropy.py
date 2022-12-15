from astropy.io import fits
from astropy.wcs.utils import pixel_to_skycoord
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy import wcs
import numpy as np

def pix2sky_astropy(filename,x,y):
    try:
        WCS = wcs.WCS(fits.open(filename)[0].header)
        skycoord_val = pixel_to_skycoord(x,y,WCS)
        ra,dec = skycoord_val.ra.value,skycoord_val.dec.value
        return ra,dec
    except Exception as ex:
        print(ex)
