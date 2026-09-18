# Base Ubuntu image
FROM ubuntu:latest

# Non-interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN=true

# Install necessary packages
RUN apt update && apt install -y \
    git wget curl \
    gcc-mingw-w64-x86-64 build-essential libssl-dev libffi-dev libsasl2-modules-gssapi-mit \
    python3 python3-dev python3-pip python3-venv pipx \
    nmap smbclient ldap-utils hashcat \
    krb5-user libkrb5-dev \
    proxychains4 ntpdate dnsutils net-tools iproute2 && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN pipx ensurepath

# Create a virtual environment
RUN python3 -m venv /opt/.venv

# Add Cargo, pipx and the virtual environment to PATH
ENV PATH="/root/.cargo/bin:/opt/.venv/bin:$PATH:/root/.local/bin"

# Install core Python tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel packaging

# Install specific Python tools
RUN pip install --no-cache-dir --upgrade aioquic certipy-ad ldeep

WORKDIR /root

# Install Kerbrute
RUN wget https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64 && \
    mv kerbrute_linux_amd64 kerbrute && \
    chmod +x kerbrute

# Install Impacket
RUN pip install --no-cache-dir --upgrade impacket

# Install NetExec (replacing CrackMapExec)
RUN pipx install git+https://github.com/Pennyw0rth/NetExec

# Install Responder
RUN git clone https://github.com/lgandx/Responder.git ./Responder && \
    pip install --no-cache-dir --upgrade ./Responder

# Install Kerberos Relay Attack Tools
RUN git clone https://github.com/dirkjanm/krbrelayx ./krbrelayx && \
    sed -i '/setAddComputer/d' ./krbrelayx/krbrelayx.py

# Install pnightmare
RUN git clone https://github.com/cube0x0/CVE-2021-1675 ./pnightmare

# Install pyGPOAbuse
RUN git clone https://github.com/Hackndo/pyGPOAbuse ./pyGPOAbuse

# Retrieve modified scripts for different attacks
RUN mkdir ./mssql_modified_script && \
    mkdir ./samaccountname_scripts && \
    mkdir ./acl_attack && \
    mkdir ./webshell && \
    curl https://raw.githubusercontent.com/Mayfly277/impacket/86a5cbf8a112d3f4442d6e9f920feb7d5abaaabc/examples/mssqlclient.py -o ./mssql_modified_script/mssqlclient.py && \
    curl https://raw.githubusercontent.com/ShutdownRepo/impacket/refs/heads/getST/examples/getST.py -o ./samaccountname_scripts/getST.py && \
    curl https://raw.githubusercontent.com/fortra/impacket/0c74df065eeffde8c24edb56e880ab49c82530b7/examples/renameMachine.py -o ./samaccountname_scripts/renameMachine.py && \
    curl https://raw.githubusercontent.com/ThePorgs/impacket/refs/heads/main/examples/dacledit.py -o ./acl_attack/dacledit.py

# Webshell attack scripts
COPY ./attacker-files/amsi-net-bypass.txt ./webshell/amsi-net-bypass.txt
COPY ./attacker-files/webshell.aspx ./webshell/webshell.aspx
COPY ./attacker-files/reverse_shell_command.py ./webshell/reverse_shell_command.py

# Install PowerSharpPack
RUN git clone https://github.com/S3cur3Th1sSh1t/PowerSharpPack ./PowerSharpPack

# Install PowerSploit
RUN git clone https://github.com/PowerShellMafia/PowerSploit ./PowerSploit

COPY ./attacker-files/rockyou.txt ./wordlists/rockyou.txt
COPY ./attacker-files/potential_passwords.txt ./wordlists/potential_passwords.txt
COPY ./attacker-files/potential_users.txt ./wordlists/potential_users.txt

# Install UV from the Astral image
COPY --from=ghcr.io/astral-sh/uv:0.10.5 /uv /uvx /bin/

WORKDIR /root/mcp-server

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY src/ ./src/
RUN uv sync --frozen

EXPOSE 8000

CMD ["uv", "run", "adpilot-mcp"]