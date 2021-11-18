import os
import json
import glob
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
            eventInfo.toWinpick(self.master.outdir, self.master.stntbl)
        self.files = glob.glob(os.path.join(self.master.outdir, '*'))

class WINLocator(object):
    def __init__(self, eventConverter, config):
        self.files = eventConverter.files
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
        for fname in self.files:
            baseFname = os.path.basename(fname)
            self. __locateOne(baseFname)

    # def convert2json(self, n):
    #     # winファイルを順にwith文で読み込んで、行を一要素としたリストとして、event, picksに格納していく
    #     # それ以上の操作はmodel_event.pyで行う

    #     # make EventInfo instance
    #     eventInfoList = []
    #     for i, winrawfile in enumerate(self.files):
    #         # read txt
    #         with open(events_rawfile) as f:
    #             events_meta = [line.rstrip().lstrip() for line in f.readlines()]

    #         i = 1; picks_meta = []; picks_onemeta = []
    #         with open(picks_rawfile) as f:
    #             for pick_meta in f:
    #                 pick_meta = pick_meta.rstrip().lstrip()
    #                 if pick_meta in events_meta:
    #                     # if line is event info
    #                     if len(picks_onemeta) != 0:
    #                         # if previous event has one or more picks
    #                         picks_meta.append(picks_onemeta)
    #                         i += 1
    #                     picks_onemeta = []
    #                 else:
    #                     # if line is pick info
    #                     picks_onemeta.append(pick_meta)
    #             else:
    #                 # if line is end
    #                 if len(picks_onemeta) != 0:
    #                     # if last event has one or more picks
    #                     picks_meta.append(picks_onemeta)

    #         eventInfoList.append(EventInfo(i+1, event, picks, "win"))

    #     # write json
    #     meta = [eventInfo.toJson() for eventInfo in eventInfoList]
    #     outfile = os.path.join(self.outdir, "picks_located.json") # outdirはwindirと分けないといけない(master.pyなどを修正する必要あり)

    #     with open(outfile, 'w') as f:
    #         json.dump(meta, f, indent=2)