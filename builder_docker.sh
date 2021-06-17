#! /bin/bash

echo "Resetting docker"
echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
echo "Stop / Remove gnssir_jupyter container - command -> docker stop and docker rm gnssir_jupyter_docker"
echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
docker stop gnssir_jupyter_docker
docker rm gnssir_jupyter_docker

echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
echo "Remove python image, image that made gnssir_jupyter_docker: command -> docker image rm python"
echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
docker image rm gnssir_jupyter/python

echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
echo "ReBuild gnssir_jupyter/python image in current directory: command -> docker build --rm -t gnssir_jupyter/python ."
echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
docker build --rm -t gnssir_jupyter/python . 

echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
echo "docker run gnssir_jupyter_docker container"
echo "Interactive, on port 8888, name = gnssir_jupyter_docker "
echo "Mount external volumes - notebooks & events directory, bin directoy is copied into Docker container"
echo "* Starting Container..."
echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

# Open jupyter notebook directly 
docker run \
        -it \
        -p 8888:8888 \
        --name='gnssir_jupyter_docker' \
        -e GRANT_SUDO=yes --user root \
        -v notebooks:/home/jovyan/gnssir_jupyter/notebooks \
 	    -v bin:/home/jovyan/gnssir_jupyter/bin \
        --env-file gnssir_env.txt \
        --restart=unless-stopped \
        gnssir_jupyter/python

# If you want to add your own external volume add another -v command to the docker run command
#-v ~/[path_to_local_directory]:/home/jovyan/gnssir_jupyter/[personal_directory]

echo *--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

# Do not open jupyter notebook directly - detached mode (-d), and then use docker execute to enter the container in a bash shell

#docker run -it -d -p 8888:8888 --name='gnssir_jupyter_docker' -e GRANT_SUDO=yes -v ./notebooks:/home/jovyan/gnssir_jupyter gnssir_jupyter/python
#docker exec -it gnssir_jupyter_docker /bin/bash
