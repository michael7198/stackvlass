from glob import glob
from astropy.table import Table, vstack
import warnings
import os
warnings.filterwarnings('ignore')

def concatenate(directory):
    #directory: glob-stly command with all the (identical columns) catalogs, eg "files/*catalog.fits" or something
    return vstack([Table.read(i) for i in glob(str(directory))]) 

concatenate('epoch1/*').write('epoch1.fits')
concatenate('epoch2/*').write('epoch2.fits')
concatenate('epoch3/*').write('epoch3.fits')
concatenate('convolved_epoch1/*').write('convolved_epoch1.fits')
concatenate('convolved_epoch2/*').write('convolved_epoch2.fits')
concatenate('convolved_epoch3/*').write('convolved_epoch3.fits')
concatenate('stack/*').write('stack.fits')
