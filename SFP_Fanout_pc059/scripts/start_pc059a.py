# -*- coding: utf-8 -*-
# PC059A SFP FANOUT

import uhal
import sys
import time
# from ROOT import TFile, TTree
# from ROOT import gROOT
from datetime import datetime

from pc059a_class import pc059a
# Use to have interactive shell
import cmd

class MyPrompt(cmd.Cmd):

    def do_connect(self, args):
        """Configures the board to connect a specific SFP port using the multiplexersself.
        Syntax: connect #
        Where N must be an integer between 0 and 7."""
        arglist = args.split()
        if len(arglist) == 0:
            print "\tno port specified. ignoring the command"
        else:
            results = list(map(int, arglist))
            iSFP= results[0]
            hw_pc059a._sfpSelect(iSFP, 2, 0)

    def do_i2c(self, args):
        arglist = args.split()
        if len(arglist) == 0:
            print "\tno command specified"
        else:
            i2ccmd= arglist[0]
            results = list(map(int, arglist))
            hw_pc059a.DISP.writeSomething(results)
            print "Sending i2c command to display"
        return
        
    def do_enableAll(self, args):
        for iSFP in range (0,8):
            print "enabling SFP", iSFP
            hw_pc059a._sfpEnable(iSFP, True)
            hw_pc059a._setLED(iSFP, 1)
        return

    def do_readSFPpower(self, args):
        """Reads SFP power using I2C"""
    	print "COMMAND RECEIVED: READ SFP POWER"
        print "SFPs connected:", format(hw_pc059a.mux_I2C.getChannelStatus(), '#010b')
        #hw_pc059a.SFP_ds.scanI2C()
        print "Vend ID:", hw_pc059a.SFP_ds.getVendorId()
        print "Vend PN:", hw_pc059a.SFP_ds.getVendorPN()
        print "Vend Name:", hw_pc059a.SFP_ds.getVendorName()
        hw_pc059a.SFP_ds.getEncoding()
        print "Transceiver code:", hw_pc059a.SFP_ds.getTransceiver()
        hw_pc059a.SFP_ds.getConnector()
        hw_pc059a.SFP_ds.getDiagnosticsType()
        hw_pc059a.SFP_ds.getEnhancedOpt()
        
        return

    def do_start(self, args):
    	"""Starts a PC059A run"""
    	print "COMMAND RECEIVED: START RUN"
        hw_pc059a.start()
        return

    def do_initialize(self, args):
        """Initialize PC059A"""
        hw_pc059a.initialize(0)
        return

    def do_terminate(self, args):
    	"""Stops a PC059A run"""
    	print "COMMAND RECEIVED: STOP RUN"
        return

    def do_quit(self, args):
        """Quits the program."""
        print "COMMAND RECEIVED: QUIT INTERFACE"
        #raise SystemExit
        return True

#################################################
if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print "Usage: python start_pc059a.py TARGET"
        print "Example: python start_pc059a.py DUNE_FANOUT_32"
        print "No targets specified - exiting"
        sys.exit()
    
    hw_name = sys.argv[1]
    hw_pc059a = pc059a(hw_name, "file://./pc059_connection.xml")
        
    
    prompt = MyPrompt()
    prompt.prompt = '>> '

    #hw_pc059a = pc059a("DUNE_FANOUT_32", "file://./pc059_connection.xml")
    


    # Start interactive prompt
    print "===================================================================="
    print "=======================PC059A TEST CONSOLE=========================="
    print "===================================================================="
    prompt.cmdloop("Type 'help' for a list of commands.")
