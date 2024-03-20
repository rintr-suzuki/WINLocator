#!/bin/bash

## def names
image_name='hypomh'; tag_name='v1.1-base'
container_name='hypomh-1'
app_name='python3 src/hypomh.py'

win32tooltar="dockerfiles/win32tools/win32tools.tar.gz"

## check OS
OSname="Mac-Linux"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OSname="Windows"
fi

## set config
docker_head="sudo"; docker_head_images="sudo"
workdir=`pwd`; arg_head=""

if [[ $OSname == "Windows" ]]; then
    docker_head="winpty"; docker_head_images=""
    workdir=/`pwd`; arg_head="/"
fi

## read args
volume="-v $workdir:$workdir"
for arg in ${@//=/ }; do
    if [[ $arg == *"/"* ]]; then
        arg="$arg_head$(cd -- "$(dirname -- "$arg")" && pwd)" || exit $? # convert to absolute dirname
        volume+=" -v $arg:$arg"
    fi
done

args=$@

## pull image
if ! $docker_head_images docker images --format '{{.Repository}}:{{.Tag}}' | grep -q -x "$image_name:$tag_name"; then
    $docker_head docker pull rintrsuzuki/$image_name:$tag_name
    $docker_head docker tag rintrsuzuki/$image_name:$tag_name $image_name:$tag_name
    $docker_head docker rmi rintrsuzuki/$image_name:$tag_name
fi

## build image with win32tools if tar exists
if [ -e $win32tooltar ]; then
    tag_name=${tag_name//-base/}
    if ! $docker_head_images docker images --format '{{.Repository}}:{{.Tag}}' | grep -q -x "$image_name:$tag_name"; then
        $docker_head docker build -t $image_name:$tag_name -f dockerfiles/win32tools/Dockerfile dockerfiles/win32tools
    fi
fi

### stop old container if exists
if $docker_head_images docker ps --format '{{.Names}}' | grep -q -x "$container_name"; then
    $docker_head docker stop $container_name
fi

## run container
$docker_head docker run -itd --rm \
$volume \
--name $container_name \
$image_name:$tag_name

if [[ $1 == "DEBUG" ]]; then
    ### attach container as DEBUG mode
    $docker_head docker exec -it -w $workdir $container_name bash

else
    ### exec app
    $docker_head docker exec -it -w $workdir $container_name $app_name $args

    ### stop container
    $docker_head docker stop $container_name
fi