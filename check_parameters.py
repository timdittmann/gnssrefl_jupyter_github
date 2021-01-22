import sys
import os
import subprocess
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
import gnssrefl.gps as g
import gnssrefl.gnssir as guts

#(station, year_list, doy_list, isnr, orb, rate,dec_rate,archive,fortran,nol,overwrite)
def rinex2snr(station, year, doy, isnr=66, orb='nav', rate='low', dec_rate=0, fortran=False,
              nolook=False, archive=None, doy_end=None, year_end=None, overwrite=None):
    ns = len(station)
    if (ns == 4) or (ns == 9):
        station = station
        #print('You have submitted a nominally valid station name')
    else:
        print('Illegal input - Station name must have 4 or 9 characters. Exiting.')
        sys.exit()

    if len(str(year)) != 4:
        print('Year must be four characters long. Exiting.', year)
        sys.exit()

    orbit_list = ['gps', 'gps+glo', 'gnss', 'nav', 'igs', 'igr', 'jax', 'gbm', 'grg', 'wum']
    if orb not in orbit_list:
        print('You picked an orbit type I do not recognize. Here are the ones I allow')
        print(orbit_list)
        print('Exiting')
        sys.exit()

    # if you choose GPS, you get the nav message
    if orb == 'gps':
        orb = 'nav'

    # if you choose GNSS, you get the GFZ sp3 file
    if orb == 'gnss':
        orb = 'gbm'

    # if you choose GPS+GLO, you get the JAXA sp3 file
    if orb == 'gps+glo':
        orb = 'jax'

    if fortran == 'True':
        fortran = True
    else:
        fortran = False

    # check that the fortran exe exist
    if fortran:
        if orb == 'nav':
            snrexe = g.gpsSNR_version()
            if not os.path.isfile(snrexe):
                print('You have selected the fortran and GPS only options.')
                print('However, the fortran translator gpsSNR.e has not been properly installed.')
                print('We are changing to the non-fortran option.')
                fortran = False
        else:
            snrexe = g.gnssSNR_version()
            if not os.path.isfile(snrexe):
                print('You have selected the fortran and GNSS options.')
                print('However, the fortran translator gnssSNR.e has not been properly installed.')
                print('We are changing to the non-fortran option.')
                fortran = False

    if nolook == 'True':
        nol = True
    else:
        nol = False

    if doy_end == None:
        doy2 = doy
    else:
        doy2 = doy_end

    archive_list = ['sopac', 'unavco', 'sonel', 'cddis', 'nz', 'ga', 'bkg', 'jeff', 'ngs', 'nrcan']
    if archive == None:
        archive = 'all'
    else:
        archive = archive.lower()
        if archive not in archive_list:
            print('You picked an archive that does not exist')
            print('For future reference: I allow these archives:')
            print(archive_list)
            print('Exiting')
            sys.exit()

    year1 = year
    if year_end == None:
        year2 = year
    else:
        year2 = year_end

    doy_list = list(range(doy, doy2 + 1))
    year_list = list(range(year1, year2 + 1))

    if overwrite == 'True':
        overwrite = True
    else:
        overwrite = False

    return {'station': station, 'year_list': year_list, 'doy_list': doy_list, 'isnr': isnr, 'orbtype': orb,
            'rate': rate, 'dec_rate': dec_rate, 'archive': archive, 'fortran': fortran, 'nol': nol, 'overwrite': overwrite}


def quicklook(station, year, doy, snr=66, f=1, reqAmp=[7], e1=5, e2=25, h1=0.5, h2=6, sat=None,
              PkNoise=3, fortran=False):
    if len(str(year)) != 4:
        print('Year must have four characters: ', year)
        sys.exit()

    exitS = g.check_inputs(station, year, doy, snr)

    if exitS:
        sys.exit()

    if fortran == 'True':
        fortran = True
    else:
        fortran = False

    # set some reasonable default values for LSP (Reflector Height calculation).
    # most of these can be overriden at the command line
    pele = [5, 30]  # polynomial fit limits
    # peak to noise value is one way of defining that significance (not the only way).
    # For snow and ice, 3.5 or greater, tides can be tricky if the water is rough (and thus
    # you might go below 3 a bit, say 2.5-2.7

    if e1 < 5:
        print('have to change the polynomial limits because you went below 5 degrees')
        print('this restriction is for quickLook only ')
        pele[0] = e1

    return {'station': station, 'year': year, 'doy': doy, 'snr_type': snr, 'f': f, 'reqAmp': reqAmp, 'e1': e1,
            'e2': e2, 'minH': h1, 'maxH': h2, 'PkNoise': PkNoise, 'satsel': sat, 'fortran': fortran, 'pele': pele}


def gnssir(station, year, doy, snr=66, plt=False, fr=None, ampl=None, sat=None, doy_end=None, year_end=None,
           azim1=0, azim2=360, nooverwrite=None, extension='', compress=None, screenstats=True, delTmax=None, e1=None,
           e2=None, mmdd=None):

    year = int(year)
    doy = int(doy)

    if len(str(year)) != 4:
        print('Year must have four characters: ', year)
        sys.exit()

    if doy > 366:
        print('doy cannot be larger than 366: ', year)
        sys.exit()

    lsp = guts.read_json_file(station, extension)
    #print(lsp)

    #print('plt argument', plt)
    if plt is True:
        lsp['plt_screen'] = True
    elif plt is False:
        lsp['plt_screen'] = False

    if delTmax is not None:
        lsp['delTmax'] = delTmax
        #print('Using user defined maximum satellite arc time (minutes) ', lsp['delTmax'])

    # though I would think not many people would do this ...
    if compress is not None:
        if compress == 'True':
            lsp['wantCompression'] = True
        else:
            lsp['wantCompression'] = False

    if screenstats is False:
        #print('no statistics will come to the screen')
        lsp['screenstats'] = False
    else:
        #print('statistics will come to the screen')
        lsp['screenstats'] = True

    # in case you want to analyze multiple days of data
    if doy_end is None:
        doy_end = doy
    else:
        doy_end = int(doy_end)

    # in case you want to analyze multiple years of data
    if year_end is None:
        year_end = year
    else:
        year_end = int(year_end)

    # default will be to overwrite
    if nooverwrite is None:
        lsp['overwriteResults'] = True
        #print('LSP results will be overwritten')
    else:
        lsp['overwriteResults'] = False
        #print('LSP results will not be overwritten')

    if e1 is not None:
        #print('overriding minimum elevation angle: ', e1)
        lsp['e1'] = float(e1)
    if e2 is not None:
        #print('overriding maximum elevation angle: ', e2)
        lsp['e2'] = float(e2)

    # in case you want to look at a restricted azimuth range from the command line
    setA = 0
    if azim1 == 0:
        pass
    else:
        setA = 1

    if azim2 == 360:
        pass
    else:
        setA = setA + 1

    if setA == 2:
        lsp['azval'] = [azim1, azim2]

    # this is for when you want to run the code with just a single frequency, i.e. input at the console
    # rather than using the input restrictions
    if fr is not None:
        lsp['freqs'] = [fr]
        #print('overriding frequency choices')
    if ampl is not None:
        #print('overriding amplitude choices')
        lsp['reqAmp'] = [ampl]

    if sat is not None:
        #print('overriding - only looking at a single satellite')
        lsp['onesat'] = [sat]

    add_mmddhhss = False
    if mmdd == 'True':
        add_mmddhhss = True

    lsp['mmdd'] = add_mmddhhss

    return {'args': {'station': station, 'year': year, 'doy': doy, 'snr_type': snr, 'extension': extension, 'lsp': lsp}, 'doy_end': doy_end, 'year_end': year_end}


def make_json(station, lat, long, height, e1=5, e2=25, h1=0.5, h2=6, nr1=None, nr2=None, peak2noise=2.7,
              allfreq=None, xyz=None, refraction=None):

    NS = len(station)
    if (NS != 4):
        print('station name must be four characters long. Exiting.')
        sys.exit()

    if xyz == 'True':
        xyz = [lat, long, height]
        lat, long, height = g.xyz2llhd(xyz)

    lsp = {}
    lsp['station'] = station
    lsp['lat'] = lat
    lsp['lon'] = long
    lsp['ht'] = height
    lsp['minH'] = h1
    lsp['maxH'] = h2
    lsp['e1'] = e1
    lsp['e2'] = e2

    if nr1 is None:
        nr1 = h1
    if nr2 is None:
        nr2 = h2

    lsp['NReg'] = [nr1, nr2]
    lsp['PkNoise'] = peak2noise

    xdir = os.environ['REFL_CODE']
    outputdir = xdir + '/input'
    if not os.path.isdir(outputdir):
        subprocess.call(['mkdir', outputdir])

    outputfile = outputdir + '/' + station + '.json'

    lsp['polyV'] = 4  # polynomial order for DC removal
    lsp['pele'] = [5, 30]  # elevation angles used for DC removal
    lsp['ediff'] = 2  # degrees
    lsp['desiredP'] = 0.005  # precision of RH in meters
    # azimuth regions in degrees (in pairs)
    # you can of course have more subdivisions here
    lsp['azval'] = [0, 90, 90, 180, 180, 270, 270, 360]

    # frequencies to use - and their required amplitudes. The amplitudes are not set in stone
    # added L5 as default october 13, 2020
    if allfreq is None:
        # choose GPS as the default
        lsp['freqs'] = [1, 20, 5]
        lsp['reqAmp'] = [6, 6, 6]
    else:
        lsp['freqs'] = [1, 20, 5, 101, 102, 201, 205, 206, 207, 208, 302, 306]
        lsp['reqAmp'] = [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
    # use refraction correction
    lsp['refraction'] = True
    if refraction == 'False':
        lsp['refraction'] = False

    # write new RH results  each time you run the code
    lsp['overwriteResults'] = True

    # if snr file does not exist, try to make one
    lsp['seekRinex'] = False

    # compress snr files after analysis - saves disk space
    lsp['wantCompression'] = False

    # periodogram plots come to the screen
    lsp['plt_screen'] = False

    # command line req to only do a single satellite - default is do all satellites
    lsp['onesat'] = None

    # send some information on periodogram RH retrievals to the screen
    lsp['screenstats'] = True

    # save the output plots
    lsp['pltname'] = station + '_lsp.png'

    # how long can the arc be, in minutes
    lsp['delTmax'] = 75  # - this is appropriate for 5-30 degrees

    print('writing out to:', outputfile)
    with open(outputfile, 'w+') as outfile:
        json.dump(lsp, outfile, indent=4)


def daily_avg(station, medfilter, ReqTracks, txtfile=None, plt2screen=True, extension='', year1=2005, year2=2021, fr=0):
    #   make surer environment variables are set
    xdir = os.environ['REFL_CODE']
    year1 = int(year1)
    year2 = int(year2)

    # where the summary files will be written to
    txtdir = xdir + '/Files'

    if not os.path.exists(txtdir):
        print('make an output directory', txtdir)
        os.makedirs(txtdir)

    # outliers limit, defined in meters
    howBig = medfilter;
    k = 0
    # added standard deviation 2020 feb 14, changed n=6
    n = 7
    # now require it as an input
    # you can change this - trying out 80 for now
    # ReqTracks = 80
    # putting the results in a np.array, year, doy, RH, Nvalues, month, day
    tv = np.empty(shape=[0, n])
    obstimes = []
    medRH = []
    meanRH = []
    plt.figure()
    year_list = np.arange(year1, year2 + 1, 1)
    # print('Years to examine: ',year_list)
    print(fr)
    for yr in year_list:
        direc = xdir + '/' + str(yr) + '/results/' + station + '/' + extension + '/'
        if os.path.isdir(direc):
            all_files = os.listdir(direc)
            print('Number of files in ', yr, len(all_files))
            for f in all_files:
                fname = direc + f
                L = len(f)
                # file names have 7 characters in them ...
                if (L == 7):
                    # check that it is a file and not a directory and that it has something/anything in it
                    try:
                        a = np.loadtxt(fname, skiprows=3, comments='%').T
                        numlines = len(a)
                        if (len(a) > 0):
                            y = a[0] + a[1] / 365.25;
                            rh = a[2];
                            doy = int(np.mean(a[1]))
                            frequency = a[10]
                            # change from doy to month and day in datetime
                            d = datetime.date(yr, 1, 1) + datetime.timedelta(doy - 1)
                            medv = np.median(rh)
                            if fr == 0:
                                cc = (rh < (medv + howBig)) & (rh > (medv - howBig))
                            else:
                                cc = (rh < (medv + howBig)) & (rh > (medv - howBig)) & (frequency == fr)
                            good = rh[cc];
                            goodT = y[cc]
                            # only save if there are some minimal number of values
                            if (len(good) > ReqTracks):
                                rh = good
                                obstimes.append(
                                    datetime.datetime(year=yr, month=d.month, day=d.day, hour=12, minute=0,
                                                      second=0))
                                medRH = np.append(medRH, medv)
                                plt.plot(goodT, good, '.')
                                # store the meanRH after the outliers are removed using simple median filter
                                meanRHtoday = np.mean(good)
                                stdRHtoday = np.std(good)
                                meanRH = np.append(meanRH, meanRHtoday)
                                # add month and day just cause some people like that instead of doy
                                # added standard deviation feb14, 2020
                                newl = [yr, doy, meanRHtoday, len(rh), d.month, d.day, stdRHtoday]
                                tv = np.append(tv, [newl], axis=0)
                                k += 1
                            else:
                                print('not enough retrievals on ', yr, d.month, d.day, len(good))
                    except:
                        print('problem reading ', fname, ' so skipping it')
        else:
            abc = 0;  # dummy line
            # print('that directory does not exist - so skipping')
    plt.ylabel('Reflector Height (m)')
    plt.title('GNSS station: ' + station)
    plt.gca().invert_yaxis()
    plt.grid()
    if plt2screen:
        plt.show()
    fig, ax = plt.subplots()
    ax.plot(obstimes, meanRH, '.')
    fig.autofmt_xdate()
    plt.ylabel('Reflector Height (m)')
    today = str(date.today())
    plt.title(station.upper() + ': Daily Mean Reflector Height, Computed ' + today)
    plt.grid()
    plt.gca().invert_yaxis()
    pltname = txtdir + '/' + station + '_RH.png'
    plt.savefig(pltname)
    print('png file saved as: ', pltname)

    # default is to show the plot
    if plt2screen:
        plt.show()

    if txtfile == None:
        print('no output file name has been provided, so no results are written')
    else:
        # sort the time tags
        ii = np.argsort(obstimes)
        # apply time tags to a new variable
        ntv = tv[ii, :]
        N, M = np.shape(ntv)
        outfile = txtdir + '/' + txtfile
        xxx = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print('output file: ', outfile)
        fout = open(outfile, 'w+')
        # change comment value from # to %
        fout.write("{0:28s} \n".format('% calculated on ' + xxx))
        fout.write("% year doy   RH    numval month day RH-sigma\n")
        fout.write("% year doy   (m)                      (m)\n")
        fout.write("% (1)  (2)   (3)    (4)    (5)  (6)   (7)\n")
        for i in np.arange(0, N, 1):
            fout.write(" {0:4.0f}   {1:3.0f} {2:7.3f} {3:3.0f} {4:4.0f} {5:4.0f} {6:7.3f} \n".format(ntv[i, 0],
                                                                                                     ntv[i, 1],
                                                                                                     ntv[i, 2],
                                                                                                     ntv[i, 3],
                                                                                                     ntv[i, 4],
                                                                                                     ntv[i, 5],
                                                                                                     ntv[i, 6]))
        fout.close()