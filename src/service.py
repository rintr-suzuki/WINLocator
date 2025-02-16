import os
import json
import pandas as pd
import subprocess as sp
from scipy.spatial import cKDTree
from tqdm import tqdm

from model_event import EventInfo

class EventConverter(object):
    def __init__(self, config):
        self.master = config

    def convertFromJson(self, config, winLocator):
        # set config
        ## itr
        n = config.n

        ## input
        pres = config.res[0]
        sres = config.res[1]

        ## output
        # file_day = config.file_day
        out_dir = config.out_dir

        # read input
        if n >= 1:
            eventInfoList0 = winLocator.eventInfoLists[n-1]
            self.eventInfoList = []
            for item in eventInfoList0:
                picksInfoNew = []
                for sub_item in item.picks:
                    if (sub_item['type'] == "p") and (abs(sub_item['residual']) <= pres):
                        picksInfoNew.append(sub_item)
                    elif (sub_item['type'] == "s") and (abs(sub_item['residual']) <= sres):
                        picksInfoNew.append(sub_item)
                #print(picksInfoNew)
                if len(picksInfoNew) >= 4:
                    # at least 4 picks are needed to locate
                    self.eventInfoList.append(EventInfo(item.event_index, item.event, picksInfoNew, "json"))

        elif n == 0:
            self.infile = self.master.infile
            with open(self.infile) as f:
                meta = json.load(f)

            self.eventInfoList = [EventInfo(eventInfo["index"], eventInfo["eventInfo"], eventInfo["picksInfo"], "json") for eventInfo in meta]
            if len(self.eventInfoList) == 0:
                print("[ERROR]: Number of input events is 0. Input 1 event data at least.")
                exit()   

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
        
    def convert2json(self, config):
        ## itr
        n = config.n

        # convert to dict
        self.__convert2dict()

        # write json
        ## add to meta
        metaone = self.eventInfoLists[n]
        self.meta.append(metaone)

        ## write output
        if self.master.mkEachJson:
            self.writeJson(n=config.n, format=self.master.format)

        ## select event after the last iteration
        if n+1 == self.master.itr_hypo:
            print("[WINLocator.convert2json]: Select hypo")
            metaone_selected0 = self.__selectHypo(metaone, self.master)
            
            if self.master.rm_duplicate:
                print("[WINLocator.convert2json]: Remove duplicated hypo")
                metaone_selected = self.__removeDuplicate(metaone_selected0)
            else:
                metaone_selected = metaone_selected0

            self.meta.append(metaone_selected)

            # write json
            self.writeJson(format=self.master.format)

    def writeJson(self, n=-1, format=['csv']):
        # select meta
        ## write each
        if n >= 0:
            outfilebase = "picks_located-%s" % n
            outmeta = [eventInfo.toJson() for eventInfo in self.meta[n]]

        ## write final
        elif n == -1:
            outfilebase = "picks_located"
            outmeta = [eventInfo.toJson() for eventInfo in self.meta[-1]]

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
    
    def __selectHypo(self, eventInfoList0, config):
        eventInfoList =[]
        for event in eventInfoList0:
            event.addPickCounts(stntbl=config.stntbl.chtbl_df, nearstn=config.nearstn)
            if self.__selectHypoFlag(event, config):
                eventInfoList.append(event)
        return eventInfoList
    
    def __selectHypoFlag(self, event, config):
        flag = False
        if (event.event["dlat"] < config.dolat) & \
            (event.event["dlon"] < config.dolon) & \
            (event.event["stdPResidual"] < config.std_ditp) & \
            (event.event["stdSResidual"] < config.std_dits) & \
            (event.event["pickCounts"]["nPorS_nearonly"] >= config.pspicknear) & \
            (event.event["pickCounts"]["nStn-PandS"] >= config.bothps) & \
            (event.event["pickCounts"]["nP"] >= config.ppick) & \
            (event.event["pickCounts"]["nPorS"] >= config.pspick):
            flag = True
        return flag
    
    def __removeDuplicate(self, eventInfoList0):
        # CSVファイルの読み込み
        # TODO: eventInfoList0をdict型のまま処理する
        catalogmeta = [eventInfo.toJson() for eventInfo in eventInfoList0]
        df = self.__extractInfo2(catalogmeta)

        # グループを取得
        grouped_indices = self.__group_rows(df, self.master.dupotime, self.master.dupolat, self.master.dupolon)

        # 抜き出された行の処理
        ## 処理前のdfをコピー
        remaining_rows = df.copy()

        ## 重複イベントを削除
        processed_rows = []
        for group in tqdm(grouped_indices, desc="Processing groups"):
            # 各重複イベントグループ(サブセット)に対して処理
            sub_df = df.loc[group]
            # サブセットのうち検測値数が最も多いもののみ残して削除
            max_pspick = sub_df.loc[sub_df['nPorS'].idxmax()]
            updated_row = max_pspick.copy()
            processed_rows.append(updated_row)
            # 上記で処理された行を削除
            remaining_rows.drop(group, inplace=True)
        df_processed = pd.DataFrame(processed_rows)

        # 重複イベント候補とならなかったものと結合
        df_final = pd.concat([remaining_rows, df_processed]).sort_values(by="timestamp")

        # df_finalのindexだけ抜き出す
        eventInfoList = [eventInfo for eventInfo in eventInfoList0 if eventInfo.event_index in df_final.index]
        return eventInfoList

    def __extractInfo2(self, meta):
        data = []
        data += [[event['index'], event['eventInfo']['timestamp'], \
                    event['eventInfo']['lat'], \
                    event['eventInfo']['lon'], \
                    event['eventInfo']['dep'], \
                    event['eventInfo']['mag'], \
                    event['eventInfo']['pickCounts']['nPorS']] for event in meta]

        df = pd.DataFrame(data, columns=['index', 'timestamp', 'lat', 'lon', 'dep', 'mag', 'nPorS']).set_index('index')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    # 条件に基づく行のグループ化
    def __group_rows(self, df, tdth, latdth, londth):
        # 2イベントの組に対して、緩い条件を満たすものを網羅探索する (同じindexが複数回利用されることあり)
        coords = df[["timestamp", "lat", "lon"]].copy()
        coords["timestamp"] = coords["timestamp"].astype(int) // 10**9  # 秒単位に変換
        tree = cKDTree(coords.values)
        pairs = tree.query_pairs(r=(tdth+latdth+londth+0.01), p=1)  # 合計+少しの誤差範囲で検索
        
        # 小さい要素の昇順ソート
        normalized_pairs = [(min(i, j), max(i, j)) for i, j in pairs]
        sorted_pairs = sorted(normalized_pairs, key=lambda pair: pair[0])

        grouped = []
        used_indices = set()

        # 2イベントの組をベースに時刻順に精査
        for i, j in tqdm(sorted_pairs, desc="Grouping rows"):
            # 時刻順に検索して、既にindexが重複イベント該当済のものは除外
            if df.index[i] in used_indices or df.index[j] in used_indices:
                continue

            # まず2イベントの組が正確に条件を満たすか確認
            time_diff = abs((df.loc[df.index[i], "timestamp"] - df.loc[df.index[j], "timestamp"]).total_seconds())
            lat_diff = abs(df.loc[df.index[i], "lat"] - df.loc[df.index[j], "lat"])
            lon_diff = abs(df.loc[df.index[i], "lon"] - df.loc[df.index[j], "lon"])
            
            if time_diff > tdth or lat_diff > latdth or lon_diff > londth:
                continue  # iとjが条件を満たしていない場合は除外

            group = {df.index[i], df.index[j]}
            for k in range(len(df)):
                # 時刻順に検索して、既にindexが重複イベント該当済のものは除外
                if df.index[k] in group or df.index[k] in used_indices:
                    continue

                # 3イベント目を探す
                time_diff = abs((df.loc[df.index[i], "timestamp"] - df.loc[df.index[k], "timestamp"]).total_seconds())
                lat_diff = abs(df.loc[df.index[i], "lat"] - df.loc[df.index[k], "lat"])
                lon_diff = abs(df.loc[df.index[i], "lon"] - df.loc[df.index[k], "lon"])
                if time_diff <= tdth and lat_diff <= latdth and lon_diff <= londth:
                    group.add(df.index[k])
            grouped.append(list(group))
            used_indices.update(group)
        
        return grouped