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
        print "--", self.dev_name, "FIRMWARE VERSION= " , hex(self.fwVersion)

    # Instantiate a I2C core to configure components
        self.i2c_master= I2CCore(self.hw, 10, 5, "i2c_master", None)

    # Instantiate a secondary I2C core for SFP cage (not working yet)
        #self.i2c_secondary= I2CCore(self.hw, 10, 5, "i2c_sfp", None)

    # Enable the I2C interface on enclustra
        enableCore= True #Only need to run this once, after power-up
        self._enableCore()

    # Instantiate EEPROM
        self.zeEEPROM= E24AA025E48T(self.i2c_master, 0x57)

    # Instantiate clock chip
        self.zeClock=si5345(self.i2c_master, 0x68)
        res= self.zeClock.getDeviceVersion()
        self.zeClock.checkDesignID()

    # Instantiate expander for the equalizers (IC28)
        self.exp_EQ=PCA9539PW(self.i2c_master, 0x74)
        self.exp_EQ.setInvertReg(0, 0x00)# 0= normal
        self.exp_EQ.setIOReg(0, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
        self.exp_EQ.setInvertReg(1, 0x00)# 0= normal
        self.exp_EQ.setIOReg(1, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<

    # Instantiate expander for SFP signals (IC29)
        self.exp_SFP=PCA9539PW(self.i2c_master, 0x75)
        self.exp_SFP.setInvertReg(0, 0x00)# 0= normal
        self.exp_SFP.setIOReg(0, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
        self.exp_SFP.setInvertReg(1, 0x00)# 0= normal
        self.exp_SFP.setIOReg(1, 0xFF)# FF= input <<<<<<<<<<<<<<<<<<<

    # Instantiate expander for LED control (IC27)
        self.exp_LED=PCA9539PW(self.i2c_master, 0x76)
        self.exp_LED.setInvertReg(0, 0x00)# 0= normal
        self.exp_LED.setIOReg(0, 0x00)# 0= output (LED) <<<<<<<<<<<<<<<<<<<
        self.exp_LED.setInvertReg(1, 0x00)# 0= normal
        self.exp_LED.setIOReg(1, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<

    # Instantiate I2C multiplexer
        self.mux_I2C=PCA9548ADW(self.i2c_master, 0x73)

    # Instantiate CDR for upstream and multiplexer
        self.cdr_UPS=ADN2814ACPZ(self.i2c_master, 0x40)
        self.cdr_MUX=ADN2814ACPZ(self.i2c_master, 0x60)

##################################################################################################################################
##################################################################################################################################
    def _configureClock(self, filename, verbose= False):
        #clkRegList= zeClock.parse_clk("./../../bitFiles/pc059_Si5345.txt")
        clkRegList= self.zeClock.parse_clk(filename)
        self.zeClock.writeConfiguration(clkRegList, verbose)
        self.zeClock.writeRegister(0x0536, [0x0B]) #Configures manual switch of inputs
        self.zeClock.writeRegister(0x0949, [0x0F]) #Enable all inputs
        self.zeClock.writeRegister(0x052A, [0x05]) #Configures source of input

    def _enableCore(self):
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

    def _LEDallOff(self):
        self.exp_LED.setOutputs(0, 0x0)
        old1= self.exp_LED.getInputs(1)[0]
        new1= old1 & 0xF
        self.exp_LED.setOutputs(1, new1)

    def _LEDallOn(self):
        self.exp_LED.setOutputs(0, 0xFF)
        old1= self.exp_LED.getInputs(1)[0]
        new1= old1 | 0xF0
        self.exp_LED.setOutputs(1, new1)

    def _LEDselfcheck(self):
        """Flash all LEDs once to ensure they work correctly. Return to original state once done."""
        old0= self.exp_LED.getInputs(0)[0]
        old1= self.exp_LED.getInputs(1)[0]
        self._LEDallOff()
        time.sleep(0.2)
        self._LEDallOn()
        time.sleep(0.2)
        self._LEDallOff()
        for iLED in range(0, 12):
            self._setLED(iLED, 1)
            time.sleep(0.2)
            self._setLED(iLED, 0)
            time.sleep(0.1)
        self.exp_LED.setOutputs(0, old0)
        self.exp_LED.setOutputs(1, old1)

    def _getSN(self):
        """Return the unique ID from the EEPROM on the board"""
        epromcontent=self.zeEEPROM.readEEPROM(0xfa, 6)
        print "  ", self.dev_name, "serial number (EEPROM):"
        result="\t"
        for iaddr in epromcontent:
            result+="%02x "%(iaddr)
        print result
        return epromcontent

    def _set_bit(self, v, index, x):
        """Set the index:th bit of v to 1 if x is truthy, else to 0, and return the new value."""
        if (index == -1):
            print "  SETBIT: Index= -1 will be ignored"
        else:
            mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
            v &= ~mask          # Clear the bit indicated by the mask (if x is False)
            if x:
                v |= mask         # If x was True, set the bit indicated by the mask.
        return v

    def _setLED(self, iLED, status):
        """Switch one of the leds ON or OFF
        # LED 0:7 = Green SFP indicators (left to right)
        # LED 8:11 = Status indicators (left to right). 11 is red, all the rest green"""
        if  (0 <= iLED <= 7):
            res= self.exp_LED.getInputs(0)[0]
            newState= ( self._set_bit(res, iLED, status) ) & 0xFF
            self.exp_LED.setOutputs(0, newState)
        elif (8 <= iLED <= 11):
            res= self.exp_LED.getInputs(1)[0]
            newState= ( self._set_bit(res, 11-(iLED-4), status) ) & 0xFF
            self.exp_LED.setOutputs(1, newState)
        else:
            print "_setLED: index out of range. iLED must be comprised between 0 and 11"

##################################################################################################################################
##################################################################################################################################

    def initialize(self):
        print "--", self.dev_name, " INITIALIZING..."

    # READ CONTENT OF EPROM VIA I2C
        self._getSN()

    # CONFIGURE CLOCK
        doClock= False
        if doClock:
            clockfile= "./../../bitFiles/pc059_Si5345.txt"
            self._configureClock(clockfile, False)
            self.zeClock.checkDesignID()

    # INITIALIZE EQUALIZER EXPANDER
        #BANK 0
        self.exp_EQ.setOutputs(0, 0xFF)
        res= self.exp_EQ.getInputs(0)
        print "  EXP_EQ read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.exp_EQ.setOutputs(1, 0xFF)
        res= self.exp_EQ.getInputs(1)
        print "  EXP_EQ read back bank 1: 0x%X" % res[0]

    # INITIALIZE SFP EXPANDER
        #BANK 0
        self.exp_SFP.setOutputs(0, 0xFF)
        res= self.exp_SFP.getInputs(0)
        print "  EXP_SFP read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.exp_SFP.setOutputs(1, 0xFF)
        res= self.exp_SFP.getInputs(1)
        print "  EXP_SFP read back bank 1: 0x%X" % res[0]

        print "  ", self.dev_name, " INITIALIZED"

    # INITIALIZE LED EXPANDER
        #BANK0
        self.exp_LED.setOutputs(0, 0x00)
        res= self.exp_LED.getInputs(0)
        print "  EXP_LED read back bank 0: 0x%X" % res[0]
        #BANK1
        self.exp_LED.setOutputs(1, 0x0F)
        res= self.exp_LED.getInputs(1)
        print "  EXP_LED read back bank 1: 0x%X" % res[0]

    # DISABLE ALL CHANNELS FOR I2C multiplexer
        self.mux_I2C.disableAllChannels(True)
        print "  I2C MUX (should be 0)", self.mux_I2C.getChannelStatus(True)

##################################################################################################################################
##################################################################################################################################
    def start(self, logtimestamps=False):
        print "--", self.dev_name, " STARTING..."
        self._LEDselfcheck()

        print "  ", self.dev_name, " RUNNING"

##################################################################################################################################
##################################################################################################################################
    def stop(self):
        print "--", self.dev_name, " STOPPING..."

        print "  ", self.dev_name, " STOPPED"
