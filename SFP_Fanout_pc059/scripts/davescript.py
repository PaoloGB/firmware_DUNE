# -*- coding: utf-8 -*-


#!/usr/bin/python

import uhal
import time
import sys

uhal.setLogLevelTo(uhal.LogLevel.NOTICE)
manager = uhal.ConnectionManager("file://daveconnections.xml")
hw_list = [manager.getDevice(i) for i in sys.argv[1:]]

if len(hw_list) == 0:
    print "No targets specified - I'm done"
    sys.exit()

for hw in hw_list:
    print hw.id()
    hw.getNode("io.csr.ctrl.cdr_edge").write(1)#do not change
    hw.getNode("io.csr.ctrl.sfp_edge").write(1)
    hw.getNode("io.csr.ctrl.hdmi_edge").write(1)
    hw.getNode("io.csr.ctrl.usfp_edge").write(1)# change this to 0 or 1 to change detection edge
    hw.getNode("io.csr.ctrl.mux").write(0)
    hw.getNode("csr.ctrl.prbs_init").write(1);
    hw.dispatch()
    hw.getNode("csr.ctrl.prbs_init").write(0);
    hw.dispatch()
    reg = hw.getNode("io.csr.stat").read()
    hw.dispatch()
    print hex(reg)

while True:
    time.sleep(1)
    for hw in hw_list:
        reg = hw.getNode("io.csr.stat").read()
        reg2 = hw.getNode("csr.stat").read()
        cyc_ctr = hw.getNode("cyc_ctr").readBlock(2)
        ust_ctrs = hw.getNode("ust_ctr").readBlock(2)
        cdr_ctr = hw.getNode("cdr_ctr").read()
        sfp_ctrs = hw.getNode("sfp_ctr").readBlock(8)
        hw.dispatch()
        cycles= (int(cyc_ctr[1]) << 32) + int(cyc_ctr[0])
        print "________________________________________________________________________________________________________________________________________________________________________________________"
        print "io_status \t|   stat   \t\t|   cycles    \t\t|   hdmi   \t\t|   ucdr   \t\t|   cdr    \t\t\n", "{0:#0{1}x}".format(reg, 12),"\t|  ", "{0:#0{1}x}".format(reg2, 12),"\t|  ", "{0:#0{1}x}".format(cycles, 12), "\t|  ", "{0:#0{1}x}".format(ust_ctrs[0], 12),"\t|  ", "{0:#0{1}x}".format(ust_ctrs[1], 12),"\t|  ", "{0:#0{1}x}".format(cdr_ctr, 12)
        print "\tsfp7\t\t|\tsfp6\t\t|\tspf5\t\t|\tsfp4\t\t|\tsfp3\t\t|\tsfp2\t\t|\tsfp1\t\t|\tsfp0"
        for i in reversed(range(8)):
            print "\t", "{0:#0{1}x}".format(sfp_ctrs[i], 10),"\t|",
        print
        print
