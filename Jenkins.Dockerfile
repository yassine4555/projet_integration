FROM jenkins/jenkins:lts

USER root

# Install Git with OpenSSL support and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libcurl4-openssl-dev \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Update CA certificates
RUN update-ca-certificates

# Verify Git installation
RUN git --version

USER jenkins

# Skip initial setup wizard (optional)
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
