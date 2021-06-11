# GNSS Reflectometry Jupyter Stack

Jupyter Notebooks using the GNSS IR reflectometry code written by Kristine Larson. See https://github.com/kristinemlarson/gnssrefl

### 1. Install Docker 
&ensp;&ensp; Pick your system and follow instructions on the Docker website. \
* **Mac** - https://docs.docker.com/docker-for-mac/install/ \
* **Windows** - https://docs.docker.com/docker-for-windows/install/ \
* **Ubuntu** - https://docs.docker.com/install/linux/docker-ce/ubuntu/ \

*Once installed, type `docker run hello-world` in terminal to check if installed correctly.*

More information on [getting started, testing your installation, and developing.](https://docs.docker.com/get-started/) 

### 2. Clone the Git Repository to your local machine 
Use the HTTPS link in this repository to clone the repository to your local machine. You may do this in a terminal 
using git or use a git client ([Fork](https://git-fork.com/), etc...) You will want to do this in a location on your local computer that you 
wish to store the repository. 

To get the latest version of master or your own branch, use the git pull command.   

***

### **Building the Docker image**
Navigate to the directory where the Dockerfile is stored and run... 

`docker build --rm -t gnssir_jupyter/python .`

#### Description of commands used
* `--rm `: remove temporary images built
* `-t` : tag/name the docker image 'event_response/python'
* `.` : to build it in current directory

### Run image as container
Prior to running the docker, make sure you do not have other jupyter notebooks running on 8888 or else it will not work properly. To open the jupyter notebook directly in the run command...

`docker run -it -p 8888:8888 --name='gnssir_jupyter_docker' -e GRANT_SUDO=yes --user root -v ~[path_to_local_repository]/notebooks:/home/jovyan/gnssir_jupyter --env-file gnssir_env.txt --restart=unless-stopped gnssir_jupyter/python`

#### Description of commands used
* `-it` : interactive process (shell)
* `-p` : publish on port
* `--name` : name of docker container
* `-v` : sets up external volume (volume on your host computer), can set up multiple with multiple -v flags
* `reference docker image`

### Add your own directories as external volumes
If you want to add your own external volume add another `-v` command to the docker run command. You can add as many external volumes as you wish. All changes will be reflected on your host computer.

`-v ~/[your_host_directory]:/home/jovyan/gnssir_jupyter/[personal_directory_name]`

### Run image as container in detached mode
If instead you wish to not run the container in the current terminal, then run the container in detached mode. To do this, add a `-d` to the docker run command...

`docker run -it -d -p 8888:8888 --name='gnssir_jupyter_docker' -e GRANT_SUDO=yes --user root -v ~[path_to_local_repository]/notebooks:/home/jovyan/gnssir_jupyter --env-file gnssir_env.txt --restart=unless-stopped gnssir_jupyter/python`

### Execute Docker in terminal 
If your container is running and you need to enter the container (such as detached mode), then use the `docker exec` command to enter the container in a bash shell. 

`docker exec -it gnssir_jupyter /bin/bash`

#### Obtain Jupyter Notebook token
From here you can obtain the token for the Jupyter Notebook by running the command `jupyter notebook list` to get the link and token to run the notebook in your browser. 

### Stop container & rm container
If you need to change your docker run command, exit out of jupyter notebook (Control-C), stop, and remove the container before running a new one.

`docker stop gnssir_jupyter`

`docker rm gnssir_jupyter`

### Remove image
If you need to rebuild the image, follow the previous steps to remove the container and then remove the image before trying to rebuild. 

`docker image rm gnssir_jupyter/python`

***

# Directories

## **The notebook directory**

The notebook directory is where we store the notebooks for the gnssir use cases.

### Event ID directory

When responding to an event, an event ID directory will be created and all generated data/figures/html pages will be stored in this directoy. When building the docker, set the notebook directory as an external volume and all of the generated content will be saved to your local machine. 


## **The bin directory**

The bin directory contains all of the executable and importable scripts. 

## **The data directory**

Contains any data or figures needed to generate content for the gnssir notebooks.

***

