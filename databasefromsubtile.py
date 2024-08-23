from astropy.io import fits
import requests


cat = fits.open('subtilematch.fits')[1].data

subtiles = fits.open('randomsubtiles.fits')[1].data

#structure: Epoch1.continuum, Epoch1.rms, Epoch2.continuum, Epoch2.rms, Epoch3.continuum, Epoch3.rms

filelists = []

def rmsify(url):
    return url[:-10] + 'rms.' + url[-10:]

for row in cat: #its bad code time

    if row['Subtile_2'] in subtiles['Subtile']:

        #first fix URLs for epoch 1 by completely rebuilding the URL since ITS BROKEN
        for ver in range(1,10): #have to loop over versions
            e1 = 'https://archive-new.nrao.edu/vlass/quicklook/VLASS'
            e1 += str(row['Epoch_1']) + 'v2/'
            e1 += row['Tile_2'] + '/VLASS'
            e1 += str(row['Epoch_1']) + '.ql.'
            e1 += row['Tile_2'] + '.'
            e1 += row['Subtile_2'] + '.10.2048.v'
            e1 += str(ver) + '/VLASS'
            e1 += str(row['Epoch_1']) + '.ql.'
            e1 += row['Tile_2'] + '.'
            e1 += row['Subtile_2'] + '.10.2048.v'
            e1 += str(ver) + '.I.iter1.image.pbcor.tt0.'
            e1 += 'subim.fits'
            if requests.head(e1).status_code == 200: #aka if the file exists, ie we've found the right version
                break


        for ver in range(1,10): #have to loop over versions
            e2 = 'https://archive-new.nrao.edu/vlass/quicklook/VLASS'
            e2 += str(row['Epoch_2']) + '/'
            e2 += row['Tile_2'] + '/VLASS'
            e2 += str(row['Epoch_2']) + '.ql.'
            e2 += row['Tile_2'] + '.'
            e2 += row['Subtile_2'] + '.10.2048.v'
            e2 += str(ver) + '/VLASS'
            e2 += str(row['Epoch_2']) + '.ql.'
            e2 += row['Tile_2'] + '.'
            e2 += row['Subtile_2'] + '.10.2048.v'
            e2 += str(ver) + '.I.iter1.image.pbcor.tt0.'
            e2 += 'subim.fits'
            if requests.head(e2).status_code == 200: #aka if the file exists, ie we've found the right version
                break
            

        #construct url for epoch 3
        e3 = 'https://archive-new.nrao.edu/vlass/quicklook/VLASS3.'
        e3 += str(row['Epoch_1'])[-1] + '/'
        e3 += row['Tile_2'] + '/VLASS3.'
        e3 += str(row['Epoch_1'])[-1] + '.ql.'
        e3 += row['Tile_2'] + '.'
        e3 += row['Subtile_1'] + '.10.2048.v1/VLASS3.' #assume epoch 3 images are v1
        e3 += str(row['Epoch_1'])[-1] + '.ql.'
        e3 += row['Tile_2'] + '.'
        e3 += row['Subtile_2'] + '.10.2048.v1.I.iter1.image.pbcor.tt0.'
        e3 += 'subim.fits'

        if requests.head(e3).status_code == 200:
            filelists.append([e1, rmsify(e1), e2, rmsify(e2), e3, rmsify(e3)])

out = ''

for i in filelists:
    for j in i:
        out += (j+',')
    out += ('\n')

print(out)
