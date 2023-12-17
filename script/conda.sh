#!/bin/bash
# download miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# install miniconda
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
rm -rf Miniconda3-latest-Linux-x86_64.sh

# create env var
export PATH="/miniconda/bin:${PATH}"

# create conda environment
conda create -n $ENV_NAME python=$VERSION -y

# add to bashrc for debugging in interactive mode
echo "source /miniconda/bin/activate $ENV_NAME" >> /root/.bashrc
