#!/usr/bin/env python
import os
import math

__rethrow_casa_exceptions=True

datadir = '.'
asdmlist = ['uid___A002_X85c183_X36f',
            'uid___A002_X85c183_X60b',
            'uid___A002_X8602fa_X2ab',
            'uid___A002_X8602fa_X577',
            'uid___A002_X864236_X2d4',
            'uid___A002_X864236_X693',
            'uid___A002_X86fcfa_X664',
            'uid___A002_X86fcfa_X96c',
            'uid___A002_X86fcfa_Xd9']
factors = [[41.52, 42.47, 43.58, 42.98],
           [41.52, 42.47, 43.58, 42.98],
           [41.38, 42.59, 42.08, 42.53],
           [41.38, 42.59, 42.08, 42.53],
           [40.88, 42.48, 41.47, 41.94],
           [40.88, 42.48, 41.47, 41.94],
           [41.71, 42.88, 41.69, 42.18],
           [41.71, 42.88, 41.69, 42.18],
           [41.71, 42.88, 41.69, 42.18]]

# Application of the caltable created by gencal with
# caltype 'amp' appears to multiply x^-2 where x is
# the factor in the caltable. So, desired multiplication
# factor must be converted to its inverse square root
# before creating caltable.
to_amp_factor = lambda x: 1. / math.sqrt(x)

for (asdm,jyperk) in zip(asdmlist,factors):
    os.system('rm -rf %s.*'%(asdm))
    
    vis = asdm+'.ms'
    listfile = vis + '.listobs'
    calvis = vis + '.cal'
    splitvis = calvis + '.split'
    blvis = vis + '.bl'
    nlccaltable = vis + '.nlc'
    jypkcaltable = vis + '.jy'
    
    # importasdm
    importasdm(os.path.join(datadir, asdm), vis=vis, asis='Antenna Station Receiver Source CalAtmosphere CalWVR', bdfflags=True)

    # listobs
    listobs(vis=vis, listfile=listfile)

    # edge channel flagging
    flagdata(vis=vis, mode='manual', spw='17:0~119;3960~4079,19:0~119;3960~4079,21:0~119;3960~4079,23:0~119;3960~4079', action='apply', flagbackup=True)

    # calibration
    sdcal(infile=vis, calmode='ps,tsys,apply', spwmap={9:[17], 11:[19], 13:[21],15:[23]}, spw='17,19,21,23')
    
    # non-linearity correction
    split(vis=vis, outputvis=splitvis, datacolumn='corrected', spw='17,19,21,23')
    
    if os.path.exists(nlccaltable):
        os.system('rm -rf %s'%(nlccaltable))

    gencal(vis=splitvis, caltable=nlccaltable, caltype='amp', spw='', parameter=[to_amp_factor(1.25)])
    applycal(vis=splitvis, gaintable=nlccaltable)

    # baseline subtraction
    sdbaseline(infile=splitvis, datacolumn='corrected', spw='', blfunc='poly', order=1, outfile=blvis, overwrite=True)

    os.system('rm -rf %s'%(splitvis))
    
    # Jy/K factor application
    if os.path.exists(jypkcaltable):
        os.system('rm -rf %s'%(jypkcaltable))

    gencal(vis=blvis, caltable=jypkcaltable, caltype='amp', spw='0,1,2,3', parameter=[to_amp_factor(factor) for factor in jyperk])
    applycal(vis=blvis, gaintable=jypkcaltable)

#Flag out PM02 in two datasets because of instability in bandpasses.
flagdata(vis='uid___A002_X8602fa_X2ab.ms.bl', antenna='PM02&&&')
flagdata(vis='uid___A002_X8602fa_X577.ms.bl',antenna='PM02&&&')
