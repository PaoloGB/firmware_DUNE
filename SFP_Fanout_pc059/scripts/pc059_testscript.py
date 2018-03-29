# -*- coding: utf-8 -*-

#IMPORT THE LIBRARIES WRITTEN FOR AIDA TLU
#CHANGE THIS PATH ACCORDING TO WHERE THE FILES ARE SAVED ON
#LOCAL MACHINE
import sys
sys.path.append('/users/phpgb/workspace/myFirmware/AIDA/packages')

import uhal
from I2CuHal2 import I2CCore
import time
#import miniTLU
from si5345 import si5345
from AD5665R import AD5665R
from PCA9539PW import PCA9539PW
from E24AA025E48T import E24AA025E48T
from PCA9548ADW import PCA9548ADW
from ADN2814ACPZ import ADN2814ACPZ

manager = uhal.ConnectionManager("file://./pc059_connection.xml")
hw = manager.getDevice("sfpfanout")

# hw.getNode("A").write(255)
#reg = hw.getNode("version").read()
#hw.dispatch()
#print "CHECK REG= ", hex(reg)


# #Main I2C core
print ("Instantiating master I2C core:")
#master_I2C= I2CCore(hw, 12800, 10, "i2c_master", None)
master_I2C= I2CCore(hw, 10, 5, "io.i2c", None)
master_I2C.state()

# #Secondary I2C core for SFP
#print ("Instantiating secondary I2C core (for upstream SFP):")
#sfp_I2C= I2CCore(hw, 12800, 10, "i2c_sfp", None)
#sfp_I2C.state()


#
# #######################################
enableCore= True #Only need to run this once, after power-up
if (enableCore):
   mystop=True
   print "  Write RegDir to set I/O[7] to output:"
   myslave= 0x21
   mycmd= [0x01, 0x7F]
   nwords= 1
   master_I2C.write(myslave, mycmd, mystop)

   mystop=False
   mycmd= [0x01]
   master_I2C.write(myslave, mycmd, mystop)
   res= master_I2C.read( myslave, nwords)
   print "\tPost RegDir: ", res

#######################################################
#EEPROM BEGIN
doEeprom= True
if doEeprom:
  zeEEPROM= E24AA025E48T(master_I2C, 0x57)
  res=zeEEPROM.readEEPROM(0xfa, 6)
  result="  EEPROM ID:\n\t"
  for iaddr in res:
      result+="%02x "%(iaddr)
  print result
#EEPROM END

#######################################################
#CLOCK CONFIGURATION BEGIN
doClock = False
zeClock=si5345(master_I2C, 0x68)
res= zeClock.getDeviceVersion()
if doClock:
  #zeClock.setPage(0, True)
  #zeClock.getPage(True)
  clkRegList= zeClock.parse_clk("./../../bitFiles/pc059_Si5345.txt")
  zeClock.writeConfiguration(clkRegList, True)######
  zeClock.writeRegister(0x0536, [0x0B]) #Configures manual switch of inputs
  zeClock.writeRegister(0x0949, [0x0F]) #Enable all inputs
  zeClock.writeRegister(0x052A, [0x05]) #Configures source of input
zeClock.checkDesignID()
iopower= zeClock.readRegister(0x0949, 1)
print "  Clock IO power (REG 0x0949): 0x%X" % iopower[0]
lol= zeClock.readRegister(0x000E, 1)
print "  Clock LOL (REG 0x000E): 0x%X" % lol[0]
los= zeClock.readRegister(0x000D, 1)
print "  Clock OOF and LOS (REG 0x000D): 0x%X" % los[0]
#CLOCK CONFIGURATION END

#######################################################
# #I2C EXPANDER CONFIGURATION BEGIN
# IC28 EQUALIZER EXPANDER
doIC28= True
if doIC28:
  IC28=PCA9539PW(master_I2C, 0x74)
  #BANK 0
  IC28.setInvertReg(0, 0x00)# 0= normal
  IC28.setIOReg(0, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
  IC28.setOutputs(0, 0xFF)
  res= IC28.getInputs(0)
  print "IC28 read back bank 0: 0x%X" % res[0]
  #BANK 1
  IC28.setInvertReg(1, 0x00)# 0= normal
  IC28.setIOReg(1, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
  IC28.setOutputs(1, 0xFF)
  res= IC28.getInputs(1)
  print "IC28 read back bank 1: 0x%X" % res[0]
# #I2C EXPANDER CONFIGURATION END

#######################################################
# #I2C EXPANDER CONFIGURATION BEGIN
# IC29 SFP SIGNALS EXPANDER
doIC29= True
if doIC29:
  IC29=PCA9539PW(master_I2C, 0x75)
  #BANK 0
  IC29.setInvertReg(0, 0x00)# 0= normal
  IC29.setIOReg(0, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
  IC29.setOutputs(0, 0xFF)
  res= IC29.getInputs(0)
  print "IC29 read back bank 0: 0x%X" % res[0]
  #BANK 1
  IC29.setInvertReg(1, 0x00)# 0= normal
  IC29.setIOReg(1, 0xFF)# FF= input <<<<<<<<<<<<<<<<<<<
  IC29.setOutputs(1, 0xFF)
  res= IC29.getInputs(1)
  print "IC29 read back bank 1: 0x%X" % res[0]
# #I2C EXPANDER CONFIGURATION END

#######################################################
# #I2C EXPANDER CONFIGURATION BEGIN
# IC27 MISC AND LED EXPANDER
doIC27= True
if doIC27:
  IC27=PCA9539PW(master_I2C, 0x76)
  #BANK 0
  IC27.setInvertReg(0, 0x00)# 0= normal
  IC27.setIOReg(0, 0x00)# 0= output (LED) <<<<<<<<<<<<<<<<<<<
  IC27.setOutputs(0, 0xAA)
  res= IC27.getInputs(0)
  print "IC27 read back bank 0: 0x%X" % res[0]
  #BANK 1
  IC27.setInvertReg(1, 0x00)# 0= normal
  IC27.setIOReg(1, 0x00)# 0= output <<<<<<<<<<<<<<<<<<<
  IC27.setOutputs(1, 0xFF)
  res= IC27.getInputs(1)
  print "IC27 read back bank 1: 0x%X" % res[0]
# #I2C EXPANDER CONFIGURATION END

#######################################################
# #I2C MULTIPLEXER BEGIN
# IC7 I2C MULTIPLEXER FOR SFPs
doIC7= True
if doIC7:
  IC7=PCA9548ADW(master_I2C, 0x73)
  IC7.disableAllChannels(True)
  print "  I2C MUX (should be 0)", IC7.getChannelStatus(True)
# #I2C MULTIPLEXER END

#######################################################
# #CDR UPSTREAM BEGIN
# IC26 CLOCK AND DATA RECOVERY CHIP
doIC26= True
if doIC26:
  IC26=ADN2814ACPZ(master_I2C, 0x40)
# #CDR UPSTREAM END

#######################################################
# #CDR MULTIPLEXER BEGIN
# IC26 CLOCK AND DATA RECOVERY CHIP
doIC6= True
if doIC6:
  IC6=ADN2814ACPZ(master_I2C, 0x60)
# #CDR MULTIPLEXER END
