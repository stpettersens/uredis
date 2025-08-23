#!/usr/bin/env bash
#
# This script will install uRedis from its latest available release
# along with any software packages (e.g. curl, python3, unzip) necessary to extract,
# install and run the distributed Python PYZ applications (uredis-server and uredis-client).
# To install uRedis in a similar way on Windows systems, please use uredis-setup.ps1
# This script works (where Bash exists) with:
#
# * Alpine Linux (run curl -sSf https://sh.homelab.stpettersen.xyz/alpine/install-bash | doas ash)
# * Void Linux
# * Arch Linux and its derivatives (e.g. Garuda, CachyOS).
# * Debian/Ubuntu Linux and its derivatives (e.g. Linux Mint, Zorin OS).
# * Fedora/RHEL Linux and its derivatives (e.g. Nobara).
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

# Define the OS variables, set later.
os=""
os_name=""

# Define the Python interpreter.
python="python3"

# Define the user elevation program, sudo by default.
sudo="sudo"

# Default installation directory (no trailing slash).
install_dir="/opt/uredis"

# Define the server root for assets served by this script.
server="https://uredis.homelab.stpettersen.xyz"

# Define the logo.
logo="$server/logo.txt"

# Define the latest release (a symbolic link to the latest file).
latest_release="$server/releases/uredis_latest.zip"

# Define the services package to install uRedis as a service.
services_pkg="$server/uredis_services.zip"

# Define the Dockerfile.
dockerfile="$server/Dockerfile"

# Define the requirements.txt file for optional dependencies.
requirements_txt="$server/requirements.txt"

# Define services manager for starting Docker service.
start="systemctl start docker"
serviceman="systemctl enable docker"
serviceman2=""

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

# Define Fedora/RHEL (dnf) packages:
dnf_pkgs=(
    "curl"
    "unzip"
    "python3"
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
pkg_add_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
)
#set_rc=""

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

start_prompt() {
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
    os=$(grep "^ID=" /etc/os-release | head -n 1 | cut -d '=' -f 2 | tr -d '"')
    os=$(echo $os | awk '{ print $1 }')
    os_name="${os^}"
    case $os in
        "rhel")
            os_name="${os^^}"
            ;;
        "freebsd")
            os_name="FreeBSD"
            ;;
        "openbsd")
            os_name="OpenBSD"
            ;;
    esac
    echo "Detected $os_name as operating system."
    sleep 1
}

update_packages() {
    echo "Updating package index..."
    case $os in
        "alpine")
            sudo="doas" # sudo is replaced by doas on alpine by default.
            alpine_enable_all_repos
            apk update
            ;;
        "void")
            xbps-install -Sy
            ;;
        "arch")
            pacman -Sy --noconfirm
            ;;
        "debian"|"ubuntu"|"linuxmint"|"zorin")
            apt-get update -y
            ;;
        "fedora"|"rhel")
            dnf update
            ;;
        "freebsd")
            sudo="doas"
            pkg update
            #if (($1==2)) && [[ -z $set_rc ]]; then
                #echo "docker_enable=\"YES\"" >> /etc/rc.conf
                #set_rc="1"
            #fi
            ;;
        "openbsd")
            sudo="doas"
            pkg_info update
            ;;
    esac
    clear
}

install_packages() {
    if (($1<=1)); then
        echo "Installing required packages..."
    fi
    local end
    local pkgs
    local pkgman
    case $os in
        "alpine")
            end=2
            pkgs=("${apk_pkgs[@]}")
            pkgman="apk add"
            serviceman="rc-update add docker default"
            start="service docker start"
            ;;
        "void")
            end=1
            pkgs=("${xbps_pkgs[@]}")
            pkgman="xbps-install -Sy"
            serviceman="ln -sf /etc/sv/docker /var/service/"
            start="sv up docker"
            ;;
        "arch")
            end=1
            pkgs=("${pacman_pkgs[@]}")
            pkgman="pacman -Sy --noconfirm"
            ;;
        "debian"|"ubuntu"|"linuxmint"|"zorin")
            end=1
            pkgs=("${apt_pkgs[@]}")
            pkgman="apt-get install -y"
            ;;
        "fedora"|"rhel")
            end=1
            pkgs=("${dnf_pkgs[@]}")
            pkgman="dnf install"
            ;;
        "freebsd")
            install_dir="/usr/local/opt/uredis"
            end=1
            pkgs=("${pkg_pkgs[@]}")
            pkgman="pkg install"
            serviceman="service docker start"
            serviceman2="service docker enable"
            ;;
        "openbsd")
            install_dir="/usr/local/opt/uredis"
            end=1
            pkgs=("${pkg_add_pkgs[@]}")
            pkgman="pkg_add"
            serviceman="rcctl set docker on"
            serviceman2="rcctl enable docker"
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

install_uredis_service() {
    echo "Installing uRedis as service..."
    unzip -qq -o $(basename $latest_release)
    curl -sSf $service_pkg > $(basename $services_pkg)
    unzip -qq -o $(basename $services_pkg)
    rm -f $(basename $services_pkg)
    mkdir -p /opt/uredis
    cp uredis/uredis-server.pyz /opt/uredis
    cp uredis/uredis-client.pyz /opt/uredis
    rm -rf uredis
    case $os in
        freebsd)
            pw useradd uredis
            chown -R uredis:uredis /opt/uredis
            cp uredis_services/freebsd/uredis_freebsd /etc/rc.d/uredis
            chmod +x /etc/rc.d/uredis
            service uredis onestart
            service uredis enable
            ;;
        openbsd)
            useradd uredis
            cp uredis_services/openbsd/uredis_openbsd /etc/rc.d/uredis
            chmod +x /etc/rc.d/uredis
            touch /opt/uredis/uredis.pid
            chown -R uredis:uredis /opt/uredis
            rcctl set uredis user uredis
            rcctl start uredis
            rcctl enable uredis
            ;;
        alpine)
            echo "TODO Install service for Alpine."
            exit 1
            ;;
        void)
            echo "TODO Install service for Void."
            exit 1
            ;;
        *) # Any Linux distro using SystemD
            useradd -m uredis
            cp uredis_services/systemd/uredis_systemd.service /etc/systemd/uredis.service
            chown -R uredis:uredis /opt/uredis
            systemctl enable uredis
            systemctl start uredis
            systemctl daemon-reload
            ;;
    esac
    rm -rf uredis_services
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
    if [[ $os == "alpine" ]]; then
        addgroup $1 docker
    else
        usermod -aG docker $1
    fi
    $serviceman
    $start
    if [[ -n $serviceman2 ]]; then
        sleep 3
        $serviceman2
    fi
    sleep 3
}

generate_run_docker_shellscript() {
    echo "#!/usr/bin/env bash" > run_uredis_container.sh
    echo "docker network create ${1}_network" >> run_uredis_container.sh
    echo "docker run --rm --network ${1}_network --name uredis_${1} -h uredis -v \$(pwd):/opt/uredis -d uredis_img" >> run_uredis_container.sh
    echo "ipaddress=\$(docker inspect --format \"{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\" uredis_${1})" >> run_uredis_container.sh
    echo "echo \"APP_NETWORK=${1}_network\" > ../.env" >> run_uredis_container.sh
    echo "echo \"${1^^}_REDIS_HOST=\$ipaddress\" >> ../.env" >> run_uredis_container.sh
    echo "echo \"${1^^}_REDIS_PORT=6379\" >> ../.env" >> run_uredis_container.sh
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
    else
        echo "Could not build Docker image as a PYZ file does not exist!"
        exit 1
    fi
}

main() {
    start_prompt
    detect_os
    update_packages 0
    install_packages 0
    print_uredis_logo
    mkdir -p uredis
    cd uredis
    download_uredis_latest
    local install
    local user
    read -p "Install uRedis on system or on Docker [SYSTEM/docker/service]? " install < /dev/tty
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
        install_uredis_system $user
        create_server_wrapper
        create_client_wrapper
        rm -rf /home/$user/uredis
        print_uredis_logo
        echo "Done."
        echo
        echo "Run uRedis server with: \"uredis-server\""
        echo "Run uRedis client with: \"uredis-client\""

    elif [[ ${install,} == 'docker' ]]; then
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
        generate_run_docker_shellscript $appname $user
        #update_packages 2
        print_uredis_logo
        echo "Done."
        echo
        echo "An image (uredis-img) has been created for Docker:"
        echo "Run \"$sudo docker image ls\" to see it."
        echo
        echo "ATTENTION:"
        echo "You may need to logout first to use Docker as a non-root user."
        echo
        echo "Under uredis subdirectory:"
        echo "Run \"./run_uredis_container.sh\" to run an instance of that image."
    else
        # Install uRedis as a service...
        cd ..
        install_uredis_service
        create_server_wrapper
        create_client_wrapper
        print_uredis_logo
        echo "Done."
        echo
        echo "uRedis has been installed as a service on $os_name."
        echo "It has been configured to run now and on system startup."
    fi
    echo
    echo
    exit 0
}

main
