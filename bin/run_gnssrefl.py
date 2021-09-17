import sys
import os
import subprocess
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
import gnssrefl.gps as g
import gnssrefl.gnssir as guts
import gnssrefl.rinex2snr as r2s
import gnssrefl.quickLook_function as q_func
import wget


def rinex2snr(station, year, doy, snr=66, orb='nav', rate='low', dec_rate=0, fortran=False,
              nolook=False, archive=None, doy_end=None, year_end=None, overwrite=None, translator='hybrid',
              srate=30, mk=False, weekly=False):
    """
        rinex2snr translates RINEX files to an SNR format. This function will fetch orbit files for you.

        Parameters:
        ___________
        station : string
            4 or 9 character ID of the station

        year : integer
            Year

        doy : integer
            Day of year

        snr : integer, optional
            SNR format. This tells the code what elevation angles to save data for. Will be the snr file ending.
            value options:
                66 (default) : saves all data with elevation angles less than 30 degress
                99 : saves all data with elevation angles between 5 and 30 degrees
                88 : saves all data with elevation angles between 5 and 90 degrees
                50 : saves all data with elevation angles less than 10 degrees

        orb : string, optional
            Which orbit files to download.
            value options:
            gps (default) : will use GPS broadcast orbit
            gps+glos : will use JAXA orbits which have GPS and Glonass (usually available in 48 hours)
            gnss : will use GFZ orbits, which is multi-GNSS (available in 3-4 days?)
            nav : GPS broadcast, perfectly adequate for reflectometry.
            igs : IGS precise, GPS only
            igr : IGS rapid, GPS only
            jax : JAXA, GPS + Glonass, within a few days, missing block III GPS satellites
            gbm : GFZ Potsdam, multi-GNSS, not rapid
            grg : French group, GPS, Galileo and Glonass, not rapid
            esa : ESA, multi-GNSS
            gfr : GFZ rapid, GPS, Galileo and Glonass, since May 17 2021
            wum : (disabled) Wuhan, multi-GNSS, not rapid

        rate : string, optional
            The data rate
            value options:
                low (default) : standard rate data
                high : high rate data

        dec_rate : integer, optional
            Decimation rate. 0 is default.

        fortran : boolean, optional
            Whether to use fortran to translate the rinex files. Note: This option requires Fortran RINEX translators.
            Please see documentation at https://github.com/kristinemlarson/gnssrefl to see instructions to get these.
            value options:
                False (default) : does not use fortran to translate rinex
                True : uses fortran to translate rinex

        nolook : boolean, optional
            This parameter tells the code not to get the rinex files online if the files exist locally already.
            default is False.

        archive : string, optional
            Select which archive to get the files from.
            Default is None. None means that the code will search and find an archive with the data for you.
                value options:
                unavco
                sonel (global sea level observing system)
                sopac (Scripps Orbit and Permanent Array Center)
                cddis
                ngs (National Geodetic Survey)
                nrcan (Natural Resources Canada)
                bkg (German Agency for Cartography and Geodesy)
                nz (GNS, New Zealand)
                ga (Geoscience Australia)
                bev (Austria Federal Office of Metrology and Surveying)

        doy_end : int, optional
            end day of year. This is to create a range from doy to doy_end of days to get the snr files.
            If year_end parameter is used - then day_end will end in the day of the year_end.
            Default is None. (meaning only a single day using the doy parameter)

        year_end : int, optional
            end year. This is to create a range from year to year_end to get the snr files for more than one year.
            Default is None.

        overwrite : boolean, optional
            Make a new SNR file even if one already exists (overwrite existing file).
            Default is False.

        translator : string, optional
            hybrid (default) : uses a combination of python and fortran to translate the files.
            fortran : uses fortran to translate (requires the fortran translator executable - see https://github.com/kristinemlarson/gnssrefl)
            python : uses python to translate. (Warning: This can be very slow)

        srate : int, optional
            sample rate for rinex 3 only
            Default is 30.

        mk : boolean, optional
            The Makan option. Use True for uppercase station names.
            Default is False.

        weekly : boolean, optional
            Takes 1 out of every 7 days in the doy-doy_end range (one file per week) - used to save time.
            Default is False.

        """

    #
    ns = len(station)
    if ns == 4 or ns == 9:
        station = station.lower()
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

    if nolook == 'True':
        nol = True
    else:
        nol = False

    if doy_end == None:
        doy2 = doy
    else:
        doy2 = doy_end

    archive_list = ['sopac', 'unavco', 'sonel', 'cddis', 'nz', 'ga', 'bkg', 'jeff', 'ngs', 'nrcan', 'special']
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

    # the weekly option
    skipit = 1
    if weekly is True:
        print('you have invoked the weekly option')
        skipit = 7

    doy_list = [doy, doy2]
    year_list = list(range(year1, year2 + 1))

    if translator == 'fortran':
        fortran = True
    # check that the fortran exe exist
    if fortran:
        if orb == 'nav':
            snrexe = g.gpsSNR_version()
            if not os.path.isfile(snrexe):
                print('You have selected the fortran and GPS only options.')
                print('However, the fortran translator gpsSNR.e has not been properly installed.')
                print('We are changing to the hybrid translator option.')
                fortran = False
        else:
            snrexe = g.gnssSNR_version()
            if not os.path.isfile(snrexe):
                print('You have selected the fortran and GNSS options.')
                print('However, the fortran translator gnssSNR.e has not been properly installed.')
                print('We are changing to the python translator option (the hybrid is not yet working).')
                fortran = False
                translator = 'python'

    # default is to use hybrid for RINEX translator
    if translator == 'hybrid':
        fortran = False  # override
    if translator == 'python':
        fortran = False  # override - but this is sllllllooooowwww

    if type(fortran) is not bool:
        print('please set fortran parameter to boolean True or False')
        sys.exit()

    if mk is True:
        print('you have invoked the Makan option')

    args = {'station': station, 'year_list': year_list, 'doy_list': doy_list, 'isnr': snr, 'orbtype': orb,
            'rate': rate, 'dec_rate': dec_rate, 'archive': archive, 'fortran': fortran, 'nol': nol,
            'overwrite': overwrite, 'translator': translator, 'srate': srate, 'mk': mk, 'skipit': skipit}

    r2s.run_rinex2snr(**args)


def quicklook(station, year, doy, snr=66, f=1, reqAmp=[7], e1=5, e2=25, h1=0.5, h2=6, sat=None,
              PkNoise=3, pltscreen=False):
    """

        Parameters:
        ___________
        station : string
            4 or 9 character ID of the station

        year : integer
            Year

        doy : integer
            Day of year

        snr : integer, optional
            SNR format. This tells the code what elevation angles to save data for. Will be the snr file ending.
            value options:
                66 (default) : saves all data with elevation angles less than 30 degress
                99 : saves all data with elevation angles between 5 and 30 degrees
                88 : saves all data with elevation angles between 5 and 90 degrees
                50 : saves all data with elevation angles less than 10 degrees
        f : integer, optional
            GNSS frequency.
            value options:
                1 (default) : GPS L1
                2 : GPS L2
                20 : GPS L2C
                5 : GPS L5
                101 : GLONASS L1
                102 : GLONASS L2
                201 : GALILEO E1
                205 : GALILEO E5a
                206 : GALILEO E6
                207 : GALILEO E5b
                208 : GALILEO E5
                302 : BEIDOU B1
                306 : BEIDOU B3
                307 : BEIDOU B2

            reqAmp : array_like, optional
                Lomb-Scargle Periodogram (LSP) amplitude significance criterion in volts/volts.
                Default is [7].

            e1 : integer, optional
                elevation angle lower limit in degrees for the LSP.
                default is 5.

            e2: integer, optional
                elevation angle upper limit in degrees for the LSP.
                default is 25.

            h1 : float, optional
                The allowed LSP reflector height lower limit in meters.
                default is 0.5.

            h2 : float, optional
                The allowed LSP reflector height upper limit in meters.
                default is 6.

            sat : array_like, optional
                list of satellites numbers
                default is None.
                array items: integer

            PkNoise : integer, optional
                 peak to noise ratio of the periodogram values (periodogram peak divided by the periodogram noise).
                 default is 3.

            pltscreen : boolean, optional
                Print quicklook plots to screen. False for values only.
                Default is False.
    """

    if len(str(year)) != 4:
        print('Year must have four characters: ', year)
        sys.exit()

    exitS = g.check_inputs(station.lower(), year, doy, snr)

    if exitS:
        sys.exit()

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

    args = {'station': station.lower(), 'year': year, 'doy': doy, 'snr_type': snr, 'f': f, 'reqAmp': reqAmp, 'e1': e1,
            'e2': e2, 'minH': h1, 'maxH': h2, 'PkNoise': PkNoise, 'satsel': sat, 'fortran': None, 'pele': pele,
            'pltscreen': pltscreen}

    values, metrics = q_func.quickLook_function(**args)

    return values, metrics



def gnssir(station, year, doy, snr=66, plt=False, fr=None, ampl=None, sat=None, doy_end=None, year_end=None,
           azim1=0, azim2=360, nooverwrite=True, extension='', compress=False, screenstats=True, delTmax=None, e1=None,
           e2=None, mmdd=False):
    """
        This is the main driver for running GNSS Interferometric Reflectometry.

        parameters:
        ___________
        station : string
            4 or 9 character ID of the station

        year : integer
            Year

        doy : integer
            Day of year

        snr : integer, optional
            SNR format. This tells the code what elevation angles to save data for. Will be the snr file ending.
            value options:
                66 (default) : saves all data with elevation angles less than 30 degress
                99 : saves all data with elevation angles between 5 and 30 degrees
                88 : saves all data with elevation angles between 5 and 90 degrees
                50 : saves all data with elevation angles less than 10 degrees

        plt : boolean, optional
            Send plots to screen or not.
            Default is False.

        fr : integer, optional
            GNSS frequency.
            value options:
                1 (default) : GPS L1
                2 : GPS L2
                20 : GPS L2C
                5 : GPS L5
                101 : GLONASS L1
                102 : GLONASS L2
                201 : GALILEO E1
                205 : GALILEO E5a
                206 : GALILEO E6
                207 : GALILEO E5b
                208 : GALILEO E5
                302 : BEIDOU B1
                306 : BEIDOU B3
                307 : BEIDOU B2

        ampl : float, optional
            minimum spectral peak amplitude.
            default is None

        sat : integer, optional
            satellite number to only look at that single satellite.
            default is None.

        doy_end : int, optional
            end day of year. This is to create a range from doy to doy_end of days.
            If year_end parameter is used - then day_end will end in the day of the year_end.
            Default is None. (meaning only a single day using the doy parameter)

        year_end : int, optional
            end year. This is to create a range from year to year_end to get the snr files for more than one year.
            doy_end will be for year_end.
            Default is None.

        azim1 : integer, optional
            lower limit azimuth.
            If the azimuth angles are changed in the json (using 'azval' key) and not here, then the json overrides these.
            If changed here, then it overrides what you requested in the json.
            default is 0.

        azim2 : integer, optional
            upper limit azimuth.
            If the azimuth angles are changed in the json (using 'azval' key) and not changed here, then the json overrides these.
            If changed here, then it overrides what you requested in the json.
            default is 360.

        nooverwrite : boolean, optional
            Use to overwrite files or not.
            Default is True (overwrite files).

        extension : string, optional
            extension for result file, useful for testing strategies.
            default is ''. (empty string)

        compress : boolean, optional
            xz compress SNR files after use.
            default is False.

        screenstats : boolean, optional
            whether to print stats to the screen or not.
            default is True.

        delTmax : integer, optional
            satellite arc length in minutes.
            default is None.

        e1 : float, optional
            use to override the minimum elevation angle.
            default is None.

        e2 : float, optional
            use to override the maximum elevation angle.
            default is None.

        mmdd : boolean, optional
            adds columns in results for month, day, hour, and minute.
            default is False.

    """

    year = int(year)
    doy = int(doy)

    if len(str(year)) != 4:
        print('Year must have four characters: ', year)
        sys.exit()

    if doy > 366:
        print('doy cannot be larger than 366: ', doy)
        sys.exit()

    lsp = guts.read_json_file(station.lower(), extension)
    #print(lsp)

    #print('plt argument', plt)
    if plt is True:
        lsp['plt_screen'] = True
    else:
        lsp['plt_screen'] = False

    if delTmax is not None:
        lsp['delTmax'] = delTmax
        #print('Using user defined maximum satellite arc time (minutes) ', lsp['delTmax'])

    # though I would think not many people would do this ...
    if compress is True:
        lsp['wantCompression'] = True
    elif compress is False:
        lsp['wantCompression'] = False
    else:
        print('compress must be a boolean: True or False')
        sys.exit()

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
    if nooverwrite is True:
        lsp['overwriteResults'] = True
        #print('LSP results will be overwritten')
    elif nooverwrite is False:
        lsp['overwriteResults'] = False
        #print('LSP results will not be overwritten')
    else:
        print('nooverwrite must be a boolean: True or False')
        sys.exit()

    if e1 is not None:
        #print('overriding minimum elevation angle: ', e1)
        lsp['e1'] = float(e1)
    if e2 is not None:
        #print('overriding maximum elevation angle: ', e2)
        lsp['e2'] = float(e2)

    # in case you want to look at a restricted azimuth range from the command line
    setA = 0
    if azim1 != 0:
        setA += 1

    if azim2 != 360:
        setA += 1

    if setA == 2:
        lsp['azval'] = [azim1, azim2]

    # this is for when you want to run the code with just a single frequency, i.e. input at the console
    # rather than using the input restrictions
    if fr is not None:
        lsp['freqs'] = [fr]
        #print('overriding frequency choices')
    if ampl is not None:
        #print('overriding amplitude choices')
        dumA = ampl
        # this is not elegant - but allows people to set ampl on the command line
        # but use the frequency list from their json ...  which i think has max of 12
        # but use 14 to be sure
        lsp['reqAmp'] = [dumA for i in range(14)]

    if sat is not None:
        #print('overriding - only looking at a single satellite')
        lsp['onesat'] = [sat]

    add_mmddhhss = False
    if mmdd is True:
        add_mmddhhss = True

    lsp['mmdd'] = add_mmddhhss

    xdir = str(os.environ['REFL_CODE'])
    picklefile = 'gpt_1wA.pickle'
    pname = xdir + '/input/' + picklefile

    if os.path.isfile(pname):
        print('refraction file exists')
    else:
        local_copy = 'gnssrefl/' + picklefile
        if os.path.isfile(local_copy):
            print('found local copy of refraction file')
            subprocess.call(['cp', '-f', local_copy, xdir + '/input/'])
        else:
            print('download and move refraction file')
            url = 'https://github.com/kristinemlarson/gnssrefl/raw/master/gnssrefl/gpt_1wA.pickle'
            wget.download(url, picklefile)
            subprocess.call(['mv', '-f', picklefile, xdir + '/input/'])

    args = {'station': station.lower(), 'year': year, 'doy': doy, 'snr_type': snr, 'extension': extension, 'lsp': lsp}

    year_start = year
    year_list = list(range(year_start, year_end + 1))
    for year in year_list:
        if year != year_end:
            doy_en = 366
        else:
            doy_en = doy_end
        if year == year_start:
            doy_list = list(range(doy, doy_en + 1))
        else:
            doy_list = list(range(1, doy_en + 1))

        args['year'] = year
        for doy in doy_list:
            args['doy'] = doy
            guts.gnssir_guts(**args)


def make_json(station, lat, long, height, e1=5, e2=25, h1=0.5, h2=6, nr1=None, nr2=None, peak2noise=2.7, ampl=6.0,
              allfreq=False, l1=False, l2c=False, xyz=False, refraction=None):
    """
        Parameters:
        ___________
        station : string
            4 or 9 character ID of the station.

        lat : float
            latitude in degrees.

        long : float
            longitude in degrees.

        height : float
            ellipsoidal height in meters.

        e1 : integer, optional
            elevation angle lower limit in degrees.
            default is 5.

        e2 : integer, optional
            elevation angle upper limit in degrees.
            default is 25.

        h1 : float, optional
            reflector height lower limit in meters.
            default is 0.5.

        h2 : float, optional
            reflector height upper limit in meters.
            default is 6.

        nr1 : float, optional
            noise region lower limit for QC in meters.
            default is None.

        nr2 : float, optional
            noise region upper limit for QC in meters.
            default is None.

        peak2noise : float, optional
            peak to noise ratio used for QC.
            default is 2.7.

        ampl : float, optional
            spectral peak amplitude for QC.
            default is 6.0

        allfreq : Boolean, optional
            True requests all GNSS frequencies.
            default is False (defaults to use GPS frequencies).

        l1 : boolean, optional
            set to True to use only GPS L1 frequency.
            default is False.

        l2c : boolean, optional
            set to Trye to use only GPS L2C frequency.
            default is False.

        xyz : boolean, optional
            set to True if using Cartesian coordinates.
            default is False.

        refraction : boolean, optional
            set to False to turn off refraction correction.
            default is True.
    """

    NS = len(station)
    if (NS != 4):
        print('station name must be four characters long. Exiting.')
        sys.exit()

    if xyz is True:
        xyz = [lat, long, height]
        lat, long, height = g.xyz2llhd(xyz)

    reqA = ampl

    lsp = {}
    lsp['station'] = station.lower()
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

    if h1 > h2:
        print(f'h1 ({h1}) cannot be greater than h2 ({h2}). Exiting.')
        sys.exit()

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
    if allfreq is False:
        # choose GPS as the default
        lsp['freqs'] = [1, 20, 5]
        lsp['reqAmp'] = [reqA, reqA,reqA]
    elif allfreq is True:
        lsp['freqs'] = [1, 20, 5, 101, 102, 201, 205, 206, 207, 208, 302, 306]
        lsp['reqAmp'] = [reqA,reqA,reqA,reqA,reqA,reqA, reqA,reqA,reqA,reqA,reqA,reqA]

    if l1 is True:
        lsp['freqs'] = [1]
        lsp['reqAmp'] = [reqA]

    if l2c is True:
        lsp['freqs'] = [20]
        lsp['reqAmp'] = [reqA]

    # use refraction correction
    lsp['refraction'] = refraction

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


def daily_avg(station, medfilter, ReqTracks, txtfile=None, plt2screen=True, extension='', year1=2005, year2=2021, fr=0, csv=False):
    """
        Parameters:
        ___________
        station : string
            4 or 9 character ID of the station.

        medfilter : float
            Median filter for daily reflector height (m). Start with 0.25

        ReqTracks : integer
            Required number of tracks.

        txtfile : string, optional
            Use this parameter to set your own output filename.
            default is None.

        plt2screen : boolean, optional
            whether to print plots to screen or not.
            default is True.

        extension : string, optional
            extension for solution names.
            default is ''. (empty string)

        year1 : integer, optional
            restrict to years starting with.
            default is 2005.

        year2 : integer, optional
            restrict to years ending with.
            default is 2021.

        fr : integer, optional
            GNSS frequency.
            default is 0. (all)

        csv : boolean, optional
            Whether you want csv instead of a plain text file.
            default is False (plain text).
    """
    #   make surer environment variables are set
    xdir = os.environ['REFL_CODE']
    year1 = int(year1)
    year2 = int(year2)

    station = station.lower()

    csvformat = csv
    if type(csvformat) is not bool:
        print('csv must be True or false. Setting to default False')
        csvformat = False

    # where the summary files will be written to
    txtdir = xdir + '/Files'

    if not os.path.exists(txtdir):
        print('make an output directory', txtdir)
        os.makedirs(txtdir)

    if csvformat:
        alldatafile = txtdir + '/' + station + '_allRH.csv'
    else:
        alldatafile = txtdir + '/' + station + '_allRH.txt'

    print('all RH will be written to: ', alldatafile)
    allrh = open(alldatafile, 'w+')
    allrh.write(" {0:s}  \n".format('% year,doy, RH(m), Month, day, azimuth(deg),freq, satNu, LSP amp,peak2noise'))

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
    alltimes = []
    plt.figure()
    year_list = np.arange(year1, year2 + 1, 1)
    # print('Years to examine: ',year_list)
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
                            azimuth = a[5]
                            sat = a[3]
                            amplitude = a[6]
                            xd = datetime.date(yr, 1, 1) + datetime.timedelta(doy - 1)
                            # year =[str(int(year[i])) for i in range(N)];
                            # alltimes.append(datetime.datetime(year=a[0], month=d.month, day=d.day, hour=12, minute=0, second=0))
                            peak2noise = a[13]

                            # change from doy to month and day in datetime
                            d = datetime.date(yr, 1, 1) + datetime.timedelta(doy - 1)
                            medv = np.median(rh)
                            if fr == 0:
                                cc = (rh < (medv + howBig)) & (rh > (medv - howBig))
                            else:
                                cc = (rh < (medv + howBig)) & (rh > (medv - howBig)) & (frequency == fr)
                            good = rh[cc];
                            goodT = y[cc]
                            gazim = azimuth[cc];
                            gsat = sat[cc];
                            gamp = amplitude[cc];
                            gpeak2noise = peak2noise[cc]
                            gfreq = frequency[cc]

                            NG = len(good)
                            if (NG > 0):
                                if csvformat:
                                    for ijk in range(0, NG):
                                        allrh.write(
                                            " {0:4.0f},  {1:3.0f},{2:7.3f}, {3:2.0f}, {4:2.0f},{5:6.1f},{6:4.0f},{7:4.0f},{8:6.2f},{9:6.2f}\n".format(
                                                yr,
                                                doy, good[ijk], d.month, d.day, gazim[ijk], gfreq[ijk], gsat[ijk],
                                                gamp[ijk], gpeak2noise[ijk]))
                                else:
                                    for ijk in range(0, NG):
                                        allrh.write(
                                            " {0:4.0f}   {1:3.0f} {2:7.3f} {3:2.0f} {4:2.0f} {5:6.1f} {6:4.0f} {7:4.0f} {8:6.2f} {9:6.2f}\n".format(
                                                yr,
                                                doy, good[ijk], d.month, d.day, gazim[ijk], gfreq[ijk], gsat[ijk],
                                                gamp[ijk], gpeak2noise[ijk]))

                            # only save if there are some minimal number of values
                            if (len(good) > ReqTracks):
                                rh = good
                                obstimes.append(
                                    datetime.datetime(year=yr, month=d.month, day=d.day, hour=12, minute=0,
                                                      second=0))
                                medRH = np.append(medRH, medv)
                                plt.plot(goodT, good, 'b.')
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
    fig, ax = plt.subplots()
    ax.plot(obstimes, meanRH, 'b.')
    fig.autofmt_xdate()

    if plt2screen is True:
        pass
    else:
        plt.close()

    plt.ylabel('Reflector Height (m)')
    today = str(datetime.datetime.today().date())
    plt.title(station.upper() + ': Daily Mean Reflector Height, Computed ' + today)
    plt.grid()
    plt.gca().invert_yaxis()
    pltname = txtdir + '/' + station + '_RH.png'
    plt.savefig(pltname)
    print('Daily average RH png file saved as: ', pltname)

    if plt2screen is True:
        plt.show()
    else:
        plt.close()

    fig, ax = plt.subplots()
    plt.plot(obstimes, tv[:, 3], 'b.')
    fig.autofmt_xdate()
    plt.title('Number of values used in the daily average')
    plt.grid()

    # default is to show the plot
    if plt2screen is True:
        plt.show()
    else:
        plt.close()

    # close the file with all the RH values'
    allrh.close()


    if txtfile is None:
        if csvformat:
            outfile = txtdir + '/' + station + '_dailyRH.csv'
        else:
            # use default  filename for the average
            outfile = txtdir + '/' + station + '_dailyRH.txt'

    else:
        # use filename provided by the user
        outfile = txtdir + '/' + txtfile
    print('Daily average RH will be written to: ', outfile)
    # to avoid indenting again,  use True
    if True:
        # sort the time tags
        ii = np.argsort(obstimes)
        # apply time tags to a new variable
        ntv = tv[ii, :]
        N, M = np.shape(ntv)
        xxx = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        fout = open(outfile, 'w+')
        # change comment value from # to %
        fout.write("{0:28s} \n".format('% calculated on ' + xxx))
        fout.write("% year doy   RH    numval month day RH-sigma\n")
        fout.write("% year doy   (m)                      (m)\n")
        fout.write("% (1)  (2)   (3)    (4)    (5)  (6)   (7)\n")
    if csvformat:
        for i in np.arange(0, N, 1):
            fout.write(" {0:4.0f},  {1:3.0f},{2:7.3f},{3:3.0f},{4:4.0f},{5:4.0f},{6:7.3f} \n".format(ntv[i, 0],
                                                                                                     ntv[i, 1],
                                                                                                     ntv[i, 2],
                                                                                                     ntv[i, 3],
                                                                                                     ntv[i, 4],
                                                                                                     ntv[i, 5],
                                                                                                     ntv[i, 6]))
    else:
        for i in np.arange(0, N, 1):
            fout.write(" {0:4.0f}   {1:3.0f} {2:7.3f} {3:3.0f} {4:4.0f} {5:4.0f} {6:7.3f} \n".format(ntv[i, 0],
                                                                                                     ntv[i, 1],
                                                                                                     ntv[i, 2],
                                                                                                     ntv[i, 3],
                                                                                                     ntv[i, 4],
                                                                                                     ntv[i, 5],
                                                                                                     ntv[i, 6]))
    fout.close()