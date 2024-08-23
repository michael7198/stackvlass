#!/usr/bin/env python3

# ~~~VARIABLES~~~

# Final Convolution FWHM (arcsec)
convwidth = 5.4
# Weight Images?
weight = True


import numpy as np
from astropy.io import fits
from reproject.mosaicking import reproject_and_coadd, find_optimal_celestial_wcs
from reproject import reproject_exact
from glob import glob
from astropy.wcs import WCS
from scipy.ndimage import gaussian_filter
import bdsf
import os

#find files
files = glob('./VLASS*tt0.subim.fits')
rms = glob('./VLASS*tt0.rms.subim.fits')


#get tile and subtile
spl = files[0].split('/')[-1].split('.')
tile = spl[3]; coords = spl[4]

#make subtile output folder
os.mkdir(coords)

#preprocessing for reproject
hdus = [fits.open(i)[0] for i in files]
rmss = [fits.open(i)[0] for i in rms]
rescale = [(convwidth/3600)**2 / (i.header['BMAJ']*i.header['BMIN']) for i in hdus]

tuples = [(i.data[0][0]*j, WCS(i).dropaxis(3).dropaxis(2)) for i,j in zip(hdus, rescale)]
weights = [1/i.data[0][0] for i in rmss]
wcs_out, shape_out = find_optimal_celestial_wcs(tuples)

#do the reprojecting: output_array is necessary to stay 32 bit
if weight == True:
    array, footprint = reproject_and_coadd(tuples, wcs_out, shape_out=shape_out, reproject_function=reproject_exact, input_weights=weights, output_array = np.zeros(shape=shape_out, dtype=np.float32))
else:
    array, footprint = reproject_and_coadd(tuples, wcs_out, shape_out=shape_out, reproject_function=reproject_exact, output_array = np.zeros(shape=shape_out, dtype=np.float32))

#blur to circular gaussian beam
weightconv = gaussian_filter(array, sigma=convwidth/2.35, mode='constant')

#create output fits with appropriate header information
head = wcs_out.to_header()
contfiles = [i.split('/')[-1].strip() for i in files]
rmsfiles = [i.split('/')[-1].strip() for i in rms]
head.add_comment("Created using reproject v0.13.1")
head.add_history("File constructed from these continuum images:")
for i in contfiles:
    head.add_history(i)
head.add_history("And these rms images:")
for i in rmsfiles:
    head.add_history(i)
head.append(("BMAJ", convwidth/3600, "[deg]"))
head.append(("BMIN", convwidth/3600, "[deg]"))
head.append(("BPA", 0, "[deg]"))
head.append(("RESTFRQ", 3e9, "[Hz]"))
head.append(("BUNIT", 'Jy/beam', 'Brightness (pixel) unit'))
hdu = fits.PrimaryHDU(weightconv, header = head)

#write output file
#VLASS.qlstack.[$TILE].[$COORDS].10.2048.v[$VERSION].I.iter1.image.pbcor.tt0.subim.fits
outname = 'VLASS.qlstack.'
outname += str(tile) + '.' + coords
outname += '.10.2048.v1.I.iter1'

#save file
hdu.writeto(outname + '.image.pbcor.tt0.subim.fits')


#run pybdsf
proc = bdsf.process_image(outname + '.image.pbcor.tt0.subim.fits', rms_box=(200,50), frequency=3e9)
proc.write_catalog(outfile=outname+'.catalog.fits', format='fits', incl_empty=True, catalog_type='srl')
proc.export_image(outfile=outname+'.image.pbcor.tt0.rms.subim.fits', img_type='rms')

#process individual images
for i in files:
    im = bdsf.process_image(i, rms_box=(200,50), frequency=3e9)
    im.write_catalog(outfile=i[:-10]+'catalog.fits', format='fits', incl_empty=True, catalog_type='srl')
