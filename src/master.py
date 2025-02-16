import os
import glob

from model_stn import StationTable

class MasterConfig(object):
    def __init__(self, args):
        ## set args
        for key, value in args.items():
            setattr(self, key, value)

        # ## init input files
        # self.files = glob.glob(self.indir + "/*")

        ## set tmpdir and outdir
        self.tmpdir = ".tmp"
        os.makedirs(self.tmpdir, exist_ok=True)

        windirname = "win"
        if self.outdir is None:
            self.outdir = os.path.dirname(self.infile)
        self.windir = os.path.join(self.outdir, windirname)
        os.makedirs(self.windir, exist_ok=True)

        ## set locating program
        self.locator = "hypomh"

        ## set chlst
        stntbl = StationTable(self.chtbl, None)
        stntbl.screeningTbl(self.tmpdir)

        self.stntbl = stntbl
        self.chtbl = stntbl.chtbl

        # set format
        for format in self.format:
            if format not in ['csv', 'json', 'txt']:
                print("[Error: invalid format]:", format)
                exit(1)
            
        # ## set stntbl
        # self.stnlstData = read_stnlst(self.stnlst)
        # self.chtblData = read_chtbl(self.chtbl)
        # self.stntblData = make_stntbl(self.stnlstData, self.chtblData)

class Config(object):
    def __init__(self, masterConfig, n):
        self.master = masterConfig
        self.n = n

        self.file_day = 'all'
        self.out_dir_header = os.path.join(self.master.windir, 'out-%s' % self.n)
        self.out_dir = os.path.join(self.out_dir_header, self.file_day)
        os.makedirs(self.out_dir, exist_ok=True)

        ## make win parameter file
        self.prmfile = os.path.join(self.master.tmpdir, 'win.prm')

        lines = []
        lines.append("") #/* default directory for data file */
        lines.append(self.master.chtbl) #/* channel table */
        lines.append("") #/* zone file */
        lines.append(self.out_dir) #/* picks directory */
        lines.append(self.master.locator) #/* hypomh program */	
        lines.append(self.master.velfile) #/* structure model */
        lines.append("") #/* map file */
        lines.append("") #/* output directory */
        lines.append("") #/* output format */
        lines.append("") #/* filter file */
        lines.append("") #/* printer name */
        lines.append("") #/* projection */
        lines.append("") #/* labels file */
        lines.append("") #/* hypocenters file */
        lines.append("") #/* printer's DPI */
        lines.append(self.master.tmpdir) #/* working directory */

        with open(self.prmfile, 'w') as f:
            f.writelines("\n".join(lines))

        # if set several th
        if type(self.master.res[0]) == list:
            if len(self.master.res) == self.master.itr_hypo - 1:
                self.res = self.master.res[self.n-1]
            else:
                print("[Error]: --res format is not proper. \
                      For example, 2 sets of thresholds are required for a 3 iteration process, like '5-10,1-2'. \
                      Alternatively, common set of thresholds can be set like '5-10'.")
        elif type(self.master.res[0]) == int:
            if len(self.master.res) == 2:
                self.res = self.master.res
            else:
                print("[Error]: --res format is not proper. Required 2 values, like '5-10', but given %s. \
                      Alternatively, individual sets of thresholds can be set like '5-10,1-2'." % len(self.master.res))
        else:
            print("[Error]: --res format is not proper. Must be like '5-10,1-2' or '5-10'.")

class MasterProcess(object):
    def __init__(self, config):
        self.config = config

    def rm_tmp(self):
        # remove tmp file
        ext = ["tbl", "prm"]

        l = []
        for s in ext:
            l += glob.glob(self.config.tmpdir + "/**/*.%s" % s, recursive=True)
        for file in l:
            os.remove(file)
            # print(file)

        # remove tmp dir
        # paths = glob.glob(self.config.tmpdir + "/**/*", recursive=True)
        # max_depth = max(paths, key=lambda p: p.count(os.sep)).count(os.sep)
        # l = [p for p in paths if p.count(os.sep) == max_depth]
        l = [self.config.tmpdir]
        for dir in l:
            os.removedirs(dir)
    
    def rm_old(self):
        l = glob.glob(self.config.windir + "/**/??????.??????-???", recursive=True)
        for file in l:
            os.remove(file)
            # print(file)