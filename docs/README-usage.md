# WINLocator
Detailed usage for WINLocator

## What is the output?
* hypocenter location result file (win pickfile): `data/win/yymmdd.hhmmss-xxx`
  * format: win pickfile format <br>
    For the detailed information, see https://wwweic.eri.u-tokyo.ac.jp/WIN/man.en/pickfile.html.

* hypocenter location result file (csv, json, txt): `data/picks_located.xxx`
  * format: csv, json or txt format <br>
    Event and pick information from "win pickfile".
  * Csv and txt format has the minimum information to identify the hypocenter, while json format has all of "win pickfile" information, including pick information.
  * You can choose one or more format to output with `--format` option (default: csv only).

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
  | `--infile INFILE` | path of input associated-picks json file |
  | `[--format FORMAT]` | output format, multiple specifications separated by commas (default: csv) |
  | `[--res RES]` | (Valid for itr_hypo=2 or more) Threshold of the P,S-wave travel time residuals on relocation connected by hyphens. <br> Picks with larger residuals than this threshold are excluded from the following iteration. <br> It can be set for each iteration by separating them with commas. (default: 5-10,1-2) |
  | `[--itr_hypo ITR_HYPO]` | Number of relocation process iterations. <br> After 2nd relocation, remaining picks are used, excluding the picks with larger residuals than "--res" values. (default: 3) |

* Use `-h` option for the detailed information of all other options.

### 3. Execute WINLocator
```
# Pull docker image (only once), run the 'hypomh' container and then execute WINLocator on the container environment. *1
# Stop and delete the container environment after execution is complete.
$ ./WINLocator.bash --infile INFILE [--format FORMAT]
# e.g. 
# $ ./WINLocator.bash --infile data/associated_picks.json --format txt,json

# You can find the output of WINLocator in '<dirname of infile>' directory.
```

## Notes
* *1 docker image is built from the following Dockerfile.
    * dockerfiles/base/Dockerfile