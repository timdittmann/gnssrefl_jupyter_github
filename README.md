# GNSS Reflectometry Jupyter Stack

Jupyter Notebooks for the GNSS interferometric reflectometry python package hosted at https://github.com/kristinemlarson/gnssrefl

## Use Notebooks with Docker Container
### Step 1. Install Docker 
&ensp;&ensp; Pick your system and follow instructions on the Docker website. 
* **Mac** - https://docs.docker.com/docker-for-mac/install/ 
* **Windows** - https://docs.docker.com/docker-for-windows/install/ 
* **Ubuntu** - https://docs.docker.com/install/linux/docker-ce/ubuntu/ 

*Once installed, type `docker run hello-world` in terminal to check if installed correctly.*

More information on [getting started, testing your installation, and developing.](https://docs.docker.com/get-started/) 

### Step 2. Clone the Git Repository to your local machine 
For instructions on how to install git on any OS: https://github.com/git-guides/install-git

Use the HTTPS link in this repository to clone the repository to your local machine. You may do this in a terminal 
using git or use a git client ([Fork](https://git-fork.com/), etc...) You will want to do this in a location on your local computer that you 
wish to store the repository.

To clone a repository onto your local machine using the HTTPS link, click on the drop down that says 'clone' in the 
repository and copy the link that says 'Clone with HTTPS'. Using your terminal, navigate to where you would like to clone 
the repository and then run the command `git clone [https url]`

To get the latest version of master or your own branch,  use the git pull command from inside the now-local repository.   

***
### Step 3. Build the docker image and running the container
#### option 1:
This repository includes a shell script that will set up the image and container for you. Once you give it executable permission, you can run:
`./build_docker.sh`

This will build the docker image and run the container. Once everything has finished building in the terminal, you can copy and paste one of the urls provided at th end into a browser and run the jupyter notebooks from there.
The url will look something like `http://127.0.0.1:8888/?token=` with a randomly generated token at the end.
#### option 2:
To set up the docker image and container without the shell script, use the following instructions:
##### **Build the Docker image**

Navigate to the directory where the Dockerfile is stored and run... 

`docker build --rm -t gnssir_jupyter/python .`

Description of the commands used:
* `--rm `: remove temporary images built
* `-t` : tag/name the docker image 'event_response/python'
* `.` : to build it in current directory

##### Run image as container
Prior to running the docker, make sure you do not have other jupyter notebooks running on 8888 or else it will not work properly. To open the jupyter notebook directly in the run command...

`docker run -it -p 8888:8888 --name='gnssir_jupyter' -e GRANT_SUDO=yes --user root --env-file gnssir_env.txt --restart=unless-stopped gnssir_jupyter/python`

Description of the commands used:
* `-it` : interactive process (shell)
* `-p` : publish on port
* `--name` : name of docker container
* `reference docker image`

The following are additional commands that are optional:

##### (optional) Add your own directories as external volumes
If you want to add your own external volume add another `-v` command to the docker run command. You can add as many external volumes as you wish. All changes will be reflected on your host computer.

`-v ~/[your_host_directory]:/home/jovyan/gnssir_jupyter/[personal_directory_name]`

##### (optional) Run image as container in detached mode
If instead you wish to not run the container in the current terminal, then run the container in detached mode. To do this, add a `-d` to the docker run command...

`docker run -it -d -p 8888:8888 --name='gnssir_jupyter' -e GRANT_SUDO=yes --user root -v ~[path_to_local_repository]/notebooks:/home/jovyan/gnssir_jupyter --env-file gnssir_env.txt --restart=unless-stopped gnssir_jupyter/python`

If your container is running and you need to enter the container (such as detached mode), then use the `docker exec` command to enter the container in a bash shell. 

`docker exec -it gnssir_jupyter /bin/bash`

From here you can obtain the token for the Jupyter Notebook by running the command `jupyter notebook list` to get the link and token to run the notebook in your browser. 

#### Stop container & rm container
If you need to change your docker run command, exit out of jupyter notebook (Control-C), stop, and remove the container before running a new one.

`docker stop gnssir_jupyter`

`docker rm gnssir_jupyter`

#### Remove image
If you need to rebuild the image, follow the previous steps to remove the container and then remove the image before trying to rebuild. 

`docker image rm gnssir_jupyter/python`

***
## Use Notebooks without Docker
If you do not wish to use the docker container, then you can run Jupyter notebook using your local Python 3 environment.


**NOTE** this setup requires system dependencies: **gcc** and **gfortran**.

To install:
* if you are using a LINUX then simply run `apt-get install -y gcc` and `apt-get install -y gcc` in your terminal.
* if you are using a MacOS then you will need to install xcode. First, in your terminal, check if you have xcode by `xcode-select -p`. 
If it is installed, it should return a path. If it is not installed then run `xcode-select --install`. 
This should install gcc.You can check if you have gcc by `gcc --version`. Check if you have gfortran by `gfortran --version`.
If you do not have gfortran, then follow instructions to install for your system [here](https://gcc.gnu.org/wiki/GFortranBinariesMacOS) for MacOS 
and [here](https://gcc.gnu.org/wiki/GFortranBinaries) for Linux.

If you are still experiencing trouble then it is recommended you try the docker version of these notebooks. See above.
### Clone the Git Repository to your local machine 
For instructions on how to install git on any OS: https://github.com/git-guides/install-git

Use the HTTPS link in this repository to clone the repository to your local machine. You may do this in a terminal 
using git or use a git client ([Fork](https://git-fork.com/), etc...) You will want to do this in a location on your local computer that you 
wish to store the repository.

To clone a repository onto your local machine using the HTTPS link, click on the drop down that says 'clone' in the 
repository and copy the link that says 'Clone with HTTPS'. Using your terminal, navigate to where you would like to clone 
the repository and then run the command `git clone [https url]`

To get the latest version of master or your own branch, use the git pull command from inside the now-local repository.   

### pip install requirements
To install all the required python packages, use pip to install the requirements.txt file. 
Navigate to the gnssrefl_jupyter directory (where you cloned this repository) that contains the requirements.txt file and run:

`pip install -r requirements.txt`

*note that depending on your environmnet you may need to use pip3 instead of pip.
### run jupyter notebook
run the command jupyter notebook and it should open a local jupyter instance in a browser.

`jupyter notebook`

***

# Directories

## **The notebook directory**

The notebook directory is where we store the notebooks for the gnssir use cases.

## **The bin directory**

The bin directory contains all of the executable and importable scripts. 

## **The data directory**

Contains any data or figures needed to generate content for the gnssir notebooks.

***

