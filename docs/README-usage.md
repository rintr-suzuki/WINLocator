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

* The final result is filtered with the threshold for the event.
  * Default filtering rule is as the following: <br>
    (1) Sum of the number of P- and S-phases at 20 stations near the epicenter: 5 or more (`--pspicknear`, `--nearstn`) <br>
    (2)-1 Number of stations from which both the P- and S-phases are selected: 2 or more (`--bothps`) <br>
    (2)-2 Number of stations from which at least the P-phases are selected: 10 or more (`--ppick`) <br>
    (3) Root mean square of the P-wave travel time residuals: less than 0.9 sec (`--std_ditp`) <br>
    (4) Root mean square of the S-wave travel time residuals: less than 1.4 sec (`--std_dits`) <br>
    (5)-1 Latitude error: less than 17 km (`--dolat`) <br>
    (5)-2 Longitude error: less than 17 km (`--dolon`) <br>
  * The defaults are from Tamaribuchi et al., 2021, but (3) and (4) are empirically tuned. <br> (Originally, `--std_ditp`=0.6 and `--std_dits`=1.2)

* Also, `--rm_duplicate` option can exclude events that occurred almost simultaneously (default: within 1 second difference in origin time) and at the same location (default: within 0.15 degree difference in latitude and longitude of epicenter), leaving only the single event with the highest number of assosiated picks on the event. <br>
This option is useful for removing erroneously divided into two or more events during association.

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
  | `[--mkEachJson]` | if set, output the results of each iteration to files (default: False) |
  | `[--rm_duplicate]` | if set, delete split events due to miss association (default: False) |

* Use `-h` option for the detailed information of all other options.

### 3. Execute WINLocator
```
# Pull docker image (only once), run the 'hypomh' container and then execute WINLocator on the container environment. *1
# Stop and delete the container environment after execution is complete.
$ ./WINLocator.bash --infile INFILE [--format FORMAT] [--res RES] [--itr_hypo ITR_HYPO] [--mkEachJson] [--rm_duplicate]
# e.g. 
# $ ./WINLocator.bash --infile data/associated_picks.json --format txt,json --rm_duplicate

# You can find the output of WINLocator in '<dirname of infile>' directory.
```

## Notes
* *1 docker image is built from the following Dockerfile.
    * dockerfiles/base/Dockerfile