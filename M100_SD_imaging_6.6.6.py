#!/usr/bin/env python
import os
import analysisUtils as aU

__rethrow_casa_exceptions=True

# determine grid parameters, gridding and obtaining grid metadata
asdmlist = ['uid___A002_X85c183_X36f',
            'uid___A002_X85c183_X60b',
            'uid___A002_X8602fa_X2ab',
            'uid___A002_X8602fa_X577',
            'uid___A002_X864236_X2d4',
            'uid___A002_X864236_X693',
            'uid___A002_X86fcfa_X664',
            'uid___A002_X86fcfa_X96c',
            'uid___A002_X86fcfa_Xd9']
vislist = map(lambda x: x + '.ms.bl', asdmlist)

spw = 3
imagename = 'M100_TP_CO_cube.spw%s.image'%(spw)
blimagename = imagename + '.bl'
integimagename = imagename + '.integ'
fwhmfactor = 1.13
diameter = 12

xSampling, ySampling, maxsize = aU.getTPSampling(vis='uid___A002_X85c183_X36f.ms', showplot=False)

msmd.open(asdmlist[0]+'.ms.bl')
freq = msmd.meanfreq(spw)
msmd.close()
print("SPW %d: %.3f GHz" % (spw, freq*1e-9))

theorybeam = aU.primaryBeamArcsec(frequency=freq*1e-9,
                                  fwhmfactor=fwhmfactor,
                                  diameter=diameter)

cell = theorybeam/9.0
imsize = int(round(maxsize/cell)*2)

# image the data
sdimaging(infiles=vislist,
    field='M100',
    spw='%s'%(spw),
    nchan=70,
    mode='velocity',
    start='1400km/s',
    width='5km/s',
    veltype='radio',
    outframe='lsrk',
    restfreq='115.271204GHz',
    gridfunction='SF',
    convsupport=6,
    stokes='I',
    phasecenter='J2000 12h22m54.9 +15d49m15',
    ephemsrcname='',
    imsize=imsize,
    cell='%sarcsec'%(cell),
    brightnessunit='Jy/beam',
    overwrite=True,
    outfile=imagename)

imview(imagename)

# subtract a resigual background from the image
imcontsub(imagename=imagename,
    linefile=blimagename,
    contfile='M100.residualbaseline.image',
    fitorder=1,
    chans='0~7;62~69')
os.system('rm -rf M100.residualbaseline.image')

# basic analysis - moments
immoments(imagename=blimagename,
    moments=[0],
    axis='spectral',
    chans='8~61',
    outfile=integimagename)

imview(integimagename)


