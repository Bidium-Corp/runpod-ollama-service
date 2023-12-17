# Base image
FROM ollama/ollama:latest

# Set non-interactive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Set timezone for Git installation
ENV TZ=Europe/London

# Set some env variables
ENV USERNAME="user"
ENV PYTHON_VERSION="3.10"
ENV ENV_NAME="ollama_env"


# Update and install necessary packages
RUN apt update && \
    apt upgrade -y && \
    apt install -y sudo curl build-essential git-all wget \
    psmisc procps && \
    rm -rf /var/lib/apt/lists/*

# RUN apt-get install --reinstall ca-certificates

ARG PASSWORD="****"

# Creating a generic user
RUN useradd -m ${USERNAME} && \
    echo "${USERNAME}:${PASSWORD}" | chpasswd && \
    usermod -aG sudo ${USERNAME}

WORKDIR /home/${USERNAME}

# Copy the necessary files
COPY ./libs/ ./libs/
COPY ./script/ ./script/
COPY ./requirements.txt ./requirements.txt

# Add executable permissions to the scripts
RUN chmod +x ./script/*.sh

# # Install OLLAMA
RUN /bin/bash -c "./script/mistral.sh"

# Install conda virtual environment
RUN /bin/bash -c "./script/conda.sh"

# # # Activate the Conda environment and install dependencies
RUN /bin/bash -c "source /miniconda/bin/activate ${ENV_NAME} && \
    pip install --upgrade pip && \
    pip install -r requirements.txt"

ENTRYPOINT ["./script/entrypoint.sh"]