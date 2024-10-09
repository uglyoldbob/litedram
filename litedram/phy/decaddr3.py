from migen import *

from litex.soc.interconnect.csr import *

from litedram.common import *
from litedram.phy.dfi import *

class DecaDdr3Phy(Module):
    def __init__(self, pads,
            ddr3,
            sys_clk_freq = 50e6,
            cl           = None,
            cwl          = None,
            ):
        pads        = PHYPadsCombiner(pads)
        memtype = "DDR3"
        tck         = 2/(2*2*sys_clk_freq)
        addressbits = len(pads.a)
        bankbits    = len(pads.ba)
        nranks      = 1 if not hasattr(pads, "cs_n") else len(pads.cs_n)
        databits    = len(pads.dq)
        nphases     = 2
        assert databits%8 == 0

        cl  = get_default_cl( memtype, tck) if cl  is None else cl
        cwl = get_default_cwl(memtype, tck) if cwl is None else cwl
        cl_sys_latency  = get_sys_latency(nphases, cl)
        cwl_sys_latency = get_sys_latency(nphases, cwl)

        self.ddr3 = ddr3
        rdphase = get_sys_phase(nphases, cl_sys_latency, cl)
        wrphase = get_sys_phase(nphases, cwl_sys_latency, cwl)
        self.settings = PhySettings(
            phytype       = "DECADDR3PHY",
            memtype       = memtype,
            databits      = databits,
            dfi_databits  = 4*databits,
            nranks        = nranks,
            nphases       = nphases,
            rdphase       = rdphase,
            wrphase       = wrphase,
            cl            = cl,
            cwl           = cwl,
            read_latency  = cl_sys_latency + 10,
            write_latency = cwl_sys_latency,
            read_leveling = True,
            bitslips      = 4,
            delays        = 8,
        )
        self.dfi = dfi = Interface(addressbits, bankbits, nranks, 4*databits, nphases)
        print("Init ddr3 for deca")
