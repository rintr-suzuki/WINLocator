# WINLocator
Tips of this tool

## Use DEBUG mode
You can use DEBUG mode for WINLocator.bash to enter in the docker container.
Set "DEBUG" for the first argument and execute the bash file as the following.
```
$ ./WINLocator.bash DEBUG
```

## Build image with win32tools
You can build docker image with "win32tools" by NIED to treat WIN32 waveform data in a container environment.

Download "win32tools" from [here](https://hinetwww11.bosai.go.jp/auth/manual/?LANG=en), put the file as `WINLocator/dockerfiles/win32tools/win32tools.tar.gz` <br> 
and run WINLocator.bash with DEBUG mode.
WINLocator.bash automatically build docker image with "win32tools" and run container with the image. (Dockerfile: dockerfiles/win32tools/Dockerfile)

Note that "win32tools" is NOT needed in the hypocenter location process by WINLocator.
