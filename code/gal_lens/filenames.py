import numpy as np

def filenames(survey):
  if survey=='CFHTLS':
#Cutout:
    c_prefix = 'CFHTLS'  
#Tile:
    t_prefix = 'CFHTLS_W'
    t_affix = '_T0007_MEDIAN'
  if survey=='VIDEO':
    c_prefix = 'VIDEO'
    #original video tile in ./fitsfiles was called xmm1_Ks. Have renamed to VIDEO_T1_k_v.fits
    t_prefix = 'VIDEO_T'
    t_affix = ''
  return c_prefix,t_prefix,t_affix

def bands(survey):
  if survey=='CFHTLS':
    bands = ['u','g','r','i','z']
  if survey=='VIDEO':
    bands= ['k_v']#['i_v','z_v','y_v','j_v','h_v','k_v']
  return bands

def pixel_scale_func(survey):
    if survey=='CFHTLS':
        pixsc=0.186
    #NEED TO ADJUST THIS FOR VIDEO:
    if survey=='VIDEO':
        pixsc=0.34
    return pixsc

def seeing_func(survey):
    if survey=='CFHTLS':
        sig=[0.85,0.78,0.71,0.64,0.68];
    if survey=='VIDEO':
        sig=[0.8,0.8,0.8,0.8,0.8,0.8]
    return np.array(sig)

def survey_func():
  return 'VIDEO'

def png_colours(survey):
    if survey=='CFHTLS':
        png_colours=['g','r','i'];
    if survey=='VIDEO':
        png_colours=['k_v','k_v','k_v']
    return png_colours

#Home directory should be found automatically:
#home_directory = os.getcwd().split('simct',1)[0]+'simct' #=> Looks for the word simct in the current path then treats that as the home directory
#sys.path.append(home_directory+'/code/gal_lens') #=> Then adds this to the path where needed.
