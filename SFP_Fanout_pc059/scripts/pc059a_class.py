# -*- coding: utf-8 -*-

#IMPORT THE LIBRARIES WRITTEN FOR AIDA TLU
#CHANGE THIS PATH ACCORDING TO WHERE THE FILES ARE SAVED ON
#LOCAL MACHINE
import sys
sys.path.append('/users/phpgb/workspace/myFirmware/AIDA/packages')

import uhal;
import pprint;
import time
from I2CuHal import I2CCore
from si5345 import si5345 # Library for clock chip
from AD5665R import AD5665R # Library for DAC
from PCA9539PW import PCA9539PW # Library for serial line expander
from E24AA025E48T import E24AA025E48T # Library for EEPROM
from PCA9548ADW import PCA9548ADW # Library for I2C bus expander
from ADN2814ACPZ import ADN2814ACPZ # Library for CDR chip

class pc059a:
    """docstring for PC059A DUNE FANOUT"""
    def __init__(self, dev_name, man_file):
        self.dev_name = dev_name
        self.manager= uhal.ConnectionManager(man_file)
        self.hw = self.manager.getDevice(self.dev_name)
        
        self.fwVersion = self.hw.getNode("version").read()
        self.hw.dispatch()
        print "DUNE FANOUT FIRMWARE VERSION= " , hex(self.fwVersion)

        # Instantiate a I2C core to configure components
        self.i2c_master= I2CCore(self.hw, 10, 5, "i2c_master", None)
        #self.i2c_master.state()

        enableCore= True #Only need to run this once, after power-up
        self.enableCore()
        
        # Instantiate EEPROM
        self.zeEEPROM= E24AA025E48T(master_I2C, 0x57)

        # Instantiate clock chip
        self.zeClock=si5345(self.i2c_master, 0x68)
        res= self.zeClock.getDeviceVersion()
        self.zeClock.checkDesignID()

        # Instantiate expander for the equalizers
        self.EXP_EQ=PCA9539PW(self.master_I2C, 0x74)
        #BANK 0
        self.EXP_EQ.setInvertReg(0, 0x00)# 0= normal
        self.EXP_EQ.setIOReg(0, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
        self.EXP_EQ.setOutputs(0, 0xFF)
        res= self.EXP_EQ.getInputs(0)
        print "EXP_EQ read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.EXP_EQ.setInvertReg(1, 0x00)# 0= normal
        self.EXP_EQ.setIOReg(1, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
        self.EXP_EQ.setOutputs(1, 0xFF)
        res= self.EXP_EQ.getInputs(1)
        print "EXP_EQ read back bank 1: 0x%X" % res[0]

        # Instantiate expander for SFP signals
        self.EXP_SFP=PCA9539PW(self.master_I2C, 0x75)
        #BANK 0
        self.EXP_SFP.setInvertReg(0, 0x00)# 0= normal
        self.EXP_SFP.setIOReg(0, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
        self.EXP_SFP.setOutputs(0, 0xFF)
        res= self.EXP_SFP.getInputs(0)
        print "self.EXP_SFP read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.EXP_SFP.setInvertReg(1, 0x00)# 0= normal
        self.EXP_SFP.setIOReg(1, 0xFF)# FF= input <<<<<<<<<<<<<<<<<<<
        self.EXP_SFP.setOutputs(1, 0xFF)
        res= self.EXP_SFP.getInputs(1)
        print "self.EXP_SFP read back bank 1: 0x%X" % res[0]
        
        # Instantiate expander for LED control
        self.EXP_LED=PCA9539PW(self.master_I2C, 0x76)
        #BANK 0
        self.EXP_LED.setInvertReg(0, 0x00)# 0= normal
        self.EXP_LED.setIOReg(0, 0x00)# 0= output (LED) <<<<<<<<<<<<<<<<<<<
        self.EXP_LED.setOutputs(0, 0xAA)
        res= self.EXP_LED.getInputs(0)
        print "self.EXP_LED read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.EXP_LED.setInvertReg(1, 0x00)# 0= normal
        self.EXP_LED.setIOReg(1, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
        self.EXP_LED.setOutputs(1, 0xFF)
        res= self.EXP_LED.getInputs(1)
        print "self.EXP_LED read back bank 1: 0x%X" % res[0]
        
        # Instantiate I2C multiplexer
        self.MUX_I2C=PCA9548ADW(self.master_I2C, 0x73)
        
        # Instantiate CDR for upstream and multiplexer
        CDR_UPS=ADN2814ACPZ(self.master_I2C, 0x40)
        CDR_MUX=ADN2814ACPZ(self.master_I2C, 0x60)

##################################################################################################################################
##################################################################################################################################
    def enableCore(self):
        ## At power up the Enclustra I2C lines are disabled (tristate buffer is off).
        ## This function enables the lines. It is only required once.
        mystop=True
        print "  Enabling I2C bus (expect 127):"
        myslave= 0x21
        mycmd= [0x01, 0x7F]
        nwords= 1
        self.i2c_master.write(myslave, mycmd, mystop)

        mystop=False
        mycmd= [0x01]
        self.i2c_master.write(myslave, mycmd, mystop)
        res= self.i2c_master.read( myslave, nwords)
        print "\tPost RegDir: ", res

    def getClockStatus(self):
        clockStatus = self.hw.getNode("logic_clocks.LogicClocksCSR").read()
        self.hw.dispatch()
        print "  CLOCK STATUS [expected 1]"
        print "\t", hex(clockStatus)
        if ( clockStatus == 0 ):
            "ERROR: Clocks in EUDUMMY FPGA are not locked."
        return clockStatus

    def getFifoData(self, nWords):
        #fifoData= self.hw.getNode("eventBuffer.EventFifoData").read()
        fifoData= self.hw.getNode("eventBuffer.EventFifoData").readBlock (nWords);
        self.hw.dispatch()
        #print "\tFIFO Data:", hex(fifoData)
        return fifoData

    def getFifoLevel(self):
        FifoFill= self.hw.getNode("eventBuffer.EventFifoFillLevel").read()
        self.hw.dispatch()
        print "\tFIFO level read back as:", hex(FifoFill)
        return FifoFill

    def getFifoCSR(self):
        FifoCSR= self.hw.getNode("eventBuffer.EventFifoCSR").read()
        self.hw.dispatch()
        print "\tFIFO CSR read back as:", hex(FifoCSR)
        return FifoCSR

    def getInternalTrg(self):
        trigIntervalR = self.hw.getNode("triggerLogic.InternalTriggerIntervalR").read()
        self.hw.dispatch()
        print "\tTrigger frequency read back as:", trigIntervalR, "Hz"
        return trigIntervalR

    def getSN(self):
        epromcontent=self.readEEPROM(0xfa, 6)
        print "  EUDET dummy serial number (EEPROM):"
        result="\t"
        for iaddr in epromcontent:
            result+="%02x "%(iaddr)
        print result
        return epromcontent

    def readEEPROM(self, startadd, bytes):
        mystop= 1
        time.sleep(0.1)
        myaddr= [startadd]#0xfa
        self.i2c_master.write( 0x50, [startadd], mystop)
        res= self.i2c_master.read( 0x50, bytes)
        return res

    def resetClock(self):
        # Set the RST pin from the PLL to 1
        print "  Clocks reset"
        cmd = int("0x1",16)
        self.hw.getNode("logic_clocks.LogicRst").write(cmd)
        self.hw.dispatch()

    def resetClocks(self):
        #Reset clock PLL
        self.resetClock()
        #Get clock status after reset
        self.getClockStatus()
        #Restore clock PLL
        self.restoreClock()
        #Get clock status after restore
        self.getClockStatus()
        #Get serdes status
        self.getChStatus()

    def setFifoCSR(self, cmd):
        self.hw.getNode("eventBuffer.EventFifoCSR").write(cmd)
        self.hw.dispatch()
        self.getFifoCSR()

##################################################################################################################################
##################################################################################################################################

    def initialize(self):
        print "\nPC059A (DUNE FANOUT) INITIALIZING..."

        #READ CONTENT OF EPROM VIA I2C
        self.getSN()

        # #Check clock status
        self.getClockStatus()

        print "PC059A (DUNE FANOUT) INITIALIZED"

##################################################################################################################################
##################################################################################################################################
    def start(self, logtimestamps=False):
        print "PC059A (DUNE FANOUT) STARTING..."

        print "  PC059A (DUNE FANOUT) RUNNING"

##################################################################################################################################
##################################################################################################################################
    def stop(self):
        print "PC059A (DUNE FANOUT) STOPPING..."

        print "  PC059A (DUNE FANOUT) STOPPED"
