#!/usr/bin/env bash
#
# This script install uRedis from its latest available release
# along with any software packages (e.g. curl, python3, unzip) necessary to extract,
# install and run the distributed Python PYZ applications (uredis-server and uredis-client).
# To install uRedis in a similar way on Windows systems, please use uredis-setup.ps1
# This script works (where Bash exists) with:
#
# * Void Linux
# * Alpine Linux (run curl -sSf https://sh.homelab.stpettersen.xyz/alpine/install_bash | ash)
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
# > curl -sSf https://uredis.stpettersen.xyz/setup | bash
#
# OR SAFER WAY, INSPECTING THE SCRIPT CONTENTS BEFORE RUNNING:
# > curl -sSf https://uredis.stpettersen.xyz/setup > uredis-setup.sh
# > cat uredis-setup.sh
# > bash uredis-setup.sh
# ------------------------------------------------------------------

# Define the OS variable, set later.
os=""

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
    curl -sSf -k $logo > $(basename $logo)
    cat $(basename $logo)
    echo
}

alpine_enable_all_repos() {
    sed -i '2s/^# *//' /etc/apk/repositories
}

detect_os() {
    echo "!TODO"
    sleep 3
}

install_pkgs() {
    echo "!TODO"
    sleep 3
}

download_uredis_latest() {
    echo "Downloading latest uRedis release..."
    curl -sSf -k $latest_release > $(basename $latest_release)
}

install_uredis_system() {
    echo "Installing uRedis on system..."
}

install_uredis_docker() {
    echo "Installing uRedis on docker..."
    curl -sSf -k $dockerfile > $(basename $dockerfile)
}

main() {
    detect_os
    # Install curl first, but it should have been installed.
    install_pkgs 0
    print_uredis_logo

    exit 0
}

main
