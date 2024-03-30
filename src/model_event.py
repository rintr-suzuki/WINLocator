import datetime
import os

class EventInfo(object):
    def __init__(self, i, event, picks, type):
        self.event_index = i
        self.event = {}; self.picks = []
        if type == "real":
            # read
            ## event
            event = event.split()

            self.event["index"] = int(event[0])

            self.event["year"] = event[1]
            self.event["month"] = event[2]
            self.event["day"] = event[3]
            self.event["time"] = event[4]

            event_timestamp_str = self.event["year"] + self.event["month"] + self.event["day"] + " " + self.event["time"]
            event_timestamp_dt = datetime.datetime.strptime(event_timestamp_str, '%Y%m%d %H:%M:%S.%f')
            self.event["timestamp"] = event_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            self.event["otime"] = float(event[5])
            self.event["residual"] = float(event[6])

            self.event["lat"] = float(event[7])
            self.event["lon"] = float(event[8])
            self.event["dep"] = float(event[9])

            self.event["mag"] = float(event[10])
            self.event["mag_var"] = float(event[11])

            self.event["nP"] = int(event[12])
            self.event["nS"] = int(event[13])
            self.event["nPorS"] = int(event[14])
            # self.event["nPandS"] = int(event[15])

            self.event["station_gap"] = float(event[15])

            ## picks
            picks = [pick.split() for pick in picks]
            
            for rawpick in picks:
                pick = {}

                pick["net"] = rawpick[0]
                pick["id"] = rawpick[1]
                pick["type"] = rawpick[2].lower()

                pick["absolute_time"] = float(rawpick[3])
                pick["time"] = float(rawpick[4])

                pick_timestamp_dt = event_timestamp_dt + datetime.timedelta(seconds=pick["time"])
                pick["timestamp"] = pick_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

                pick["amp"] = float(rawpick[5])
                pick["residual"] = float(rawpick[6])
                pick["prob"] = float(rawpick[7]) # weight for REAL
                pick["azimuth"] = float(rawpick[8])

                self.picks.append(pick)
                
        elif type == "win": # todo
            # read
            ## event
            ### first line of #f
            self.event["year"] = event[0][1]
            self.event["month"] = event[0][2]
            self.event["day"] = event[0][3]

            self.event["hour"] = event[0][4].zfill(2)
            self.event["minute"] = event[0][5]
            self.event["second"] = event[0][6]

            event_timestamp_str = self.event["year"] + self.event["month"] + self.event["day"] + " " \
                + self.event["hour"] + self.event["minute"] + self.event["second"]
            event_timestamp_dt = datetime.datetime.strptime(event_timestamp_str, '%y%m%d %H%M%S.%f')
            self.event["timestamp"] = event_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            self.event["lat"] = float(event[0][7])
            self.event["lon"] = float(event[0][8])
            self.event["dep"] = float(event[0][9])
            self.event["mag"] = float(event[0][10])

            ### second line of #f
            self.event["diagnosis"] = event[1][1]
            # self.event["dtimestamp"] = float(event[1][2])
            self.event["dlat"] = float(event[1][3])
            self.event["dlon"] = float(event[1][4])
            self.event["ddep"] = float(event[1][5])

            ### third line of #f
            self.event["cxx"] = float(event[2][1])
            self.event["cxy"] = float(event[2][2])
            self.event["cxz"] = float(event[2][3])
            self.event["cyy"] = float(event[2][4])
            self.event["cyz"] = float(event[2][5])
            self.event["czz"] = float(event[2][6])

            ### fourth line of #f
            self.event["ilat"] = float(event[3][1])
            self.event["idlat"] = float(event[3][2])
            self.event["ilon"] = float(event[3][3])
            self.event["idlon"] = float(event[3][4])
            self.event["idep"] = float(event[3][5])
            self.event["iddep"] = float(event[3][6])

            ### fifth line of #f
            self.event["nPorS"] = int(event[4][1])
            self.event["structure"] = event[4][2]
            self.event["nP"] = int(event[4][3])
            # self.event["rP"] = float(event[4][5].strip('%'))
            self.event["nS"] = int(event[4][7])
            # self.event["rS"] = float(event[4][9].strip('%'))
            self.event["ninit"] = int(event[4][11])
            # self.event["rinit"] = float(event[4][13].strip('%'))

            ### last line of #f
            self.event["stdPResidual"] = float(event[5][1])
            self.event["stdSResidual"] = float(event[5][2])

            ## picks
            ### sixth line and beyond of #f (except of last line)
            for rawpick in picks:
                ppick = {}; spick = {}
                ppick["time"] = float(rawpick[7])
                spick["time"] = float(rawpick[10])

                if ppick["time"] > float(self.event["second"]):
                    ppick["id"] = rawpick[1]
                    ppick["pol"] = rawpick[2]

                    ppick["dist"] = float(rawpick[3])
                    ppick["azimuth_deg"] = float(rawpick[4])
                    ppick["emergent_deg"] = float(rawpick[5])
                    ppick["incident_deg"] = float(rawpick[6])

                    ppick["type"] = 'p'

                    ppick_timestamp_dt = event_timestamp_dt \
                        - datetime.timedelta(seconds=float(self.event["second"])) + datetime.timedelta(seconds=ppick["time"])
                    ppick["timestamp"] = ppick_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

                    ppick["accuracy"] = float(rawpick[8])
                    ppick["residual"] = float(rawpick[9])

                    ppick["amp"] = float(rawpick[13])
                    ppick["mag"] = float(rawpick[14])
                    self.picks.append(ppick)

                if float(spick["time"]) > float(self.event["second"]):
                    spick["id"] = rawpick[1]
                    spick["pol"] = rawpick[2]

                    spick["dist"] = float(rawpick[3])
                    spick["azimuth_deg"] = float(rawpick[4])
                    spick["emergent_deg"] = float(rawpick[5])
                    spick["incident_deg"] = float(rawpick[6])

                    spick["type"] = 'p'

                    spick_timestamp_dt = event_timestamp_dt \
                        - datetime.timedelta(seconds=float(self.event["second"])) + datetime.timedelta(seconds=spick["time"])
                    spick["timestamp"] = spick_timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

                    spick["accuracy"] = float(rawpick[11])
                    spick["residual"] = float(rawpick[12])

                    spick["amp"] = float(rawpick[13])
                    spick["mag"] = float(rawpick[14])
                    self.picks.append(spick)

        elif type == "json":
            self.event = event; self.picks = picks

        else:
            print("[EventInfo.__init__] Error: Unsupported format", type)
            exit(1)

    def toJson(self):
        return {"index": self.event_index, "eventInfo": self.event, "picksInfo": self.picks}
    
    def toWinpick(self, outdir, stntbl):
        # func
        def p3_value(id, picks, ev, chtbl):
            # id
            chid_UD = chtbl[(chtbl[3] == id) & (chtbl[4].isin(['UD', 'U', 'Z', 'VZ']))].values[0][0] # vertical compornent for P phase and maxamp
            chid_EW = chtbl[(chtbl[3] == id) & (chtbl[4].isin(['EW', 'E', 'X', 'VX']))].values[0][0] # horizontal compornent for S phase

            # pick
            values = []; amps = {}
            for pick in picks:
                type = pick["type"]
                time = pick["time"]
                pol = '+0'

                amp = str(pick["amp"])
                
                ## P phase
                if type == "p":
                    tp = str(time).split('.')
                    tp1 = tp[0].zfill(2)
                    tp2 = tp[1][0:3]

                    value = " ".join([chid_UD, '0', tp1, tp2, tp1, tp2, pol])
                
                ## S phase
                elif type == "s":
                    ts = str(time).split('.')
                    ts1 = ts[0].zfill(2)
                    ts2 = ts[1][0:3]

                    value = " ".join([chid_EW, '1', ts1, ts2, ts1, ts2, pol])

                values.append(value)
                amps[type] = amp
                
            # maxamp
            maxamp_type = max(amps, key=amps.get)
            maxamp = amps[maxamp_type]
            pol = '-1'

            if maxamp_type == "p":
                value = " ".join([chid_EW, '3', tp1, tp2, tp1, tp2, pol, maxamp])

            elif maxamp_type == "s":
                value = " ".join([chid_EW, '3', ts1, ts2, ts1, ts2, pol, maxamp])
            
            values.append(value)

            return values

        # main
        idx = self.event_index
        ev = self.event
        picks = self.picks
        stations = set([pick["id"] for pick in picks])

        chtbl = stntbl.chtbl_df

        # file name
        t1 = datetime.datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%y%m%d.%H%M%S") + "-000" # win default is first P pick
        i = 0
        while True:
            fname = os.path.join(outdir, t1)
            if os.path.exists(fname):
                t1 = "-".join(["-".join(t1.split("-")[:-1]), str(i+1).zfill(3)])
                i += 1
            else:
                break
        self.winpickFname = fname

        # first line of #p
        p1 = ' '.join(['#p', t1, str(idx), 'auto']) + '\n'

        # second line of #p
        t2 = datetime.datetime.strptime(ev["timestamp"], "%Y-%m-%dT%H:%M:%S.%f").strftime("%y %m %d %H %M %S")
        p2 = ' '.join(['#p', t2]) + '\n'

        # third line and beyond of #p
        p3_values = []
        for id in stations:
            picks_id = [pick for pick in picks if pick["id"] == id]
            p3_values += p3_value(id, picks_id, ev, chtbl)
        p3_list = [' '.join(['#p', p3_value]) + '\n' for p3_value in p3_values]

        # write
        with open(fname, 'w') as f:
            f.write(p1)
            f.write(p2)
            f.writelines(p3_list)