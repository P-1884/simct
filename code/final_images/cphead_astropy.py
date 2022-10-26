from astropy.io import fits

#cutout1 = fits.open('/Users/hollowayp/Downloads/VIDEO_TEST_FILES/test_fits_2.fits')
#orig_im = fits.open('/Users/hollowayp/Downloads/VIDEO_TEST_FILES/xmm1_Ks.fits')

def cphead_astropy(filename_orig,filename_cutout,list_of_properties):
    orig = fits.open(filename_orig)
    cutout = fits.open(filename_cutout)
    for i in range(len(list_of_properties)):
        cutout[0].header[list_of_properties[i]]= orig[0].header[list_of_properties[i]]
    fits.writeto(filename_cutout,cutout[0].data,cutout[0].header,overwrite=True)


