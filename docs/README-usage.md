# WINLocator
Detailed usage for WINLocator

## What is the output?
* hypocenter location result file: `data/win/yymmdd.hhmmss-xxx`
  * format: win pickfile format <br>
    For the detailed information, see https://wwweic.eri.u-tokyo.ac.jp/WIN/man.en/pickfile.html 

## How to use
### 1. Input file preparation
* output file of REALAssociator (associated_picks.json)
  * format: json format <br>
    For the detailed information, see [REALAssociator](https://github.com/rintr-suzuki/REALAssociator).
  * Put the files at any directory. <br>
    You can change the path with `--infile` option.

* channel table: correspondence Table of stations and their code
  * format: txt format <br>
    For the detailed information, see https://wwweic.eri.u-tokyo.ac.jp/WIN/man.ja/win.html (only in Japanese).
  * **Only support the following "component code (column [5])"**. <br>
    -Vertical compornent: EW,E,X,VX <br>
    -Horizontal compornent 1: NS,N,Y,VY <br>
    -Horizontal compornent 2: UD,U,Z,VZ
  * **"Voltage amplification ratio (column [12])" is modified to the int value.**
  * NIED provides channel table at the same time when downloading WIN waveform files. <br>
    For the detailed information, see https://hinetwww11.bosai.go.jp/auth/download/cont/?LANG=en
  * Put the file as `WINLocator/etc/stn.tbl`. <br>
    You can change the path with `--chtbl` option.

* velocity structure table
  * format: txt format <br>
    For the detailed information, see "[6]" in [here](https://wwweic.eri.u-tokyo.ac.jp/WIN/man.ja/win.html) (only in Japanese).
  * You can use `WINLocator/etc/struct.tbl` by Hasegawa et al. (1978) as a default.
  * You can change the path with `--velfile` option.

### 2. Configuration of WINLocator
* Set the following options at least.

  | Option | Description |
  | --- | --- |
  | `[--infile INFILE]` | path of input associated-picks json file |

* Use `-h` option for the detailed information of all other options.

### 3. Execute WINLocator
```
# Pull docker image (only once), run the 'hypomh' container and then execute WINLocator on the container environment. *1
# Stop and delete the container environment after execution is complete.
$ ./WINLocator.bash --infile INFILE
# e.g. 
# $ ./WINLocator.bash --infile data/associated_picks.json

# You can find the output of WINLocator in '<dirname of infile>' directory.
```

## Notes
* *1 docker image is built from the following Dockerfile.
    * dockerfiles/base/Dockerfile