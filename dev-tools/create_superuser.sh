#!/bin/bash

# This script creates a superuser for the cms with the username "root" and an empty email-field.
# It uses the settings for the postgres docker container and cannot be used with a standalone installation of postgres.

if nc -w1 localhost 5432; then

    # Check if script is running as root
    if [ $(id -u) = 0 ]; then
        # Check if script was invoked by the root user or with sudo
        if [ -z "$SUDO_USER" ]; then
            echo "Please do not execute createsuperuser.sh as your root user." >&2
            exit 1
        else
            # Call this script again as the user who executed sudo
            sudo -u $SUDO_USER $0
            # Exit with code of subprocess
            exit $?
        fi
    fi

    cd $(dirname "$BASH_SOURCE")
    source ../.venv/bin/activate

    integreat-cms createsuperuser

else

    # Check if docker is not installed
    if ! command -v docker > /dev/null; then
        echo "In order to run the database, you need either a local postgres server or docker." >&2
        exit 1
    fi

    # Check if script is not running as root
    if ! [ $(id -u) = 0 ]; then
        echo "This script needs root privileges to connect to the docker deamon. It will be automatically restarted with sudo." >&2
        # Call this script again as root
        sudo $0
        # Exit with code of subprocess
        exit $?
    elif [ -z "$SUDO_USER" ]; then
        echo "Please do not run this script as your root user, use sudo instead." >&2
        exit 1
    fi

    # Check if docker socket is not available
    if ! docker ps > /dev/null; then
        exit 1
    fi

    cd $(dirname "$BASH_SOURCE")
    source ../.venv/bin/activate

    # Check if postgres database container is already running
    if [ "$(docker ps -q -f name=integreat_django_postgres)" ]; then
        sudo -u $SUDO_USER integreat-cms createsuperuser --settings=backend.docker_settings
    else
        # Check if stopped container is available
        if [ "$(docker ps -aq -f status=exited -f name=integreat_django_postgres)" ]; then
            # Start the existing container
            docker start integreat_django_postgres > /dev/null
            until docker exec -it integreat_django_postgres psql -U integreat -d integreat -c "select 1" > /dev/null 2>&1; do
              sleep 0.1
            done
        else
            # Run new container
            docker run -d --name "integreat_django_postgres" -e "POSTGRES_USER=integreat" -e "POSTGRES_PASSWORD=password" -e "POSTGRES_DB=integreat" -v "$(pwd)/../.postgres:/var/lib/postgresql" -p 5433:5432 postgres > /dev/null
            echo -n "Waiting for postgres database container to be ready..."
            until docker exec -it integreat_django_postgres psql -U integreat -d integreat -c "select 1" > /dev/null 2>&1; do
              sleep 0.1
              echo -n "."
            done
            echo ""
        fi
        sudo -u $SUDO_USER integreat-cms createsuperuser --settings=backend.docker_settings
        # Stop the postgres database docker container
        docker stop integreat_django_postgres > /dev/null
    fi

fi
