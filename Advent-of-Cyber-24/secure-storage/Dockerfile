FROM ubuntu:22.04
EXPOSE 1337

RUN apt update && \
    # Install standard and minimal Ubuntu packages
    apt install -y ubuntu-standard && \
    # Install additional packages you might expect in a desktop environment
    apt install -y socat gcc make bash nano kmod procps net-tools iputils-ping curl wget vim \
                   linux-headers-$(uname -r) libcap2-bin && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /root
COPY secureStorage /root/secureStorage 
COPY flag.txt /root/user.txt
COPY libc.so.6 /root/libc.so.6
COPY ld-linux-x86-64.so.2 /root/ld-linux-x86-64.so.2

RUN chmod +x /root/secureStorage
RUN chmod +x /root/libc.so.6
RUN chmod +x /root/ld-linux-x86-64.so.2


ENTRYPOINT ["socat", "tcp-l:1337,reuseaddr,fork", "EXEC:/root/secureStorage"]
