import os
import sys
import platform
import shutil
import urllib.request
import tarfile


def check_environment():
    try:
        os.environ['ORBITS']
        os.environ['REFL_CODE']
        os.environ['EXE']

        environment_set = True
    except KeyError:
        environment_set = False

    return environment_set


def set_environment(orbits='../orbits', refl_code='..', exe='../bin/exe'):
    os.environ['ORBITS'] = os.path.abspath(os.path.join(orbits))
    os.environ['REFL_CODE'] = os.path.abspath(os.path.join(refl_code))
    os.environ['EXE'] = os.path.abspath(os.path.join(exe))

    print('environment variable ORBITS set to path', os.environ['ORBITS'],
          '\nenvironment variable REFL_CODE set to path', os.environ['REFL_CODE'],
          '\nenvironment variable EXE set to path', os.environ['EXE'])


def download_crx2rnx(system=None, path_to_executables=None):
    if not system:
        system = platform.platform().lower()

    if not path_to_executables:
        # if no path is provided, then the path to executables will be in the repo from the notebooks
        try:
            path_to_executables = os.environ['EXE']
        except KeyError:
            print('you must have your environment variables set. Please use the set_environment function to set the your EXE environment variable path')
            sys.exit()
    else:
        os.environ['EXE'] = path_to_executables
        print(f'reset environment variable to the requested path_to_executables: {os.environ["EXE"]}')

    if 'macos' in system:
        download_file = 'RNXCMP_4.0.8_MacOSX10.14_gcc.tar.gz'
        downloaded_dir = 'RNXCMP_4.0.8_MacOSX10.14_gcc'
    elif 'linux' in system and '64' in system:
        download_file = 'RNXCMP_4.0.8_Linux_x86_64bit.tar.gz'
        downloaded_dir = 'RNXCMP_4.0.8_Linux_x86_64bit'
    elif 'linux' in system and '32' in system:
        download_file = 'RNXCMP_4.0.8_Linux_x86_64bit.tar.gz'
        downloaded_dir = 'RNXCMP_4.0.8_Linux_x86_64bit'
    elif 'sunos' in system:
        download_file = 'RNXCMP_4.0.8_SunOS5.9_32bit.tar.gz'
        downloaded_dir = 'RNXCMP_4.0.8_SunOS5.9_32bit'
    elif 'windows' in system and '32' in system:
        download_file = 'RNXCMP_4.0.8_Windows_mingw_32bit.tar'
        downloaded_dir = 'RNXCMP_4.0.8_Windows_mingw_32bit'
    elif 'windows' in system and '64' in system:
        download_file = 'RNXCMP_4.0.8_Windows_mingw_64bit.tar'
        downloaded_dir = 'RNXCMP_4.0.8_Windows_mingw_64bit'
    else:
        print('We could not identify your operating system.'
              'Please add the parameter system= with either macos, linux32, linux64, sunos, windows32, or windows64')
        sys.exit()

    download_path = 'https://terras.gsi.go.jp/ja/crx2rnx/'
    try:
        # download the correct file from the site
        print('downloading CRX2RNX file')
        urllib.request.urlretrieve(os.path.join(download_path, download_file), os.path.join(path_to_executables, download_file))

        # uncompress the file
        tar = tarfile.open(os.path.join(path_to_executables, download_file))
        tar.extractall(path_to_executables)
        tar.close()

        print('file placed in path to execubles set by EXE environment variable')
        current_destination = os.path.join(path_to_executables, f'{downloaded_dir}/bin/CRX2RNX')
        os.replace(current_destination, os.path.join(path_to_executables, 'CRX2RNX'))

        # cleanup and move the file where we need it
        os.remove(os.path.join(path_to_executables, download_file))
        shutil.rmtree(os.path.join(path_to_executables, downloaded_dir))

        print('finished')

    except FileNotFoundError:
        print('could not find the correct executable path. Please set the parameter path_to_excecutables= and set this to '
              'the absolute path to where you would like this file place. Please make sure this path is the same as your environment variable EXE')
        sys.exit()


