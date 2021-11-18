import argparse

from master import MasterConfig, MasterProcess, Config
from service import EventConverter, WINLocator

def read_args():
    tp1 = lambda x:list(map(float, x.split(',')))
    parser = argparse.ArgumentParser()

    # dir information
    parser.add_argument('--infile', help='path of input associated-picks json file')

    parser.add_argument('--outdir', help='path of output directory (default: dirname of infile)')

    # channel table of station code
    parser.add_argument('--chtbl', default='etc/stn.tbl', help='channel table')
    parser.add_argument('--velfile', default='etc/struct.tbl', help='velocity structure file')

    # # param for hypo limitation
    # parser.add_argument('--min_merge', type=float, default=5, help='min_merge: default=3[sec]')
    # parser.add_argument('--p_res_pick', type=tp1, default=[5, 1], help='minimum residuals of the P-wave travel time residuals: default=5(for first drop),1(for second drop and after)[sec]')
    # parser.add_argument('--s_res_pick', type=tp1, default=[10, 2], help='minimum residuals of the S-wave travel time residuals: default=10(for first drop),2(for second drop and after)[sec]')

    # # default is from Tamaribuchi et al., 2021
    # parser.add_argument('--pspicknear', type=int, default=5, help='(1)sum of the number of P- and S-phases at "nearstn" stations near the epicenter: default=5')
    # parser.add_argument('--nearstn', type=int, default=20, help='(1)default=20')
    # parser.add_argument('--bothps', type=int, default=2, help='(2)number of stations from which both the P- and S-phases are selected: default=2')
    # parser.add_argument('--ppick', type=int, default=10, help='(2)number of stations from which at least the P-phases are selected: default=10')
    # parser.add_argument('--pspick', type=int, default=0, help='sum of the number of selected P- and S-phases: default=0')    
    # parser.add_argument('--std_ditp', type=float, default=0.6, help='(3)root mean square of the P-wave travel time residuals: default=0.6[sec]')
    # parser.add_argument('--std_dits', type=float, default=1.2, help='(4)root mean square of the S-wave travel time residuals: default=1.2[sec]')
    # parser.add_argument('--dolat', type=float, default=17, help='(5)latitude error: default=17[km]')
    # parser.add_argument('--dolon', type=float, default=17, help='(5)longitude error: default=17[km]')
    # parser.add_argument('--dotime', type=float, default=2, help='(6)origin time error: default=2[sec]')

    # # step of hypomh
    parser.add_argument('--itr_hypo', type=int, default=1, help='number of relocation')
    
    # # multi-thread processing
    # parser.add_argument('--thread', type=int, help='number of thread (default: multiprocessing.cpu_count()*0.6)')

    args = parser.parse_args()
    return args

def main(params):
    # initial settings
    ## master setting
    masterConfig = MasterConfig(params)
    masterProcess = MasterProcess(masterConfig)

    masterConfig.itr_hypo = 1 # todo
    for n in range(masterConfig.itr_hypo):
        if n == 0:
            # init
            config = Config(masterConfig, n)
            eventConverter = EventConverter(config)

            # json->txt
            eventConverter.convertFromJson()
        else:
            # json->txt # todo
            eventConverter.convertFromJson(winLocator)

        winLocator = WINLocator(eventConverter, config)
        winLocator.locate()
        # winLocator.convert2json(n) # todo

    # remove tmp file
    masterProcess.rm_tmp()

if __name__ == '__main__':
   params = vars(read_args()) # convert to dict
   main(params)