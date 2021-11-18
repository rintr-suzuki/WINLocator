#image指定
FROM ubuntu:20.04

# gcc, Xなどをインストールする
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt-get update \
 && apt-get install -y wget make tk libmosquitto-dev gfortran xserver-xorg libx11-dev python3 python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# WINをインストールする
WORKDIR /usr/local/src/
RUN wget https://wwweic.eri.u-tokyo.ac.jp/WIN/pub/win/WIN_pkg-3.0.11.tar.gz
RUN tar xzfv WIN_pkg-3.0.11.tar.gz -C /usr/local/src

WORKDIR /usr/local/src/WIN_pkg-3.0.11
ENV ncpu $nproc
RUN ./configure --prefix=/usr/local/src/win
RUN make -j$ncpu
RUN make -j$ncpu install

ENV PATH $PATH:/usr/local/src/win/bin

# # python3をインストールする
WORKDIR /usr/local/src/
RUN pip3 install pandas
RUN pip3 install tqdm

WORKDIR /data/hypomh

# c.f.
# https://dandango.pw/archives/377
# https://qiita.com/tomson784/items/02d8c6e282aa865b1a87