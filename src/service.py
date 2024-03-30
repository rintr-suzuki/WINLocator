import os
import json
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
        self.eventInfoList = eventConverter.eventInfoList

        self.file = [[eventInfo.event_index, eventInfo.winpickFname] for eventInfo in self.eventInfoList]
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

    def convert2json(self, n):
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
                    if j <= 4:
                        event.append(win.split())
                    else:
                        picks.append(win.split())
                    j += 1
            else:
                # add standard deviation of picks to event info
                event.append(picks[-1])
                picks.pop()

            # convert to json format
            eventInfoList.append(EventInfo(i, event, picks, "win"))

        # write json
        meta = [eventInfo.toJson() for eventInfo in eventInfoList]
        outfile = os.path.join(self.master.outdir, "picks_located.json")

        with open(outfile, 'w') as f:
            json.dump(meta, f, indent=2)