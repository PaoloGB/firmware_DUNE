# -*- coding: utf-8 -*-

#IMPORT THE LIBRARIES WRITTEN FOR AIDA TLU
#CHANGE THIS PATH ACCORDING TO WHERE THE FILES ARE SAVED ON
#LOCAL MACHINE
import sys
sys.path.append('/users/phpgb/workspace/myFirmware/AIDA/packages')

import uhal;
import pprint;
import time
#from I2CuHal import I2CCore # I2C library for uhal. This one uses old naming
from I2CuHal2 import I2CCore # I2C library for uhal. This one uses D. Newbold's naming
from si5345 import si5345 # Library for clock chip
from AD5665R import AD5665R # Library for DAC
from PCA9539PW import PCA9539PW # Library for serial line expander
from E24AA025E48T import E24AA025E48T # Library for EEPROM
from PCA9548ADW import PCA9548ADW # Library for I2C bus expander
from SFPI2C import SFPI2C
from ADN2814ACPZ import ADN2814ACPZ # Library for CDR chip
from I2CDISP import LCD09052 #Library for display

class pc059a:
    """docstring for PC059A DUNE FANOUT"""
    def __init__(self, dev_name, man_file):
        uhal.setLogLevelTo(uhal.LogLevel.NOTICE) ## Get rid of initial flood of IPBUS messages
        self.dev_name = dev_name
        self.manager= uhal.ConnectionManager(man_file)
        self.hw = self.manager.getDevice(self.dev_name)

        #self.fwVersion = self.hw.getNode("version").read()
        #self.hw.dispatch()
        #print "--", self.dev_name, "FIRMWARE VERSION= " , hex(self.fwVersion)

    # Instantiate a I2C core to configure components
        #self.i2c_master= I2CCore(self.hw, 10, 5, "i2c_master", None)
        self.i2c_master= I2CCore(self.hw, 10, 5, "io.i2c", None)

    # Instantiate a secondary I2C core for SFP cage (not working yet)
        #self.i2c_secondary= I2CCore(self.hw, 10, 5, "io.usfp_i2c", None)

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

    # Instantiate a generic SFP transceiver for one of the 8 downstream
        self.SFP_ds= SFPI2C(self.i2c_master, 0x50)

    # Instantiate CDR for upstream and multiplexer
        self.cdr_UPS=ADN2814ACPZ(self.i2c_master, 0x40)
        self.cdr_MUX=ADN2814ACPZ(self.i2c_master, 0x60)

    #Instantiate Display
        doDisplaytest= False
        if doDisplaytest:
          self.DISP=LCD09052(self.i2c_master, 0x3A) #3A
          self.DISP.clear()
          self.DISP.test()


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

    def _getSN(self):
        """Return the unique ID from the EEPROM on the board"""
        epromcontent=self.zeEEPROM.readEEPROM(0xfa, 6)
        print "  ", self.dev_name, "serial number (EEPROM):"
        result="\t"
        for iaddr in epromcontent:
            result+="%02x "%(iaddr)
        print result
        return epromcontent

    def _getSFPfault(self):
        """Read the status of the FAULT pins for the downstream SFP ports"""
        res= self.exp_SFP.getInputs(1)[0]
        return res

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

    def _setEQ(self, iSFP, state, verbose= False):
        """ Configure the LVDS buffer equalizer for the i-th SFP port (downstream).
            There are 4 levels of equalization:
            -0: off
            -1: low (~ 4 dB at 1.56 GHZ)
            -2: med (~ 8 dB at 1.56 GHZ)
            -3: high (~ 16 dB at 1.56 GHZ)
        """
        if ( (0 <= iSFP <= 7) and (0<= state <= 3) ):
            res= [0, 0]
            bitstate= [0, 0]
            newState= [0, 0]
            for iBank in range(0,2):
                res[iBank]= self.exp_EQ.getInputs(iBank)[0]
                bitstate[iBank]= (state >> iBank) & 0x1
                newState[iBank]= self._set_bit(res[iBank], iSFP, bitstate[iBank])
                self.exp_EQ.setOutputs(iBank, newState[iBank])
                if verbose:
                    print "SFP", iSFP, "old" , bin(res[iBank]), "bit", bitstate[iBank], "new", bin(newState[iBank])
        else:
            print "setEQ: value out of range. iSFP must be in range [0, 7] and state in [0, 3]"

    def _setLED(self, iLED, status):
        """Switch one of the leds ON or OFF
        # LED 0:7 = Green SFP indicators (right to left)
        # LED 8:11 = Status indicators (left to right). 11 is red, all the rest green"""
        if  (0 <= iLED <= 7):
            res= self.exp_LED.getInputs(0)[0]
            newState= ( self._set_bit(res, 7-iLED, status) ) & 0xFF
            self.exp_LED.setOutputs(0, newState)
        elif (8 <= iLED <= 11):
            res= self.exp_LED.getInputs(1)[0]
            newState= ( self._set_bit(res, 11-(iLED-4), status) ) & 0xFF
            self.exp_LED.setOutputs(1, newState)
        else:
            print "setLED: index out of range. iLED must be comprised between 0 and 11"

    def _sfpEnable(self, iSFP, enable= True):
        """Disable/Enable one of the SFP downstream by asserting or deasserting the TX_DISABLE pin"""
        if  (0 <= iSFP <= 7):
            res= self.exp_SFP.getInputs(0)[0]
            newState= ( self._set_bit(res, iSFP, not enable) ) & 0xFF
            self.exp_SFP.setOutputs(0, newState)

    def _sfpSelect(self, iSFP, EQstate, verbose= 0):
        """Select a downstream SFP port
        - connect the iSFP-th MUX to the CDR
        - connect the I2C MULTIPLEXER so that the iSFP-th port is visible on the busy
        - set the equalizer to the chosen value
        - set the TX_DISABLE low
        - enable the iSFP-th LED, swith off all others
        """
        if  (0 <= iSFP <= 7):
            print "  ROUTING SIGNALS TO SFP #", iSFP
            #self.ipb_setMUXchannel(iSFP)
            self.mux_I2C.setActiveChannel(iSFP)
            self._setEQ(iSFP, EQstate, verbose)
            self._sfpEnable(iSFP, True)
            self._LEDallOff()
            self._setLED(iSFP, 1)
        else:
            print "  sfpSelect: iSFP must be in range [0: 7]"

####IPBUS functionalities. Might change when address map changes
    def ipb_setMUXchannel(self, iChannel):
        """Write to IPBus register to define which channel of the multiplexer is connected"""
        if  (0 <= iChannel <= 7):
            self.hw.getNode("io.csr.ctrl.mux").write(iChannel)
            self.hw.dispatch()
        else:
            print "iChannel must be comprised between 0 and 7"

    def ipb_getMUXchannel(self):
        """Read from IPBus register which channel of the multiplexer is connected"""
        res= self.hw.getNode("io.csr.ctrl.mux").read()
        self.hw.dispatch()
        return res

    def ipb_prbs_init(self):
        """Initialize PRBS generator"""
        print "  INITIALIZING PRBS"
        cmd = int("0x1", 16)
        self.hw.getNode("csr.ctrl.prbs_init").write(cmd)
        self.hw.dispatch()
        cmd = int("0x0", 16)
        self.hw.getNode("csr.ctrl.prbs_init").write(cmd)
        self.hw.dispatch()

    def ipb_getResets(self):
        """Query the status of the various reset lines. A 1 indicates that the line is being reset.
        reset, soft_rst, nuke, pll_rst, mux_rst, i2c_rst"""
        myRST= []
        rst= self.hw.getNode("io.csr.ctrl.rst").read()
        self.hw.dispatch()
        myRST.append(int(rst))

        rst_soft= self.hw.getNode("io.csr.ctrl.soft_rst").read()
        self.hw.dispatch()
        myRST.append(int(rst_soft))

        nuke= self.hw.getNode("io.csr.ctrl.nuke").read()
        self.hw.dispatch()
        myRST.append(int(nuke))

        rst_pll= self.hw.getNode("io.csr.ctrl.rst_pll").read()
        self.hw.dispatch()
        myRST.append(int(rst_pll))

        rst_mux= self.hw.getNode("io.csr.ctrl.rst_i2cmux").read()
        self.hw.dispatch()
        myRST.append(int(rst_mux))

        rst_i2c= self.hw.getNode("io.csr.ctrl.rst_i2c").read()
        self.hw.dispatch()
        myRST.append(int(rst_i2c))
        return myRST

    def ipb_getzflags(self):
        """Query the status of the various fglags. A 1 indicates that a valid pattern has been receivedself.
        [sfp, hdmi, upstream sfp]"""
        myFlags= []
        f_sfp= self.hw.getNode("io.csr.ctrl.rst").read()
        self.hw.dispatch()
        myFlags.append(int(f_sfp))

        f_hdmi= self.hw.getNode("io.csr.ctrl.soft_rst").read()
        self.hw.dispatch()
        myFlags.append(int(f_hdmi))

        f_upssfp= self.hw.getNode("io.csr.ctrl.nuke").read()
        self.hw.dispatch()
        myFlags.append(int(f_upssfp))

        return myFlags

    def ipb_readFrequency(self, channel):
        """Query the IPBus block to read the clock frequency. Channel can either be 0 (PLL) or 1 (CDR clock)"""
        """Not working?"""
        if  (0 <= channel <= 1):
            self.hw.getNode("io.freq.ctrl.chan_sel").write(channel)
            self.hw.dispatch()
            res= self.hw.getNode("io.freq.freq.valid").read()
            self.hw.dispatch()
            print "  valid frequency?", res
            if res:
                fread= self.hw.getNode("io.freq.freq.count").read()
                self.hw.dispatch()
                return fread
        else:
            print "channel must be comprised between 0 and 1"
            return 0

    def ipb_reset(self):
        """Reset the board"""
        print "  RESETTING firmware"
        cmd = int("0x1", 16)
        self.hw.getNode("io.csr.ctrl.rst").write(cmd)
        self.hw.dispatch()
        cmd = int("0x0", 16)
        self.hw.getNode("io.csr.ctrl.rst").write(cmd)
        self.hw.dispatch()

    def ipb_setLED(self, iLED, status):
        """LED on/off for the 3 indicators connected to FPGA"""
        if 0<= iLED <= 2:
            res= self.ipb_getLED()
            newState= self._set_bit(res, iLED, status)
            self.hw.getNode("io.csr.ctrl.leds").write(newState)
            self.hw.dispatch()

    def ipb_getLED(self):
        """LED status for the 3 indicators connected to FPGA"""
        res= self.hw.getNode("io.csr.ctrl.leds").read()
        self.hw.dispatch()
        return res

    def ipb_allLEDs(self):
        self.ipb_setLED(0, 1)
        self.ipb_setLED(1, 1)
        self.ipb_setLED(2, 1)
        self._LEDallOn()

##################################################################################################################################
##################################################################################################################################

    def initialize(self, verbose= False):
        print "--", self.dev_name, " INITIALIZING..."

    # READ CONTENT OF EPROM VIA I2C
        self._getSN()

    # CONFIGURE CLOCK
        doClock= True
        if doClock:
            clockfile= "./../../bitFiles/pc059_Si5345.txt"
            self._configureClock(clockfile, 1)
            self.zeClock.checkDesignID()
        self.zeClock.checkDesignID()
        iopower= self.zeClock.readRegister(0x0949, 1)
        print "  Si5345 IO power (REG 0x0949): 0x%X" % iopower[0]
        lol= self.zeClock.readRegister(0x000E, 1)
        print "  Si5345 LOL (REG 0x000E): 0x%X" % lol[0]
        los= self.zeClock.readRegister(0x000D, 1)
        print "  Si5345 OOF and LOS (REG 0x000D): 0x%X" % los[0]

    # INITIALIZE EQUALIZER EXPANDER
        #BANK 0
        self.exp_EQ.setOutputs(0, 0x00)
        res= self.exp_EQ.getInputs(0)
        print "\tEXP_EQ read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.exp_EQ.setOutputs(1, 0x00)
        res= self.exp_EQ.getInputs(1)
        print "\tEXP_EQ read back bank 1: 0x%X" % res[0]

    # INITIALIZE SFP EXPANDER
        #BANK 0
        self.exp_SFP.setOutputs(0, 0xFF)
        res= self.exp_SFP.getInputs(0)
        print "\tEXP_SFP read back bank 0: 0x%X" % res[0]
        #BANK 1
        self.exp_SFP.setOutputs(1, 0xFF)
        res= self.exp_SFP.getInputs(1)
        print "\tEXP_SFP read back bank 1: 0x%X" % res[0]

    # INITIALIZE LED EXPANDER
        #BANK0
        self.exp_LED.setOutputs(0, 0x00)
        res= self.exp_LED.getInputs(0)
        print "\tEXP_LED read back bank 0: 0x%X" % res[0]
        #BANK1
        self.exp_LED.setOutputs(1, 0x0F)
        res= self.exp_LED.getInputs(1)
        print "\tEXP_LED read back bank 1: 0x%X" % res[0]

    # DISABLE ALL CHANNELS FOR I2C multiplexer
        self.mux_I2C.disableAllChannels(True)
        print "\tI2C MUX (should be 0)", self.mux_I2C.getChannelStatus(True)

        print "  ", self.dev_name, " INITIALIZED"

        self.ipb_allLEDs()

##################################################################################################################################
##################################################################################################################################
    def start(self):
        print "--", self.dev_name, " STARTING..."
        #self._LEDselfcheck()
        #self._setEQ(iEQ, 3, True)
        #self._sfpEnable(3, True)
        #print bin(self._getSFPfault())
        self.ipb_setLED(1,1)

    # Reset board
        #self.ipb_reset()

    # Query status of reset dut_lines
        print "  RESET status [reset, soft_rst, nuke, pll_rst, mux_rst, i2c_rst]"
        print "\t", self.ipb_getResets()

    # Select one of the SFP ports downstream
        self._sfpSelect(3, 2, 0)

    # Initialize PRBS
        self.ipb_prbs_init()

    # Read frequency
        self.ipb_readFrequency(0)

    # Get get zflags
        print "  zFLAGS [SFP, HDMI, UPS_SFP]="
        print "\t", self.ipb_getzflags()




        print "  ", self.dev_name, " RUNNING"

##################################################################################################################################
##################################################################################################################################
    def stop(self):
        print "--", self.dev_name, " STOPPING..."

        print "  ", self.dev_name, " STOPPED"
