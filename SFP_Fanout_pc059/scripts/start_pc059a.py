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

    prompt = MyPrompt()
    prompt.prompt = '>> '

    hw_pc059a = pc059a("sfpfanout", "file://./pc059_connection.xml")
#    hw_pc059a.initialize()


    # Start interactive prompt
    print "===================================================================="
    print "=======================PC059A TEST CONSOLE=========================="
    print "===================================================================="
    prompt.cmdloop("Type 'help' for a list of commands.")
