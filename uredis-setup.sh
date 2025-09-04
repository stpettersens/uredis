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
# * Arch Linux and its derivatives (e.g. Artix, Garuda, CachyOS).
# * Debian/Ubuntu Linux and its derivatives (e.g. Linux Mint, Zorin OS).
# * Slax Linux (Debian-based version).
# * Fedora/RHEL Linux and its derivatives (e.g. Nobara).
# * SUSE/OpenSUSE Linux.
# * Generic Linux (any other distribution with my package manager SIP).
# * FreeBSD.
# * OpenBSD.
#
# Usage:
# ------------------------------------------------------------------
# Please install bash (if necessary) and curl.
# ------------------------------------------------------------------
# > curl -sSf https://uredis.homelab.stpettersen.xyz/setup | sudo bash
#
# OR SAFER WAY, INSPECTING THE SCRIPT CONTENTS BEFORE RUNNING:
# > curl -sSf https://uredis.homelab.stpettersen.xyz/setup > uredis-setup.sh
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
logo="${server}/logo.txt"

# Define the latest release.
latest_release="${server}/releases/uredis_latest.zip"

# Define the services directory.
services="${server}/services"

# Define the Dockerfile.
dockerfile="${server}/Dockerfile"

# Define the requirements.txt file for optional dependencies.
requirements_txt="${server}/requirements.txt"

# Define services manager for starting Docker service.
start="systemctl start docker"
serviceman="systemctl enable docker"
serviceman2="" # set as necessary later.

# Using optional dependencies?
opt_deps=0

# Global switch overrides.
pkgmnr=""
initsystem=""

# Define Alpine Linux (apk) packages:
apk_pkgs=(
    "linux-headers"
    "gcc"
    "musl-dev"
    "python3-dev"
    "curl"
    "unzip"
    "python3"
    "docker"
    "uv"
)

# Define Void Linux (xbps) packages:
xbps_pkgs=(
    "curl"
    "unzip"
    "python3"
    "docker"
    "uv"
)

# Define Arch/Artix, etc. (pacman) packages:
pacman_pkgs=(
    "curl"
    "unzip"
    "python"
    "docker"
    "uv"
)

# Define Debian/Ubuntu, etc. (apt) packages:
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
    "uv"
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

# SUSE/OpenSUSE packages.
zypper_pkgs=(
    "curl"
    "unzip"
    "python3"
    "docker"
)

# Define SIP (sip) packages.
sip_pkgs=(
    "unzip"
    "python"
    "docker"
)

# Homebrew (e.g. Darwin) packages.
brew_pkgs=(
    "unzip"
    "python@3.13"
    "docker"
    "uv"
)

sha256cksm() {
    local status
    local cksum_file
    cksum_file=$1
    cksum_file="${cksum_file%.*}_sha256.txt"
    sleep 3
    curl -sSf "${server}/${cksum_file}" > "${cksum_file}"
    sha256sum -c "${cksum_file}" > /dev/null 2>&1
    status=$?
    if (( status == 1 )); then
        echo "SHA256 checksum failed for ${1}."
        echo "Aborting..."
        rm -f "${cksum_file}"
        exit 1
    else
        echo "SHA256 checksum OK for ${1}."
        sleep 3
    fi
    rm -f "${cksum_file}"
}

script_cksm() {
    if [[ ! -f "uredis-setup.sh" ]]; then
        curl -sSf "${server}/setup" > uredis-setup.sh
    fi
    sha256cksm "uredis-setup.sh"
    if [[ $(basename "$0") != "uredis-setup.sh" ]]; then
        rm -f uredis-setup.sh
    fi
    clear
}

print_uredis_logo() {
    clear
    echo
    if [[ ! -f "$(basename $logo)" ]]; then
        curl -sSf $logo > "$(basename $logo)"
    fi
    cat "$(basename $logo)"
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
    read -r -p "Continue (y/N)? " continue < /dev/tty
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
    os=$(echo "${os}" | awk '{ print $1 }')
    os_name="${os^}"
    case $os in
        "rhel"|"sles")
            os_name="${os^^}"
            ;;
        "opensuse-tumbleweed")
            os_name="OpenSUSE Tumbleweed"
            ;;
        "opensuse-leap")
            os_name="OpenSUSE Leap"
            ;;
        "freebsd")
            os_name="FreeBSD"
            ;;
        "openbsd")
            os_name="OpenBSD"
            ;;
        "artix")
            echo "Detected Artix as operating system."
            local initsys
            while [[ -z $initsys ]]; do
                read -r -p "Which init system are you using (openrc/runit/dinit/s6): " initsys < /dev/tty
                initsys="${initsys,,}"
                # Check a valid init system was set:
                case $initsys in
                    "openrc"|"runit"|"dinit"|"s6")
                        os="artix-${initsys}"
                        ;;
                    *)
                        unset initsys
                        ;;
                esac
            done
            sleep 1
            ;;
    esac
    detect_is_slax
    if [[ $os_name != "Artix" ]]; then
        echo "Detected $os_name as operating system."
        sleep 1
    fi
}

detect_is_slax() {
    # Determine is Slax by detecting the `genslaxiso` utility.
    local status
    command -v genslaxiso > /dev/null
    status=$?
    if (( status == 0 )); then
        unset os
        unset osname
        os="slax"
        os_name=${os^}
    fi
}

write_slax_iso_or_to_modules() {
    if [[ $os == "slax" ]]; then
        rm -rf /root/uredis
        rm -f /root/logo.txt
        local status
        lsblk | grep sdb > /dev/null
        status=$?
        if [[ $status == 0 ]]; then
            local modchanges
            read -r -p "Do you want to write changes including installed uRedis back to Slax modules? (y/N): " modchanges < /dev/tty
            if [[ -z $modchanges ]] || [[ ${modchanges,,} == "n" ]]; then
                return
            elif [[ ${modchanges,,} == "y" ]]; then
                # Write changes back to drive if running from a flash drive.
                echo "Please be patient, generating a new Slax module which contains uRedis..."
                savechanges /root/uredis.sb
                mv /root/uredis.sb /run/initramfs/memory/data/slax/modules/
                echo "uRedis has been written to Slax modules folder"
                echo "and will be available on reboot."
                echo
                echo
            else
                return
            fi
        else
            local writeiso
            read -r -p "Do you want to write an new Slax ISO with installed uRedis? (y/N): " writeiso < /dev/tty
            if [[ -z $writeiso ]] || [[ ${writeiso,,} == "n" ]]; then
                return
            elif [[ ${writeiso,,} == "y" ]]; then
                # Write an ISO if system is not running from a flash drive.
                echo "Please be patient, generating a new Slax ISO which contains uRedis..."
                savechanges /root/uredis.sb
                genslaxiso /root/slax_uredis.iso /root/uredis.sb
                rm -f /root/uredis.sb
                echo "Done."
                echo
                echo "A Slax ISO has been generated:"
                echo "/root/slax_uredis.iso"
                echo
                echo
            else
                return
            fi
        fi
    fi
}

update_packages() {
    echo "Updating package index..."
    if [[ -n $pkgmnr ]]; then
        case $pkgmnr in
            "apk")
                sudo="doas"
                alpine_enable_all_repos
                apk update
                ;;
            "xbps")
                xbps-install -Sy
                ;;
            "pacman")
                pacman -Sy --no-confirm
                ;;
            "apt-get")
                apt-get update -y
                ;;
             "dnf")
                dnf update
                ;;
             "zypper")
                zypper refresh
                ;;
             "pkg")
                pkg update
                ;;
             "pkg_info")
                pkg_info update
                ;;
             "homebrew"|"brew")
                brew update
                ;;
        esac
        clear
        return
    fi
    case $os in
        "alpine")
            sudo="doas" # sudo is replaced by doas on alpine by default.
            alpine_enable_all_repos
            apk update
            ;;
        "void")
            xbps-install -Sy
            ;;
        "arch"|"artix-openrc"|"artix-runit"|"artix-dinit"|"artix-s6"|"garuda"|"cachyos")
            pacman -Sy --noconfirm
            ;;
        "debian"|"ubuntu"|"linuxmint"|"zorin"|"slax")
            apt-get update -y
            ;;
        "fedora"|"rhel")
            dnf update
            ;;
        "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
            zypper refresh
            ;;
        "freebsd")
            sudo="doas"
            pkg update
            ;;
        "openbsd")
            sudo="doas"
            pkg_info update
            ;;
        "darwin")
            brew update
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
    local pm
    case $os in
        "alpine")
            end=5
            pkgs=("${apk_pkgs[@]}")
            pkgman="apk add"
            pm="apk"
            serviceman="rc-update add docker default"
            start="rc-service docker start"
            ;;
        "artix-openrc")
            end=1
            pkgs=("${pacman_pkgs[@]}")
            pkgman="pacman -Sy --noconfirm"
            pm="pacman"
            serviceman="rc-update add docker default"
            start="rc-service docker start"
            ;;
        "void")
            end=1
            pkgs=("${xbps_pkgs[@]}")
            pkgman="xbps-install -Sy"
            pm="xbps"
            serviceman="ln -sf /etc/sv/docker /var/service/"
            start="sv up docker"
            ;;
        "artix-runit")
            end=1
            pkgs=("${pacman_pkgs[@]}")
            pkgman="pacman -Sy --noconfirm"
            pm="pacman"
            serviceman="ln -sf /etc/sv/docker /var/service/"
            start="sv up docker"
            ;;
        "artix-s6")
            end=1
            pkgs=("${pacman_pkgs[@]}")
            pkgman="pacman -Sy --noconfirm"
            pm="pacman"
            serviceman="ln -s /etc/s6/docker /service/docker"
            ;;
        "arch"|"garuda"|"cachyos")
            end=1
            pkgs=("${pacman_pkgs[@]}")
            pkgman="pacman -Sy --noconfirm"
            pm="pacman"
            serviceman="service enable docker"
            start="service start docker"
            ;;
        "debian"|"ubuntu"|"linuxmint"|"zorin"|"slax")
            end=1
            pkgs=("${apt_pkgs[@]}")
            pm="apt-get"
            pkgman="apt-get install -y"
            ;;
        "fedora"|"rhel")
            end=1
            pkgs=("${dnf_pkgs[@]}")
            pm="dnf"
            pkgman="dnf install"
            ;;
        "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
            end=1
            pkgs=($"${zypper_pkgs[@]}")
            pm="zypper"
            pkgman="zypper -n install"
            ;;
        "freebsd")
            end=1
            pkgs=("${pkg_pkgs[@]}")
            pkgman="pkg install"
            pm="pkg"
            serviceman="service docker start"
            serviceman2="service docker enable"
            ;;
        "openbsd")
            end=1
            pkgs=("${pkg_add_pkgs[@]}")
            pkgman="pkg_add"
            pm="pkg_info"
            serviceman="rcctl set docker on"
            serviceman2="rcctl enable docker"
            ;;
        "darwin")
            end=1
            pkgs=("${brew_pkgs[@]}")
            pkgman="brew install"
            pm="homebrew"
            serviceman="TODO" # TODO
            serviceman2="TODO" # TODO
            ;;
         *)
            end=0
            pkgs=("${sip_pkgs[@]}")
            pkgman="sip add"
            pm="sip"
    esac

    if [[ -n $pkgmnr ]]; then
        pm=$pkgmnr
        case $pm in
            "apk")
                end=1
                pkgs=("${apk_pkgs[@]}")
                pkgman="apk add"
                ;;
            "pacman")
                end=1
                pkgs=("${pacman_pkgs[@]}")
                pkgman="pacman -Sy --noconfirm"
                ;;
            "xbps")
                end=1
                pkgs=("${xbps_pkgs[@]}")
                pkgman="xbps-install -Sy"
                ;;
            "apt-get")
                end=1
                pkgs=("${apt_pkgs[@]}")
                pkgman="apt-get install -y"
                ;;
            "dnf")
                end=1
                pkgs=("${dnf_pkgs[@]}")
                pkgman="dnf install"
                ;;
            "zypper")
                end=1
                pkgs=($"${zypper_pkgs[@]}")
                pkgman="zypper -n install"
                ;;
            "pkg")
                end=1
                pkgs=("${pkg_pkgs[@]}")
                pkgman="pkg install"
                ;;
            "pkg_info")
                end=1
                pkgs=("${pkg_add_pkgs[@]}")
                pkgman="pkg_info"
                ;;
            "homebrew"|"brew")
                end=1
                pkgs=("${brew_pkgs[@]}")
                pkgman="brew install"
                ;;
        esac
    fi

    if [[ -n $initsystem ]]; then
        case $initsystem in
            "openrc")
                serviceman="rc-update add docker default"
                start="rc-service docker start"
                ;;
            "runit")
                serviceman="rc-update add docker default"
                start="rc-service docker start"
                ;;
            "s6")
                serviceman="ln -s /etc/s6/docker /service/docker"
                ;;
            "systemd")
                serviceman="service enable docker"
                start="service start docker"
                ;;
        esac
    fi
    local middle
    local last
    local uv
    (( middle = end + 1 ))
    (( last = end + 2 ))
    (( uv = end + 3 ))
    if [[ $1 == 0 ]]; then
        for ((i=0; i<=1; i++)); do
            echo "Installing ${pkgs[i]}..."
            $pkgman "${pkgs[i]}"
        done
    elif [[ $1 == 1 ]]; then
        echo "Installing ${pkgs[$middle]}..."
        $pkgman "${pkgs[$middle]}"
    elif [[ $1 == 2 ]]; then
        echo "Installing ${pkgs[$last]}..."
        $pkgman "${pkgs[$last]}"
    elif [[ $1 == 3 ]]; then
        case $pm in
            "apk"|"pacman"|"xbps"|"dnf"|"homebrew")
                echo "Installing ${pkgs[$uv]}..."
                $pkgman "${pkgs[$uv]}"
                ;;
            *)
                # These are package managers without the uv package.
                install_uv_via_script "${2}"
                ;;
        esac
        uv --version # Check installed version after install.
        sleep 3
    fi
    clear
}

download_uredis_latest() {
    echo "Downloading latest uRedis release..."
    curl -sSf $latest_release > "$(basename $latest_release)"
    sha256cksm "$(basename $latest_release)"
}

install_uv_via_script() {
    # This is a fallback, generally prefer to install uv
    # with the system's package manager.
    echo "Installing uv via script..."
    case $os in
        "slax")
            curl -LsSf https://astral.sh/uv/install.sh | bash
            ;;
        "freebsd"|"openbsd")
            curl -LsSf https://astral.sh/uv/install.sh | doas -u "${1}" bash
            ;;
        *)
            curl -LsSf https://astral.sh/uv/install.sh | sudo -u "${1}" bash
            ;;
    esac
    export PATH=$PATH:/home/$1/.local/bin
}

install_uredis_system() {
    echo "Installing uRedis on system..."
    mkdir -p "${install_dir}"
    mv "$(basename $latest_release)" "${install_dir}"
    cd "${install_dir}" || exit 1
    unzip -qq -o "${install_dir}/$(basename $latest_release)"
    rm -f "${install_dir}/$(basename $latest_release)"
    chown -R "${1}":"${2}" "${install_dir}"
}

install_uredis_service() {
    echo "Installing uRedis as service..."
    mkdir -p $install_dir
    cd uredis || exit 1
    mv "$(basename $latest_release)" "${install_dir}"
    cd "${install_dir}" || exit 1
    unzip -qq -o "${install_dir}/$(basename $latest_release)"
    rm -f "${install_dir}/$(basename $latest_release)"
    cd ..
    local _os
    _os=$os # Backup detected/set os.
    if [[ -n $initsystem ]]; then
        case $initsystem in
            "runit")
                os="void"
                ;;
            "s6")
                os="artix-s6"
                ;;
            "systemd")
                os="systemd"
                ;;
        esac
    fi
    case $os in
        "freebsd")
            pw useradd uredis -d /nonexistent
            curl -sSf $services/uredis_freebsd.sh > /etc/rc.d/uredis
            chmod +x /etc/rc.d/uredis
            doas -u uredis touch /usr/local/opt/uredis/uredis.pid
            chown -R uredis:uredis $install_dir
            service uredis onestart
            service uredis enable
            ;;
        "openbsd")
            useradd uredis
            curl -sSf $services/uredis_openbsd.sh > /etc/rc.d/uredis
            chmod +x /etc/rc.d/uredis
            doas -u uredis touch /usr/local/opt/uredis/uredis.pid
            chown -R uredis:uredis $install_dir
            rcctl set uredis user uredis
            rcctl start uredis
            rcctl enable uredis
            ;;
        "alpine"|"artix-openrc")
            if [[ $os == "alpine" ]]; then
                adduser -H uredis
            else
                useradd -M uredis
            fi
            curl -sSf $services/uredis_openrc.sh > /etc/init.d/uredis
            chmod +x /etc/init.d/uredis
            chown -R uredis:uredis $install_dir
            rc-update add uredis default
            rc-service uredis start
            ;;
        "void"|"artix-runit")
            useradd -M uredis
            mkdir -p /etc/sv/uredis
            curl -sSf $services/uredis_run_runit.sh > /etc/sv/uredis/run
            chmod +x /etc/sv/uredis/run
            chown -R uredis:uredis $install_dir
            ln -sf /etc/sv/uredis /var/service/
            sv up uredis
            ;;
        "artix-s6")
            usermod -M uredis
            mkdir -p /etc/s6/uredis
            curl -sSf $services/uredis_run_s6.sh > /etc/s6/uredis/run
            chmod +x /etc/s6/uredis/run
            chown -R uredis:uredis $install_dir
            ln -s /etc/s6/uredis /service/uredis
            ;;
        *) # Any Linux distro using SystemD
            echo "Installing for SystemD..."
            useradd -M uredis
            curl -sSf $services/uredis_systemd.sh > /etc/systemd/uredis.service
            chown -R uredis:uredis $install_dir
            systemctl enable uredis
            systemctl start uredis
            systemctl daemon-reload
            ;;
    esac
    os=$_os # Reset OS value.
    rm -rf "/home/${1}/uredis"
}

create_server_wrapper() {
    local exedir
    exedir="/usr/local/bin"
    case $os in
        "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
            exedir="/usr/bin"
            ;;
    esac
    echo "#!/bin/sh" > $exedir/uredis-server
    if (( opt_deps == 1 )); then
        echo "export PYTHONPATH=${install_dir}/dependencies" >> $exedir/uredis-server
    fi
    echo "$python ${install_dir}/uredis-server.pyz \$@" >> $exedir/uredis-server
    chmod +x $exedir/uredis-server
}

create_client_wrapper() {
    local exedir
    exedir="/usr/local/bin"
    case $os in
        "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
            exedir="/usr/bin"
            ;;
    esac
    echo "#!/bin/sh" > $exedir/uredis-client
    echo "$python ${install_dir}/uredis-client.pyz \$@" >> $exedir/uredis-client
    chmod +x $exedir/uredis-client
}

setup_docker() {
    if [[ $os == "alpine" ]]; then
        addgroup "${1}" docker
    else
        usermod -aG docker "${1}"
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
    {
    echo "#!/usr/bin/env bash"
    echo "docker network create ${1}_network"
    echo "docker run --rm --network ${1}_network --name uredis_${1} -h uredis -v \$(pwd):/opt/uredis -d uredis_img"
    echo "ipaddress=\$(docker inspect --format \"{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\" uredis_${1})"
    echo "echo \"APP_NETWORK=${1}_network\" > ../.env"
    echo "echo \"${1^^}_REDIS_HOST=\$ipaddress\" >> ../.env"
    echo "echo \"${1^^}_REDIS_PORT=6379\" >> ../.env"
    } > run_uredis_container.sh
    chown "${2}:${2}" run_uredis_container.sh
    chmod +x run_uredis_container.sh
}

build_uredis_image_docker() {
    clear
    echo "Building uRedis image (uredis-img) for Docker..."
    curl -sSf "${dockerfile}" > "$(basename $dockerfile)"
    rm -f "$(basename $latest_release)"
    if [[ -f "uredis-server.pyz" ]] && [[ -f "uredis-client.pyz" ]]; then
        docker build -t uredis_img .
    else
        echo "Could not build Docker image as 1 or more PYZ files do not exist!"
        exit 1
    fi
}

main() {
    # Check the SHA256 checksum for this script itself.
    script_cksm
    start_prompt
    detect_os
    update_packages 0
    install_packages 0
    setup_stage
}

# !TODO This will be activated with --os <os> switch.
# !TODO This will be activated with --pkgmnr <pkgmnr> switch.
# !TODO This will be activated with --initsystem <initsystem> switch.
: <<'END_COMMENT'
main_set_os_pkgmnr_and_initsystem() {
    script_cksm
    if [[ -n $1 ]]; then
        os=$1
        os_name=${os^}
        echo "Operating system is set as $os_name."
    fi
    if [[ -n $2 ]]; then
        pkgmr=$2
        echo "Package manager is set as $pkgmnr."
    fi
    if [[ -n $3 ]]; then
        initsystem=$3
        echo "Init system is set as $initsystem."
    fi
    sleep 5
    clear
    start_prompt
    detect_is_slax
    update_packages 0
    install_packages 0
    setup_stage
}
END_COMMENT

install_opt_dependencies_prompt() {
    local optdeps
    read -r -p "Install optional dependencies to support INFO command (N/y): " optdeps < /dev/tty
    if [[ -z $optdeps ]] || [[ ${optdeps,,} == "n" ]]; then
        if [[ $3 == "docker" ]]; then
            unzip -qq -o "$(basename $latest_release)" # Extract zip.
        fi
        return # Do not install optional dependencies.
    fi
    opt_deps=1
    if [[ $3 == "docker" ]]; then
        # Extract zip.
        unzip -qq -o "$(basename $latest_release)"
    fi
    # Install uv (if necessary).
    case $os in
        "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
            # uv is always installed on OpenSUSE regardless of opt dependencies.
            ;;
         *)
            install_packages 3 "${1}"
            uv python install
            ;;
    esac
    # Install optional dependencies with uv.
    curl -sSf "${requirements_txt}" > "$(basename $requirements_txt)"
    chown "${1}":"${2}" "$(basename $requirements_txt)"
    mkdir -p dependencies
    uv pip install -r "$(basename $requirements_txt)" --target dependencies
}

setup_stage() {
    clear
    print_uredis_logo
    mkdir -p uredis
    cd uredis || exit 1
    download_uredis_latest
    local install
    local user
    local group
    read -r -p "Install uRedis on system or on Docker [SYSTEM/docker/service]? " install < /dev/tty
    if [[ -z $install ]] || [[ ${install,,} == 'system' ]]; then
        read -r -p "Enter installation dir [$install_dir]: " install_dir < /dev/tty
        if [[ -z $install_dir ]]; then
            install_dir="/opt/uredis"
            if [[ $os == "freebsd" ]] || [[ $os == "openbsd" ]]; then
                install_dir="/usr/local/opt/uredis"
            fi
        fi
        while [[ -z $user ]]; do
            read -r -p "Enter user who should own installation dir: " user < /dev/tty
        done
        case $os in
            "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
                group="users"
                install_packages 3 "${user}"
                uv python install
                python="uv run python"
                ;;
            *)
                group=$user
                ;;
        esac
        install_packages 1
        install_uredis_system "${user}" "${group}"
        install_opt_dependencies_prompt "${user}" "${group}" "system"
        create_server_wrapper
        create_client_wrapper
        print_uredis_logo
        echo "Done."
        echo
        echo "ATTENTION:"
        echo "If uv (installed via script) is being used to run the applications,"
        echo "You may need to refresh the shell first."
        echo
        echo "Run uRedis server with: \"uredis-server\""
        echo "Run uRedis client with: \"uredis-client\""
        rm -rf "/home/${user}/uredis"
    elif [[ ${install,,} == 'docker' ]]; then
        while [[ -z $user ]]; do
            read -r -p "Enter user who should run the Docker service: " user < /dev/tty
        done
        case $os in
            "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
                group="users"
                ;;
            *)
                group=$user
                ;;
        esac
        chown -R "${user}:${user}" "$(pwd)"
        local appname="default"
        read -r -p "Enter name for app which will use this instance? [$appname]: " appname < /dev/tty
        if [[ -z $appname ]]; then
            appname="default"
        fi
        install_packages 2
        install_opt_dependencies_prompt "${user}" "${group}" "docker"
        setup_docker "${user}"
        build_uredis_image_docker "${user}"
        generate_run_docker_shellscript "${appname}" "${user}"
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
    elif [[ ${install,,} == "service" ]]; then
        cd ..
        install_dir="/opt/uredis"
        if [[ $os == "freebsd" ]] || [[ $os == "openbsd" ]]; then
            install_dir="/usr/local/opt/uredis"
        fi
        while [[ -z $user ]]; do
            read -r -p "Enter user for temp directory: " user < /dev/tty
        done
        case $os in
            "sles"|"sled"|"opensuse-tumbleweed"|"opensuse-leap")
                group="users"
                install_packages 3 "${user}"
                uv python install
                python="uv run python"
                ;;
            *)
                group=$user
                ;;
        esac
        install_packages 1
        install_uredis_service "${user}" "${group}"
        install_opt_dependencies_prompt "${user}" "${group}" "service"
        create_server_wrapper
        create_client_wrapper
        print_uredis_logo
        echo "Done."
        echo
        echo "uRedis has been installed as a service on $os_name."
        echo "It has been configured to run now and on system startup."
    else
        setup_stage
    fi
    echo
    echo
    write_slax_iso_or_to_modules
    rm -f "/home/${user}/logo.txt"
    rm -f "${install_dir}/logo.txt"
    exit 0
}

main
