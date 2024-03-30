import os
import json
import pandas as pd
import subprocess as sp

from model_event import EventInfo

class EventConverter(object):
    def __init__(self, config):
        self.master = config.master

        with open(self.master.infile) as f:
            meta = json.load(f)

        self.eventInfoList = [EventInfo(eventInfo["index"], eventInfo["eventInfo"], eventInfo["picksInfo"], "json") for eventInfo in meta]

    def convertFromJson(self):
        for eventInfo in self.eventInfoList:
            eventInfo.toWinpick(self.master.windir, self.master.stntbl)

class WINLocator(object):
    def __init__(self, eventConverter, config):
        self.master = config.master
        self.eventInfoList0 = eventConverter.eventInfoList

        self.file = [[eventInfo.event_index, eventInfo.winpickFname] for eventInfo in self.eventInfoList0]
        self.prmfile = config.prmfile
        
    def __locateOne(self, baseFname):
        com = "win" \
            + ' -x %s' % baseFname \
            + ' -p %s' % self.prmfile
        print("[WINLocator.locate]:", com)

        ## needs win ##
        proc = sp.run(com, shell=True, stdout = sp.PIPE, stderr = sp.STDOUT) #be careful for shell injection!!
        out = proc.stdout.decode("utf8")
        print("[WINLocator.locate]: win", out)

    def locate(self):
        for onefile in self.file:
            fname = onefile[1]
            baseFname = os.path.basename(fname)
            self. __locateOne(baseFname)

    def convert2dict(self, n):
        # make EventInfo instance
        self.eventInfoList = []
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
                self.eventInfoList.append(EventInfo(i, event, picks, "win"))
        
    def convert2json(self, n):
        # write json
        meta = [eventInfo.toJson() for eventInfo in self.eventInfoList]
        outfile = os.path.join(self.master.outdir, "picks_located.json")

        with open(outfile, 'w') as f:
            json.dump(meta, f, indent=2)

    def convert2csv(self, format, n):
        # load json
        meta = [eventInfo.toJson() for eventInfo in self.eventInfoList]

        data = []
        data += [[event['index'], event['eventInfo']['timestamp'], event['eventInfo']['lat'], event['eventInfo']['lon'], event['eventInfo']['dep'], event['eventInfo']['mag']] for event in meta]

        df = pd.DataFrame(data, columns=['index', 'timestamp', 'lat', 'lon', 'dep', 'mag']).set_index('index')

        # write
        if format == "csv":
            outfile = os.path.join(self.master.outdir, "picks_located.csv")
            df.to_csv(outfile, sep=",", header=True, index=True)
        elif format == "txt":
            outfile = os.path.join(self.master.outdir, "picks_located.txt")
            df.to_csv(outfile, sep=" ", header=False, index=False)