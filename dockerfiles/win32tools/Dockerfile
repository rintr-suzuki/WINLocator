FROM hypomh:v1.1-base

# install win32tool
WORKDIR /usr/local/src/
COPY win32tools.tar.gz /usr/local/src/
RUN tar xzfv win32tools.tar.gz -C /usr/local/src
WORKDIR /usr/local/src/win32tools/
RUN make clean
RUN make all 
RUN make install

WORKDIR /data/hypomh

# See here for the detailed infomation.
# https://hinetwww11.bosai.go.jp/auth/manual/?LANG=en