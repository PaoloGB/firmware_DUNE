#set_property IOSTANDARD LVCMOS33 [get_ports i2c_reset]
set_property IOSTANDARD LVCMOS25 [get_ports i2c_reset]
set_property PACKAGE_PIN R7 [get_ports i2c_reset]

#set_property IOSTANDARD LVCMOS33 [get_ports i2c_scl]
set_property IOSTANDARD LVCMOS25 [get_ports i2c_scl]
set_property PACKAGE_PIN N17 [get_ports i2c_scl]

#set_property IOSTANDARD LVCMOS33 [get_ports i2c_sda]
set_property IOSTANDARD LVCMOS25 [get_ports i2c_sda]
set_property PACKAGE_PIN P18 [get_ports i2c_sda]


## Secondary I2C core for SFP upstream
set_property IOSTANDARD LVCMOS25 [get_ports i2c_scl_sfp]
set_property PACKAGE_PIN G2 [get_ports i2c_scl_sfp]

set_property IOSTANDARD LVCMOS25 [get_ports i2c_sda_sfp]
set_property PACKAGE_PIN H2 [get_ports i2c_sda_sfp]



# -------------------------------------------------------------------------------------------------



#DEBUG PROBES





