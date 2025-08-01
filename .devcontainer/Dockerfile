# Base image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PATH=/usr/local/bin:$PATH

# Install core tooling: locales, git, curl, unzip, AWS CLI prereqs, PostgreSQL client, Node.js, Python, Docker CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      unzip \
      ca-certificates \
      gnupg \
      lsb-release \
      build-essential \
      software-properties-common \
      git \
      locales \
      python3 \
      python3-venv \
      python3-pip \
      sudo \
      apt-transport-https \
      lsb-release && \
    \
    # Locale setup
    sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    update-locale LANG=en_US.UTF-8 && \
    \
    # PostgreSQL client 13 (PGDG)
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/postgresql-archive-keyring.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" \
      | tee /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client-13 libpq-dev && \
    \
    # Install AWS CLI v2
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws && \
    \
    # Install Node.js 20.x (includes npm)
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    \
    # Install Docker CLI & Compose plugin (no daemon)
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
      https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli docker-compose-plugin && \
    \
    # Cleanup
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=1000

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Prepare workspace directory and give ownership
RUN mkdir -p /workspaces && chown -R $USERNAME:$USERNAME /workspaces

# Switch to non-root
USER $USERNAME
ENV HOME=/home/$USERNAME
WORKDIR /workspaces/${LOCAL_WORKSPACE_FOLDER_BASENAME:-workspace}

# Optional: upgrade pip in user context
RUN python3 -m pip install --upgrade pip

# Default shell
CMD [ "bash" ]
