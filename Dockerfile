# Dockerfile to run uRedis server.
FROM alpine:latest

# Install required packages, tzdata and python3.
RUN sed -i '2s/^# *//' /etc/apk/repositories
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

# Copy uredis-client PYZ to container.
COPY uredis-client.pyz ./

# Copy README to container.
COPY README.md ./

# Copy version.txt to container.
COPY version.txt ./

# Create executable wrapper for server.
RUN echo "#!/bin/sh" > /usr/local/bin/uredis-server
RUN echo "python3 /opt/uredis/uredis-server.pyz \$@" >> /usr/local/bin/uredis-server
RUN chmod +x /usr/local/bin/uredis-server

# Create executable wrapper for client.
RUN echo "#!/bin/sh" > /usr/local/bin/uredis-client
RUN echo "python3 /opt/uredis/uredis-client.pyz \$@" >> /usr/local/bin/uredis-client
RUN chmod +x /usr/local/bin/uredis-client

# Test uredis-server installed.
RUN /usr/local/bin/uredis-server --version

# Test uredis-client installed.
RUN /usr/local/bin/uredis-client --version

# Run μredis server, binding to 0.0.0.0, writing all changes to disk
# and limiting that DB file to a size of 15GB (15,000,000,000 bytes).
CMD [ "/usr/local/bin/uredis-server", "--bind", "0.0.0.0", "--max-db", "15G, "--update-disk" ]
