#!/usr/bin/env bash
#
# This script install uRedis from its latest available release
# along with any software packages (e.g. curl, python3, unzip) necessary to extract,
# install and run the distributed Python PYZ applications (uredis-server and uredis-client).
# To install uRedis in a similar way on Windows systems, please use uredis-setup.ps1
# This script works (where Bash exists) with:
#
# * Void Linux
# * Alpine Linux (run curl -sSf https://sh.homelab.stpettersen.xyz/alpine/install-bash | doas ash)
# * Arch Linux and its derivatives (e.g. Garuda, CachyOS).
# * Debian/Ubuntu Linux and its derivatives (e.g. Linux Mint, Zorin OS).
# * Generic Linux (any other distribution with my package manager SIP)
# * FreeBSD
# * OpenBSD
#
# Usage:
# ------------------------------------------------------------------
# Please install bash (if necessary) and curl.
# ------------------------------------------------------------------
# > curl -sSf https://uredis.stpettersen.xyz/setup | doas bash
#
# OR SAFER WAY, INSPECTING THE SCRIPT CONTENTS BEFORE RUNNING:
# > curl -sSf https://uredis.stpettersen.xyz/setup > uredis-setup.sh
# > cat uredis-setup.sh
# > bash uredis-setup.sh
# ------------------------------------------------------------------

# Define the OS variable, set later.
os=""

# Define the Python interpreter variable, set it later.
python=""

# Define the logo.
logo="https://uredis.homelab.stpettersen.xyz/logo.txt"

# Define the latest release (a symbolic link to the latest file).
latest_release="https://uredis.homelab.stpettersen.xyz/releases/uredis_latest.zip"

# Define the Dockerfile.
dockerfile="https://uredis.homelab.stpettersen.xyz/Dockerfile"

# Default installation directory.
install_dir="/opt/uredis"

# Define Void Linux (xbps) packages:
xbps_pkgs=(
    "curl"
    "unzip"
    "python3"
    "docker"
)

# Define Alpine Linux (apk) packages:
apk_pkgs=(
    "coreutils"
    "curl"
    "unzip"
    "python3"
    "docker"
)

# Define Arch Linux (pacman) packages:
pacman_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
)

# Define Ubuntu (apt) packages:
apt_pkgs=(
    "curl"
    "unzip"
    "python3"
    "docker.io"
)

# Define SIP (sip) packages.
sip_pkgs=(
    "unzip"
    "python"
    "docker"
)

# Define FreeBSD (pkg) packages.
pkg_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
)

# Define OpenBSD (pkg_info) packages.
pkg_info_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
)

print_uredis_logo() {
    clear
    echo
    curl -sSf $logo > $(basename $logo)
    cat $(basename $logo)
    rm -f $(basename $logo)
    echo
    echo
    echo
}

prompt() {
    clear
    echo "This script will install uRedis and necessary"
    echo "dependencies on your system."
    echo
    local continue
    read -p "Continue (y/N)? " continue < /dev/tty
    if [[ -z $continue ]] || [[ ${continue,,} == 'n' ]]; then
        exit 1
    else
        clear
    fi
}

alpine_enable_all_repos() {
    sed -i '3s/^# *//' /etc/apk/repositories
}

detect_os() {
    os=$(grep NAME /etc/os-release | head -n 1 | cut -d '=' -f 2 | tr -d '"')
    echo "Detected $os as operating system."
    sleep 3
}

update_pkgs() {
    echo "Updating package index..."
    case $os in
        "Alpine Linux")
            alpine_enable_all_repos
            apk update
            ;;
    esac
}

install_pkgs() {
    python="python3"
    if [[ $1 == 0 ]] || [[ $1 == 1 ]]; then
        echo "Installing required packages..."
    else
        echo "Installing Docker..."
    fi
    case $os in
        "Alpine Linux")
            if [[ $1 == 0 ]]; then
                for i in {0..2}; do
                    apk add "${apk_pkgs[i]}"
                done
            elif [[ $1 == 1 ]]; then
                apk add "${apk_pkgs[3]}"
            else
                apk add "${apk_pkgs[4]}"
            fi
            ;;
    esac
}

download_uredis_latest() {
    echo "Downloading latest uRedis release..."
    curl -sSf $latest_release > $(basename $latest_release)
}

install_uredis_system() {
    echo "Installing uRedis on system..."
    mkdir -p /opt/uredis
    mv $(basename $latest_release) /opt/uredis
    cd /opt/uredis
    unzip -qq -o /opt/uredis/$(basename $latest_release)
    rm -f /opt/uredis/$(basename $latest_release)
    chown -R $1:$1 /opt/uredis
}

create_server_wrapper() {
    echo "#!/bin/sh" > /usr/bin/uredis-server
    echo "$python /opt/uredis/uredis-server.pyz \$\@" >> /usr/bin/uredis-server
    chmod +x /usr/bin/uredis-server
}

create_client_wrapper() {
    echo "#!/bin/sh" > /usr/bin/uredis-client
    echo "$python /opt/uredis/uredis-client.pyz \$\@" >> /usr/bin/uredis-client
    chmod +x /usr/bin/uredis-client
}

install_uredis_docker() {
    echo "Installing uRedis on docker..."
    curl -sSf $dockerfile > $(basename $dockerfile)
}

main() {
    prompt
    detect_os
    update_pkgs
    install_pkgs 0
    print_uredis_logo
    download_uredis_latest
    local install
    read -p "Install uRedis on system or on Docker [SYSTEM/docker]? " install < /dev/tty
    if [[ -z $install ]] || [[ ${install,,} == 'system' ]]; then
        local user
        while [[ -z $user ]]; do
            read -p "Enter user who should own installation dir: " user < /dev/tty
        done
        install_pkgs 1
        install_uredis_system $user
        create_server_wrapper
        create_client_wrapper
    else
        install_pkgs 2
        install_uredis_docker
    fi
    exit 0
}

main
