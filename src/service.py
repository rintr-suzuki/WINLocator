import os
import json
import pandas as pd
import subprocess as sp

from model_event import EventInfo

class EventConverter(object):
    def __init__(self, config):
        self.master = config

    def convertFromJson(self, config, winLocator):
        # set config
        ## itr
        n = config.n

        ## input
        pres = self.master.res[n-1][0]
        sres = self.master.res[n-1][1]

        ## output
        # file_day = config.file_day
        out_dir = config.out_dir

        # read input
        if n-1 >= 0:
            eventInfoList0 = winLocator.eventInfoLists[n-1]
            self.eventInfoList = []
            for item in eventInfoList0:
                picksInfoNew = []
                for sub_item in item.picks:
                    if (sub_item['type'] == "p") and (abs(sub_item['residual']) <= pres):
                        picksInfoNew.append(sub_item)
                    elif (sub_item['type'] == "s") and (abs(sub_item['residual']) <= sres):
                        picksInfoNew.append(sub_item)
                self.eventInfoList.append(EventInfo(item.event_index, item.event, picksInfoNew, "json"))

        elif n-1 < 0:
            self.infile = self.master.infile
            with open(self.infile) as f:
                meta = json.load(f)

            self.eventInfoList = [EventInfo(eventInfo["index"], eventInfo["eventInfo"], eventInfo["picksInfo"], "json") for eventInfo in meta]
        
        # else:
        #     print("[INFO]: There is no event to locate")
        #     exit()

        # write picks
        for eventInfo in self.eventInfoList:
            eventInfo.toWinpick(out_dir, self.master.stntbl)

class WINLocator(object):
    def __init__(self, config):
        self.master = config
        self.outdir = self.master.outdir

        self.eventInfoLists = []
        self.meta = []
        
    def __locateOne(self, baseFname):
        com = "win" \
            + ' -x %s' % baseFname \
            + ' -p %s' % self.prmfile
        print("[WINLocator.locate]:", com)

        ## needs win ##
        proc = sp.run(com, shell=True, stdout = sp.PIPE, stderr = sp.STDOUT) #be careful for shell injection!!
        out = proc.stdout.decode("utf8")
        print("[WINLocator.locate]: win", out)

    def locate(self, config, eventConverter):
        # read input
        self.eventInfoList0 = eventConverter.eventInfoList
        self.file = [[eventInfo.event_index, eventInfo.winpickFname] for eventInfo in self.eventInfoList0]
        self.prmfile = config.prmfile

        # locate
        for onefile in self.file:
            fname = onefile[1]
            baseFname = os.path.basename(fname)
            self. __locateOne(baseFname)

    def __convert2dict(self):
        # make EventInfo instance
        eventInfoList = []
        for onefile in self.file:
            i = onefile[0] # event idx of input EventInfo
            fname = onefile[1]
            # read txt
            with open(fname) as f:
                win_meta = [line.rstrip().lstrip() for line in f.readlines()]

            j = 0; event = []; picks = []
            for win in win_meta:
                if win.startswith('#f'):
                    ## set size
                    if j <= 4:
                        if j == 0:
                            sizes = [3, 3, 3, 3, 6, 3, 8, 11, 11, 8, 6]
                        elif j == 1:
                            sizes = [3, 7, 19, 9, 11, 10]
                        elif j == 2:
                            sizes = [3, 10, 10, 10, 10, 10, 10]
                        elif j == 3:
                            sizes = [3, 19, 6, 8, 6, 8, 6]
                        elif j == 4:
                            sizes = [3, 5, 5, 4, 2, 6, 2, 4, 2, 6, 2, 4, 2, 6, 2]
                        flag = True
                    else:
                        sizes = [3, 10, 2, 9, 6, 6, 6, 7, 6, 7, 7, 6, 7, 10, 5]
                        flag = False

                    ## cut string
                    k = 0; meta = []
                    for size in sizes:
                        meta.append(win[k:k+size].rstrip().lstrip())
                        k += size
                        
                    ## append to list
                    if flag:
                        event.append(meta)
                    else:
                        picks.append(meta)

                    j += 1
            
            # if located
            if len(event) != 0:
                # add standard deviation of picks to event info
                event.append(picks[-1])
                picks.pop()

                # convert to json format
                eventInfoList.append(EventInfo(i, event, picks, "win"))
        self.eventInfoLists.append(eventInfoList)
        
    def convert2json(self, config, mkEachJson=False):
        ## itr
        n = config.n

        # convert to dict
        self.__convert2dict()

        # write json
        ## add to meta
        metaone = [eventInfo.toJson() for eventInfo in self.eventInfoLists[n]]
        self.meta.append(metaone)

        ## write output
        if mkEachJson:
            self.writeJson(n=config.n, format=self.master.format)

        self.writeJson(format=self.master.format)

    def writeJson(self, n=-1, format=['csv']):
        # select meta
        ## write each
        if n >= 0:
            outfilebase = "picks_located-%s" % n
            outmeta = self.meta[n]

        ## write final
        elif n == -1:
            outfilebase = "picks_located"
            outmeta = self.meta[-1]

        # write in each format
        if 'csv' in format:
            outfile = os.path.join(self.outdir, outfilebase + ".csv")
            
            df = self.__extractInfo(outmeta)
            df.to_csv(outfile, sep=",", header=True, index=True)

        if 'json' in format:
            outfile = os.path.join(self.outdir, outfilebase + ".json")

            with open(outfile, 'w') as f:
                json.dump(outmeta, f, indent=2)

        if 'txt' in format:
            outfile = os.path.join(self.outdir, outfilebase + ".txt")
            
            df = self.__extractInfo(outmeta)
            df.to_csv(outfile, sep=" ", header=False, index=False)

    def __extractInfo(self, meta):
        data = []
        data += [[event['index'], event['eventInfo']['timestamp'], \
                  event['eventInfo']['lat'], event['eventInfo']['dlat'], \
                  event['eventInfo']['lon'], event['eventInfo']['dlon'], \
                  event['eventInfo']['dep'], event['eventInfo']['dlat'], \
                  event['eventInfo']['mag']] for event in meta]

        df = pd.DataFrame(data, columns=['index', 'timestamp', 'lat', 'dlat', 'lon', 'dlon', 'dep', 'ddep', 'mag']).set_index('index')
        return df
