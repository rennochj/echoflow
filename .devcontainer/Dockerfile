FROM cgr.dev/chainguard/python:latest-dev

USER root

RUN <<EOT

    apk update && apk add posix-libc-utils && ldconfig
    apk add zsh zsh-vcs curl wget git vim make jq docker coreutils nodejs npm
    apk add sudo-rs shadow && echo "nonroot ALL = (ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers && echo y | pwck -q || true

    # Create docker group and add nonroot user to it
    sudo addgroup docker
    sudo addgroup nonroot docker

    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o ~/awscliv2.zip
    unzip ~/awscliv2.zip
    sudo ./aws/install --bin-dir /usr/bin --install-dir /usr/aws-cli --update

EOT

USER nonroot

RUN <<EOT

    cd $HOME
    
    # Create a directory for global packages

    mkdir ~/.npm-global

    # Configure npm to use it
    npm config set prefix '~/.npm-global'

    # Add to your PATH
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.profile
    source ~/.profile
    
    # Verify configuration
    npm config get prefix
    # Should show: /home/username/.npm-global

    npm install -g @anthropic-ai/claude-code
    npm install -g @google/gemini-cli
    npm install -g @jschuller/perplexity-mcp

    pip install --upgrade pip

    # Install UV
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Install default shell
    command -v zsh | sudo tee -a /etc/shells
    chsh nonroot --shell /usr/bin/zsh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

EOT

# Create entrypoint script
RUN <<EOT

cat <<'EOF' > /home/nonroot/entrypoint.sh && chmod +x /home/nonroot/entrypoint.sh
#!/bin/sh
set -e

# Setup docker socket if it exists
if [ -S /var/run/docker.sock ]; then
    sudo chown root:docker /var/run/docker.sock
fi

# Run command or default to sleep infinity
if [ $# -gt 0 ]; then
    exec "$@"
else
    exec sleep infinity
fi

EOT

COPY --chown=nonroot:nonroot .devcontainer/dotfiles/* /home/nonroot

ENTRYPOINT ["/home/nonroot/entrypoint.sh"]
