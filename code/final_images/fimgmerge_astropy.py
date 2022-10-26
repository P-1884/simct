from astropy.io import fits
import pandas as pd
import numpy as np

def fimgmerge_astropy(input_file,superimposed_images_file,output_file):
    superimposed_images = pd.read_csv(superimposed_images_file,header=None,names = ['file','y','x'])
    try:
        hdu_list = fits.open(input_file)
        for i in range(len(hdu_list)):
            orig = hdu_list[i].data
            for j in range(len(superimposed_images)):
#Image to be superimposed onto the original:
                sup_img = fits.open(superimposed_images['file'][j])[0].data #assume this data is in the first extension.
                ofx=int(superimposed_images['x'][j])
                ofy=int(superimposed_images['y'][j])
#Temporary array onto which the new image is added, which is cropped/shifted to the correct position/size:
                sup_empty = np.zeros(np.shape(orig))
                max_x = np.min([ofx+np.shape(sup_img)[0],len(sup_empty)])-(ofx+np.shape(sup_img)[0])
                max_y = np.min([ofy+np.shape(sup_img)[1],len(sup_empty)])-(ofy+np.shape(sup_img)[1])
#Adding the cropped/shifted image to the temporary array:
                sup_empty[ofx:ofx+np.shape(sup_img)[0],ofy:ofy+np.shape(sup_img)[1]]+=sup_img[0:np.shape(sup_img)[0]+max_x,0:np.shape(sup_img)[1]+max_y]
                #Adding the temporary array to the original image:
                orig+=sup_empty
            hdu_list[i].data=orig #adding the combined image back into the fits file
        hdu_list.writeto(output_file,overwrite=True)
    except Exception as ex:
        print('Exception in fimgmerge_astropy.py')
        print(ex)
        return None

#fimgmerge_astropy('../outfits/CFHTLS_078_2051_g_t.fits',superimposed_images_file_i,'testfile_can_be_deleted.fits')
