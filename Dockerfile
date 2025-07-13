# Dockerfile to run μredis server.
FROM alpine:latest

# Install required packages, tzdata and python 3.
COPY apk_repositories.txt /etc/apk/repositories
RUN apk update && apk add --no-cache tzdata python3

# Set timezone for container to UTC.
# The timezone does not really matter for uredis-server though.
ENV TZ=UTC
RUN date

# Expose port for clients.
EXPOSE 6379

# Test Python installed.
RUN python3 --version

# Copy zipped μredis server application.
RUN mkdir -p /opt/uredis
WORKDIR /opt/uredis
VOLUME /opt/uredis

# Copy uredis-server PYZ to container.
COPY uredis-server.pyz ./

# Test uredis-server installed.
RUN python3 /opt/uredis/uredis-server.pyz --version

# Copy uredis-client PYZ to container.
COPY uredis-client.pyz ./

# Test uredis-client installed.
RUN python3 /opt/uredis/uredis-client.pyz --version

# Copy executable wrapper for client.
COPY uredis-client /usr/bin/
RUN chmod +x /usr/bin/uredis-client

# Run μredis server, binding to 0.0.0.0, writing all changes to disk
# and limiting that DB file to a size of 2GB (2000000000 bytes).
CMD [ "python3", "uredis-server.pyz", "--bind", "0.0.0.0", "--max-db", "2000000000", "--update-disk" ]
