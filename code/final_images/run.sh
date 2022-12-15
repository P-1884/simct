#!/bin/bash
 
function partone() {
    fil1=$1
    dirfitsname=$2
    cp $fil1 ./finalpar.txt
    ##############################
    echo $1
    sort -k5 finalpar.txt > finalpar_srt.txt
    echo genpixlist.py
    python2 ./genpixlist.py #requires finalpar_srt, makes: inpgal0,fpxlst,rgetpix,imdir/pxlst. fpxlst is the x,y position within the main tile, not within the cutout.
#    sh rgetpix #PH: have removed this as generating the pixel coordinates is now done in genpixlist.py.
    paste inpgal0 fpxlst > inpgal.txt #inpgal.txt contains: number (not sure what) | ra | dec | tile name (e.g. 085011-051100) | tile indx (e.g. 073) | pixel val 1 | pixel val 2 corresponding to that ra/dec
    #Next command takes values in inpgal.txt and then copies them into pximtag, with some adjustments (see 50*int... function) for the last one.
    awk '{printf(" %s %f %f %s %s %f %f %04d \n",$1,$2,$3,$4,$5,$6,$7,50*int(($6-1)/386)+int(($7-1)/386)+1)}' inpgal.txt > pximtag
    #Writes output to logcomb:
    echo gencombim2
    #NEED TO KEEP WHOLE PATH ON NEXT LINE (ARGUMENT BEFORE inpgal.txt)
    python2 ./gencombim2.py /Users/hollowayp/simct/code/final_images/Final_Output/ inpgal.txt > logcomb #creates lstfile
#    python2 ./gencombim2.py $dirfitsname inpgal.txt > logcomb #PH Oct 2022: needed to make an empty file called 'gg'
    #NOTE adding in running rcpyall here, as doesn't seem to be called anywhere?
    #NEED TO BE IN IMDIR WHEN RUN THIS:
    cd ./imdir
    ./rcpyall
    cd ..
    ## Run the following two commands either here or right at the beginning
    ## Copy exptime from the parent tiles to their respective sim images 
    # sh rchd1 #PH: Have removed this as this copying of the header is now done within genpixlist.py. Previously, the commands were written within genpixlist.py and then executed with this 'sh rchd1' line, but now they are executed within genpixlist.py
    ## Add poisson noise to the simulated arc pixels (gout/imoutp*) before merging with the real data in the parent tile
#    python2 ./runpoi.py > poiout
    
    ### Check if files look alright 
    echo "imdir/idpxlst"
    awk '{print $2}' imdir/idpxlst | sort -u | wc -l
    echo "finalpar.txt"
    awk '{print $1}' finalpar.txt | sort -u | wc -l
    echo "inpgal.txt"
    awk '{print $1}' inpgal.txt | sort -u | wc -l
    wc -l logcomb

    echo runcombim.py
    python2 ./runcombim.py
    
    ### Check if files look alright 
    echo "imdir/idpxlst"
    awk '{print $1}' imdir/idpxlst | sort -u | wc -l
    echo "blanksims/*_i.fits ", `ls -l blanksims/*_i.fits | wc -l`
    echo "outfits1/*_i.fits ", `ls -l outfits1/*_i.fits | wc -l`
}

function parttwo(){
    outdirname=$1
    mkdir $outdirname
    python2 ./mkpng_blnk.py
    python2 ./mkpng_cfht.py
    python2 ./mkpng_mask.py
    ./mkpng_crsh.py $outdirname/png
    echo "blanksims/*png ",`ls -l blanksims/*png | wc -l`
    echo "outfits1/*_o_gri.png ",`ls -l outfits1/*_o_gri.png | wc -l`
    echo $outdirname"/png/*png ",`ls -l $outdirname/png/*png | wc -l`
}

function partthree(){
    outdirname=$1
    rm -r $outdirname/blanksims $outdirname/outfits1
    cp finalpar.txt inpgal.txt imdir/idpxlst $outdirname/ 
    cp -r outfits1 $outdirname/
    cp -r blanksims $outdirname/
    ls -l $outdirname/blanksims/*_g.fits | wc -l
    ls -l $outdirname/outfits1/*_g.fits | wc -l
    ls -l $outdirname/outfits1/*_o_gri.png | wc -l
}

#############################################################################
## DIR and FILES NEEDED 
## fitsfiles outfits gout blanksims imdir  outfits1
## finalpar.txt: final lens catalog
## cutoutlist: xmin,xmax,ymin,ymax,cutout_no - pixel values of each contiguous cutout extracted from the parent survey tile
## gout: simulated lens images are stored here
## fitsfiles: the original survey tiles (FITS) are stored here
## outfits: uniform size small cutouts (FITS) of contiguous survey region are stored
## here locally
#############################################################################

###############################
## RUN THIS FOR THE FIRST TIME TO SET UP ALL THE INPUT FILES
###############################

 mkdir fitsfiles outfits gout  blanksims imdir  outfits1

## Create a link to the color composite making code - HumVI/compose.py
 ln -s ./HumVI/humvi/compose.py .

## Create small cutouts of survey from the parent tiles and creates
## the file "cutoutlist"
## NOTE: this is the same dir path that will be provided to partone()
echo mkcutouts.py
#python2 ./mkcutouts.py ./Final_Output 440 386 19354 #see inside mkcutouts.py for what these values mean!


## Create local copies of the simulated images and lens catalogs
## E.g. for galaxy-galaxy lens
cp ../gal_lens/gout/imoutp*fits gout/
cp ../gal_lens/finalpar0.txt ./finalpar.txt #HAVE CHANGED FIRST ONE HERE TO FINALPAR0.TXT TEMPORARILY, FROM finalpar_g.txt (**)
echo finished_copying
## Run the following two commands either here or from within partone() 
## 1. Copy exptime from the parent tiles to their respective sim images
echo copyhdr.py
python2 ./copyhdr.py #This one **might??** to be in python3 otherwise it crashes. But might have been a different bug causing this so might be ok with python2.
## 2. Add poisson noise to the simulated arc pixels (gout/imoutp*) before merging with the real data in the parent tile
echo runpoi.py
#python2 ./runpoi.py > poiout

###############################
## MAIN
###############################
## Input param file and output dir name
fil1=./finalpar.txt
dirfitsname=./Final_Output/
outdirname=galw1
#
### Generates and run scripts which allow you to merge the simulated lensed images with the real
### survey image cutouts (FITS files) using the lensing galaxy position as a reference point     
### NOTE: this is the same dir path that was provided to "mkcutouts.py"
echo partone
partone $fil1 $dirfitsname
#
### Generates final color png images with an alpha layer of mask added to
### indicate the location of the simulated lensed images and compressed using "crush"
### algorithm
parttwo $outdirname
#
### Copying all the generated FITS and PNGs in the output dir. 
### Note: local copies of the output files need to be manually deleted
#partthree $outdirname
#
