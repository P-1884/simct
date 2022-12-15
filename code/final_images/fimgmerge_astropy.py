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
                max_x = np.min([np.shape(sup_img)[0],len(sup_empty)-ofx])
                max_y = np.min([np.shape(sup_img)[1],len(sup_empty)-ofy])
#Adding the cropped/shifted image to the temporary array:
#                print(ofx,ofx+np.shape(sup_img)[0],ofy,ofy+np.shape(sup_img)[1])
                #Need to add the x_0 and y_0's in case the ofx or ofy are negative, in which case it would otherwise just give a zero-size array along that dimension.
                if ofx<0: x_0=abs(ofx)
                else: x_0 = 0
                if ofy<0: y_0=abs(ofy)
                else: y_0 = 0
                sup_empty[x_0+ofx:ofx+np.shape(sup_img)[0],y_0+ofy:ofy+np.shape(sup_img)[1]]+=sup_img[x_0:max_x,y_0:max_y]
                #Adding the temporary array to the original image:
                orig+=sup_empty
            hdu_list[i].data=orig #adding the combined image back into the fits file
        hdu_list.writeto(output_file,overwrite=True)
    except Exception as ex:
        print(superimposed_images)
        print('Exception in fimgmerge_astropy.py')
        print(ex)
        print('orig',np.shape(orig))
        print('sup_empty',np.shape(sup_empty))
        try:
            print('x: ',ofx,x_0,np.shape(sup_img)[0],max_x)
            print('y: ',ofy,y_0,np.shape(sup_img)[1],max_y)
        except:
            pass
        return None

#fimgmerge_astropy('../outfits/CFHTLS_078_2051_g_t.fits',superimposed_images_file_i,'testfile_can_be_deleted.fits')
#fimgmerge_astropy('../outfits/VIDEO_001_0205_k_v_t.fits', 'lstfile_001_0205_k_v', '../outfits1/VIDEO_001_0205_k_v.fits')
