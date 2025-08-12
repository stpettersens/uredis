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
# > curl -sSf https://uredis.stpettersen.xyz/setup | sudo bash
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

# Default installation directory (no trailing slash).
install_dir="/opt/uredis"

# Define the logo.
logo="https://uredis.homelab.stpettersen.xyz/logo.txt"

# Define the latest release (a symbolic link to the latest file).
latest_release="https://uredis.homelab.stpettersen.xyz/releases/uredis_latest.zip"

# Define the Dockerfile.
dockerfile="https://uredis.homelab.stpettersen.xyz/Dockerfile"

# Define services manager for starting Docker service.
serviceman="systemctl enable docker"
start="systemctl start docker"

# Define Alpine Linux (apk) packages:
apk_pkgs=(
    "coreutils"
    "curl"
    "unzip"
    "python3"
    "docker"
)

# Define Void Linux (xbps) packages:
xbps_pkgs=(
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

# Define FreeBSD (pkg) packages.
pkg_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
)
set_rc=""

# Define OpenBSD (pkg_info) packages.
pkg_add_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
)

# Define SIP (sip) packages.
sip_pkgs=(
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
    echo "Redis compatible server and client in Python."
    echo "Written by Sam Saint-Pettersen <s dot stpettersen at pm dot me>"
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
    os=$(echo $os | awk '{ print $1 }')
    echo "Detected $os as operating system."
    sleep 3
}

update_packages() {
    echo "Updating package index..."
    case $os in
        "Alpine")
            alpine_enable_all_repos
            apk update
            ;;
        "Void")
            xbps-install -Syu
            ;;
        "Arch")
            pacman -Syu --noconfirm
            ;;
        "Debian"|"Ubuntu")
            apt-get update -y
            ;;
        "FreeBSD")
            pkg update
            if [[ -z $set_rc ]]; then
                echo "docker_enable=\"YES\"" >> /etc/rc.conf
                set_rc="1"
            fi
            ;;
        "OpenBSD")
            pkg_info update
            ;;
    esac
}

install_packages() {
    python="python3"
    if [[ $1 == 0 ]] || [[ $1 == 1 ]]; then
        echo "Installing required packages..."
    else
        echo "Installing Docker..."
    fi
    local end
    local pkgs
    local pkgman
    case $os in
        "Alpine")
            end=2
            pkgs=("${apk_pkgs[@]}")
            pkgman="apk add"
            serviceman="rc-update add docker default"
            start="rc-service docker start"
            ;;
        "Void")
            end=1
            pkgs=("${xbps_pkgs[@]}")
            pkgman="xbps-install -Sy"
            serviceman="ln -sf /etc/sv/docker /var/service/"
            ;;
        "Arch")
            end=1
            pkgs=("$pacman_pkgs[@]}")
            pkgman="pacman -Sy --noconfirm"
            ;;
        "Debian"|"Ubuntu")
            end=1
            pkgs=("${apt_pkgs[@]}")
            pkgman="apt-get install -y"
            ;;
        "FreeBSD")
            install_dir="/usr/local/opt/uredis"
            end=1
            pkgs=("${pkg_pkgs[@]}")
            pkgman="pkg install"
            serviceman="service docker start"
            ;;
        "OpenBSD")
            install_dir="/usr/local/opt/uredis"
            end=1
            pkgs=("${pkg_add_pkgs[@]}")
            pkgman="pkg_add"
            serviceman="rcctl set docker on"
            ;;
         *)
            end=0
            pkgs=("${sip_pkgs[@]}")
            pkgman="sip add"
    esac
    local middle
    local last
    (( middle = end + 1 ))
    (( last = end + 2 ))
    if [[ $1 == 0 ]]; then
        for ((i=0; i<=1; i++)); do
            echo "Installing ${pkgs[i]}..."
            $pkgman "${pkgs[i]}"
        done
    elif [[ $1 == 1 ]]; then
        echo "Installing ${pkgs[$middle]}..."
        $pkgman "${pkgs[$middle]}"
    else
        echo "Installing ${pkgs[$last]}..."
        $pkgman "${pkgs[$last]}"
    fi
}

download_uredis_latest() {
    echo "Downloading latest uRedis release..."
    curl -sSf $latest_release > $(basename $latest_release)
}

install_uredis_system() {
    echo "Installing uRedis on system..."
    mkdir -p $install_dir
    mv $(basename $latest_release) $install_dir
    cd $install_dir
    unzip -qq -o $install_dir/$(basename $latest_release)
    rm -f $install_dir/$(basename $latest_release)
    chown -R $1:$1 $install_dir
}

create_server_wrapper() {
    echo "#!/bin/sh" > /usr/local/bin/uredis-server
    echo "$python ${install_dir}/uredis-server.pyz \$@" >> /usr/local/bin/uredis-server
    chmod +x /usr/local/bin/uredis-server
}

create_client_wrapper() {
    echo "#!/bin/sh" > /usr/local/bin/uredis-client
    echo "$python ${install_dir}/uredis-client.pyz \$@" >> /usr/local/bin/uredis-client
    chmod +x /usr/local/bin/uredis-client
}

setup_docker() {
    if [[ $os == "Alpine" ]]; then
        addgroup $1 docker
    else
        usermod -aG docker $1
    fi
    $serviceman
    $start
}

generate_run_docker_shellscript() {
    echo "#!/bin/sh" > run_uredis_container.sh
    echo "docker network create ${1}_network" > run_uredis_container.sh
    echo "docker run --rm --network ${1}_network --name uredis_${1} -h uredis -v ($pwd):/opt/uredis -d uredis_img" >> run_uredis_container.sh
    echo "ip_address=\$(docker inspect --format {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} uredis_${1})" >> run_uredis_container.sh
    echo "echo \"APP_NETWORK=${1}_network\" > .env" >> run_uredis_container.sh
    #echo "echo \"${1##}_REDIS_HOST=${ip_address}\" >> .env" >> run_uredis_container.sh
    #echo "echo \"${1##}_REDIS_PORT=6379\" >> .env" >> run_uredis_container.sh
    chown $2:$2 run_uredis_container.sh
    chmod +x run_uredis_container.sh
}

build_uredis_image_docker() {
    clear
    echo "Building uRedis image (uredis-img) for Docker..."
    curl -sSf $dockerfile > $(basename $dockerfile)
    unzip -qq -o $(basename $latest_release)
    rm -f $(basename $latest_release)
    if [[ -f "uredis-server.pyz" ]] && [[ -f "uredis-client.pyz" ]]; then
        docker build -t uredis_img .
        rm -f README.md
        rm -f version.txt
    else
        echo "Could not build Docker image as a PYZ file does not exist!"
        exit 1
    fi
}

main() {
    prompt
    detect_os
    update_packages
    install_packages 0
    print_uredis_logo
    mkdir -p uredis
    cd uredis
    download_uredis_latest
    local install
    local user
    read -p "Install uRedis on system or on Docker [SYSTEM/docker]? " install < /dev/tty
    if [[ -z $install ]] || [[ ${install,,} == 'system' ]]; then
        read -p "Enter installation dir [$install_dir]: " install_dir < /dev/tty
        if [[ -z $install_dir ]]; then
            install_dir="/opt/uredis"
            if [[ $os == "FreeBSD" ]] || [[ $os == "OpenBSD" ]]; then
                install_dir="/usr/local/opt/uredis"
            fi
        fi
        while [[ -z $user ]]; do
            read -p "Enter user who should own installation dir: " user < /dev/tty
        done
        install_packages 1
        print_uredis_logo
        install_uredis_system $user
        create_server_wrapper
        create_client_wrapper
        rm -rf /home/$user/uredis
        echo "Done."
        echo
        echo "Run uRedis server with: \"uredis-server\""
        echo "Run uRedis client with: \"uredis-client\""

    else
        while [[ -z $user ]]; do
            read -p "Enter user who should run the Docker service: " user < /dev/tty
        done
        chown -R $user:$user $(pwd)
        local appname="default"
        read -p "Enter name for app which will use this instance? [$appname]: " appname < /dev/tty
        if [[ -z $appname ]]; then
            appname="default"
        fi
        install_packages 2
        setup_docker $user
        build_uredis_image_docker
        print_redis_logo
        generate_run_docker_shellscript $appname $user
        echo "Done."
        echo
        echo "An image (uredis-img) has been created for Docker:"
        echo "Run \"docker image ls\" to see it."
        echo
        echo "Run \"./run_uredis_container.sh\" to run an instance of that image."
    fi
    echo
    echo
    exit 0
}

main
