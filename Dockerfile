# This will be the Dockerfile for event response 

# Start from the jupyter/scipy-notebook image, which includes....
# python3, scipy, pandas, matplotlib, ipywidgets (activated), numba, hdf5, etc...
# For more information... https://hub.docker.com/r/jupyter/scipy-notebook/dockerfile

FROM jupyter/scipy-notebook
WORKDIR /home/jovyan/gnssir_jupyter

MAINTAINER = UNAVCO Inc.

USER root

RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get install -y gfortran && \
    rm -rf /var/lib/apt/lists/*

# COPY the bin folder (code that should not be edited by the user) into the docker
COPY --chown=$NB_UID:users /bin /home/jovyan/gnssir_jupyter/bin
RUN chmod +x /home/jovyan/gnssir_jupyter/bin/*
ENV PYTHONPATH "${PYTHONPATH}:/home/jovyan/gnssir_jupyter/bin"

# Copy the data directory
COPY --chown=$NB_UID:users /data /home/jovyan/gnssir_jupyter/data
RUN chmod +x /home/jovyan/gnssir_jupyter/data/*
ENV PYTHONPATH "${PYTHONPATH}:/home/jovyan/gnssir_jupyter/data"

# Copy the orbits directory
COPY --chown=$NB_UID:users /orbits /home/jovyan/gnssir_jupyter/orbits
ENV PYTHONPATH "${PYTHONPATH}:/home/jovyan/gnssir_jupyter/orbits"

# Change user to default jupyter user (from jupyter/scipy-notebook Dockerfile)
USER $NB_UID

# Install packages with pip
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
RUN pip install --quiet --no-cache-dir --requirement /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

COPY notebooks/* /home/jovyan/gnssir_jupyter/notebooks/

# Start the jupyter notebook upon executuion
ENTRYPOINT ["jupyter", "notebook", "--no-browser", "--ip=*", "--allow-root", "--notebook-dir=/home/jovyan/gnssir_jupyter/"]
