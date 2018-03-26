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


    def do_startRun(self, args):
	"""Starts a PC059A run"""
	print "COMMAND RECEIVED: STARTING RUN"
	#startTLU( uhalDevice = self.hw, pychipsBoard = self.board,  writeTimestamps = ( options.writeTimestamps == "True" ) )
	#print self.hw

    def do_stopRun(self, args):
	"""Stops a PC059A run"""
	print "COMMAND RECEIVED: STOP RUN"


    def do_quit(self, args):
        """Quits the program."""
        print "COMMAND RECEIVED: QUITTING SCRIPT."
        #raise SystemExit
	return True

#################################################
if __name__ == "__main__":
    hw_pc059a= pc059a("sfpfanout", "file://./pc059_connection.xml")
    hw_pc059a.initialize()
    hw_pc059a.start()
    hw_pc059a.stop()
    # prompt = MyPrompt()
    # prompt.prompt = '>> '
    # prompt.cmdloop("Welcome to miniTLU test console.\nType HELP for a list of commands.")
