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

        ## make win parameter file
        self.prmfile = os.path.join(self.master.tmpdir, 'win.prm')

        lines = []
        lines.append("") #/* default directory for data file */
        lines.append(self.master.chtbl) #/* channel table */
        lines.append("") #/* zone file */
        lines.append(self.master.windir) #/* picks directory */
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

    def set_fname(self, fname):
        self.fname = fname
        self.baseFname = os.path.basename(self.fname)

    def set_in(self, n):
        self.indir = self.master.indir
        # self.indir = os.path.join(self.master.indir, 'win')
        self.files = glob.glob(os.path.join(self.indir, '*'))

    def set_out(self, n):
        self.outcsv = "trg_located-%s.csv" % n

class MasterProcess(object):
    def __init__(self, config):
        self.config = config

    def rm_tmp(self):
        ext = ["tbl", "prm"]

        l = []
        for s in ext:
            l += glob.glob(self.config.tmpdir + "/**/*.%s" % s, recursive=True)
        for file in l:
            os.remove(file)
            # print(file)