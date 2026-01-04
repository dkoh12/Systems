FROM flink:latest

# Install PyFlink
# We need to ensure python3 and pip are available and up to date
# We also need a full JDK (not just JRE) for pemja to build
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev netcat-openbsd default-jdk && \
    ln -s /usr/bin/python3 /usr/bin/python

# Set JAVA_HOME to the default java location (usually a symlink)
ENV JAVA_HOME=/usr/lib/jvm/default-java

# Install Apache Flink Python library
RUN pip3 install --default-timeout=1000 apache-flink
