FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Node.js + pi runtime deps
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    ca-certificates \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
       | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
       > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && npm install -g @mariozechner/pi-coding-agent \
    && rm -rf /var/lib/apt/lists/*

# Non-root runtime user
RUN useradd --create-home --shell /bin/bash pi

# Baked-in assets live outside $HOME so host ~/.pi mounts don't hide them
COPY skills /opt/pibox/skills
COPY defaults /opt/pibox/defaults
COPY entrypoint.sh /usr/local/bin/pibox-entrypoint.sh
RUN chmod +x /usr/local/bin/pibox-entrypoint.sh

USER pi
WORKDIR /workdir

ENV HOME=/home/pi
ENV PIBOX_SKILLS_DIR=/opt/pibox/skills
ENV PIBOX_DEFAULTS_DIR=/opt/pibox/defaults
ENV PI_CODING_AGENT_DIR=/home/pi/.pi/agent

ENTRYPOINT ["/usr/local/bin/pibox-entrypoint.sh"]
CMD ["pi"]
