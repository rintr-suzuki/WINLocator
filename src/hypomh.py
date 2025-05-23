import argparse

from master import MasterConfig, MasterProcess, Config
from service import EventConverter, WINLocator

def tp2(arg):
    parts = arg.split(',')
    result = []
    for part in parts:
        values = list(map(int, part.split('-')))
        result.append(values)

    if len(result) <= 1:
        result = result[0]
    return result

def read_args():
    tp1 = lambda x:x.split(',')
    parser = argparse.ArgumentParser()

    # dir information
    parser.add_argument('--infile', help='path of input associated-picks json file')

    parser.add_argument('--outdir', help='path of output directory (default: dirname of infile)')
    parser.add_argument('--format', type=tp1, default=['csv'], help='output format, multiple specifications separated by commas (default: csv)')
    parser.add_argument('--mkEachJson', action='store_true', help='if set, output the results of each iteration to files (default: False)')

    # channel table of station code
    parser.add_argument('--chtbl', default='etc/stn.tbl', help='channel table')
    parser.add_argument('--velfile', default='etc/struct.tbl', help='velocity structure file')

    # param for hypo limitation
    # parser.add_argument('--min_merge', type=float, default=5, help='min_merge: default=3[sec]')
    parser.add_argument('--res', type=tp2, default=[[5, 10], [1, 2]], help='(Valid for itr_hypo=2 or more) Threshold of the P,S-wave travel time residuals on relocation connected by hyphens. \
                        Picks with larger residuals than this threshold are excluded from the following iteration. \
                        It can be set for each iteration by separating them with commas. (default: 5-10,1-2)')

    # 
    parser.add_argument('--pspicknear', type=int, default=5, help='(1) sum of the number of P- and S-phases at "nearstn" stations near the epicenter: default=5')
    parser.add_argument('--nearstn', type=int, default=20, help='(1) default=20')
    parser.add_argument('--bothps', type=int, default=2, help='(2)-1 number of stations from which both the P- and S-phases are selected: default=2')
    parser.add_argument('--ppick', type=int, default=10, help='(2)-2 number of stations from which at least the P-phases are selected: default=10')
    parser.add_argument('--pspick', type=int, default=0, help='sum of the number of selected P- and S-phases: default=0')    
    parser.add_argument('--std_ditp', type=float, default=0.9, help='(3) root mean square of the P-wave travel time residuals: default=0.9[sec]')
    parser.add_argument('--std_dits', type=float, default=1.4, help='(4) root mean square of the S-wave travel time residuals: default=1.4[sec]')
    parser.add_argument('--dolat', type=float, default=17, help='(5)-1 latitude error: default=17[km]')
    parser.add_argument('--dolon', type=float, default=17, help='(5)-2 longitude error: default=17[km]')
    # parser.add_argument('--dotime', type=float, default=2, help='(6)origin time error: default=2[sec]')

    # step of hypomh
    parser.add_argument('--itr_hypo', type=int, default=3, help='Number of relocation process iterations. \
                        After 2nd relocation, remaining picks are used, excluding the picks with larger residuals than "--res" values. (default: 3)')
    
    # select event
    parser.add_argument('--rm_duplicate', action='store_true', help='if set, delete split events due to miss association (default: False)')
    parser.add_argument('--dupotime', type=float, default=1.0, help='time residuals of origin time to define split events: default=1.0[sec]')
    parser.add_argument('--dupolat', type=float, default=0.15, help='latitude residuals to define split events: default=0.15[deg]')
    parser.add_argument('--dupolon', type=float, default=0.15, help='longitude residuals to define split events: default=0.15[deg]')    
    
    # # multi-thread processing
    # parser.add_argument('--thread', type=int, help='number of thread (default: multiprocessing.cpu_count()*0.6)')

    args = parser.parse_args()
    return args

def main(params):
    # initial settings
    ## master setting
    masterConfig = MasterConfig(params)
    masterProcess = MasterProcess(masterConfig)

    # init
    # masterConfig.itr_hypo = 1 # todo
    eventConverter = EventConverter(masterConfig)
    winLocator = WINLocator(masterConfig)

    # remove old file
    masterProcess.rm_old()

    for n in range(masterConfig.itr_hypo):
        config = Config(masterConfig, n)

        # json->txt
        eventConverter.convertFromJson(config, winLocator)

        # txt->win->txt
        winLocator.locate(config, eventConverter)

        # txt->json
        winLocator.convert2json(config)

    # remove tmp file
    masterProcess.rm_tmp()

if __name__ == '__main__':
   params = vars(read_args()) # convert to dict
   main(params)