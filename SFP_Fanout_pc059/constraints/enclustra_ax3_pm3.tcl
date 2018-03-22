#-------------------------------------------------------------------------------
#
#   Copyright 2017 - Rutherford Appleton Laboratory and University of Bristol
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#                                     - - -
#
#   Additional information about ipbus-firmare and the list of ipbus-firmware
#   contacts are available at
#
#       https://ipbus.web.cern.ch/ipbus
#
#-------------------------------------------------------------------------------


set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]

proc false_path {patt clk} {
    set p [get_ports -quiet $patt -filter {direction != out}]
    if {[llength $p] != 0} {
        set_input_delay 0 -clock [get_clocks $clk] [get_ports $patt -filter {direction != out}]
        set_false_path -from [get_ports $patt -filter {direction != out}]
    }
    set p [get_ports -quiet $patt -filter {direction != in}]
    if {[llength $p] != 0} {
       	set_output_delay 0 -clock [get_clocks $clk] [get_ports $patt -filter {direction != in}]
	    set_false_path -to [get_ports $patt -filter {direction != in}]
	}
}

# System clock (50MHz)
create_clock -period 20.000 -name sysclk [get_ports sysclk]

set_false_path -through [get_pins infra/clocks/rst_reg/Q]
set_false_path -through [get_nets infra/clocks/nuke_i]

set_property IOSTANDARD LVCMOS25 [get_ports sysclk]
#set_property IOSTANDARD LVCMOS33 [get_ports sysclk]
set_property PACKAGE_PIN P17 [get_ports sysclk]

set_property IOSTANDARD LVCMOS25 [get_ports {leds[*]}]
#set_property IOSTANDARD LVCMOS33 [get_ports {leds[*]}]
set_property SLEW SLOW [get_ports {leds[*]}]
set_property PACKAGE_PIN M16 [get_ports {leds[0]}]
set_property PACKAGE_PIN M17 [get_ports {leds[1]}]
set_property PACKAGE_PIN L18 [get_ports {leds[2]}]
set_property PACKAGE_PIN M18 [get_ports {leds[3]}]
false_path {leds[*]} sysclk

set_property IOSTANDARD LVCMOS25 [get_ports {rgmii_* phy_rstn}]
#set_property IOSTANDARD LVCMOS33 [get_ports {rgmii_* phy_rstn}]
set_property PACKAGE_PIN R18 [get_ports {rgmii_txd[0]}]
set_property PACKAGE_PIN T18 [get_ports {rgmii_txd[1]}]
set_property PACKAGE_PIN U17 [get_ports {rgmii_txd[2]}]
set_property PACKAGE_PIN U18 [get_ports {rgmii_txd[3]}]
set_property PACKAGE_PIN T16 [get_ports {rgmii_tx_ctl}]
set_property PACKAGE_PIN N16 [get_ports {rgmii_txc}]
set_property PACKAGE_PIN U16 [get_ports {rgmii_rxd[0]}]
set_property PACKAGE_PIN V17 [get_ports {rgmii_rxd[1]}]
set_property PACKAGE_PIN V15 [get_ports {rgmii_rxd[2]}]
set_property PACKAGE_PIN V16 [get_ports {rgmii_rxd[3]}]
set_property PACKAGE_PIN R16 [get_ports {rgmii_rx_ctl}]
set_property PACKAGE_PIN T14 [get_ports {rgmii_rxc}]
set_property PACKAGE_PIN M13 [get_ports {phy_rstn}]
false_path {phy_rstn} sysclk

## Reset signal for the Si5345 clock generator
#set_property IOSTANDARD LVCMOS33 [get_ports rst_clk_cvcc]
set_property IOSTANDARD LVCMOS25 [get_ports rst_clk_cvcc]
set_property PACKAGE_PIN T6 [get_ports rst_clk_cvcc]

## Reset signal for the 1:8 I2C multiplexer
#set_property IOSTANDARD LVCMOS33 [get_ports rst_i2cmux_cvcc]
set_property IOSTANDARD LVCMOS25 [get_ports rst_i2cmux_cvcc]
set_property PACKAGE_PIN T1 [get_ports rst_i2cmux_cvcc]

## Reset signal sent to 0.1" header for external I2C
#set_property IOSTANDARD LVCMOS33 [get_ports ext_rst]
set_property IOSTANDARD LVCMOS25 [get_ports ext_rst]
set_property PACKAGE_PIN C7 [get_ports ext_rst]

## Spare LED controls
#set_property IOSTANDARD LVCMOS33 [get_ports {led_fmc_disable[*]}]
set_property IOSTANDARD LVCMOS25 [get_ports {led_fmc_disable[*]}]
set_property PACKAGE_PIN E7 [get_ports {led_fmc_disable[0]}]
set_property PACKAGE_PIN H6 [get_ports {led_fmc_disable[1]}]
set_property PACKAGE_PIN H1 [get_ports {led_fmc_disable[2]}]

## Spare LED controls
#set_property IOSTANDARD LVCMOS33 [get_ports {gpio_pins[*]}]
set_property IOSTANDARD LVCMOS25 [get_ports {gpio_pins[*]}]
set_property PACKAGE_PIN P4 [get_ports {gpio_pins[0]}]
set_property PACKAGE_PIN P3 [get_ports {gpio_pins[1]}]
set_property PACKAGE_PIN P2 [get_ports {gpio_pins[2]}]
set_property PACKAGE_PIN R2 [get_ports {gpio_pins[3]}]
set_property PACKAGE_PIN U4 [get_ports {gpio_pins[4]}]
set_property PACKAGE_PIN U3 [get_ports {gpio_pins[5]}]

## LOS signals from SFP cages (downstream)
#set_property IOSTANDARD LVCMOS33 [get_ports {sfp_los[*]}]
set_property IOSTANDARD LVCMOS25 [get_ports {sfp_los[*]}]
set_property PACKAGE_PIN R8 [get_ports {sfp_los[0]}]
set_property PACKAGE_PIN T8 [get_ports {sfp_los[1]}]
set_property PACKAGE_PIN E2 [get_ports {sfp_los[2]}]
set_property PACKAGE_PIN D2 [get_ports {sfp_los[3]}]
set_property PACKAGE_PIN J3 [get_ports {sfp_los[4]}]
set_property PACKAGE_PIN J2 [get_ports {sfp_los[5]}]
set_property PACKAGE_PIN M4 [get_ports {sfp_los[6]}]
set_property PACKAGE_PIN N4 [get_ports {sfp_los[7]}]

## Signals from/to upstream SFP cage
#set_property IOSTANDARD LVCMOS33 [get_ports {sfp_ups_los}]
set_property IOSTANDARD LVCMOS25 [get_ports {sfp_ups_los}]
set_property PACKAGE_PIN F1 [get_ports {sfp_ups_los}]

#set_property IOSTANDARD LVCMOS33 [get_ports {sfp_ups_fault_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {sfp_ups_fault_cvcc}]
set_property PACKAGE_PIN L3 [get_ports {sfp_ups_fault_cvcc}]

#set_property IOSTANDARD LVCMOS33 [get_ports {sfp_ups_tx_disable_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {sfp_ups_tx_disable_cvcc}]
set_property PACKAGE_PIN E1 [get_ports {sfp_ups_tx_disable_cvcc}]

## Control signals for the INPUT multiplexer 8:1
#set_property IOSTANDARD LVCMOS33 [get_ports {inmux_cvcc[*]}]
set_property IOSTANDARD LVCMOS25 [get_ports {inmux_cvcc[*]}]
set_property PACKAGE_PIN N2 [get_ports {inmux_cvcc[0]}]
set_property PACKAGE_PIN N1 [get_ports {inmux_cvcc[1]}]
set_property PACKAGE_PIN R1 [get_ports {inmux_cvcc[2]}]

## Control signals from Si5345
#set_property IOSTANDARD LVCMOS33 [get_ports {clk_lol_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {clk_lol_cvcc}]
set_property PACKAGE_PIN K3 [get_ports {clk_lol_cvcc}]

#set_property IOSTANDARD LVCMOS33 [get_ports {clk_intr_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {clk_intr_cvcc}]
set_property PACKAGE_PIN D8 [get_ports {clk_intr_cvcc}]

## Signals from the upstream CDR
#set_property IOSTANDARD LVCMOS33 [get_ports {ups_cdr_los_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {ups_cdr_los_cvcc}]
set_property PACKAGE_PIN F4 [get_ports {ups_cdr_los_cvcc}]

#set_property IOSTANDARD LVCMOS33 [get_ports {ups_cdr_lol_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {ups_cdr_lol_cvcc}]
set_property PACKAGE_PIN F3 [get_ports {ups_cdr_lol_cvcc}]

# Differential data from upstream CDR
set_property IOSTANDARD LVDS_25 [get_ports {data_cdr_ups_p}]
set_property PACKAGE_PIN M3 [get_ports {data_cdr_ups_p}]
set_property PACKAGE_PIN M2 [get_ports {data_cdr_ups_n}]

# Differential data from downstream multiplexer (via CDR)
set_property IOSTANDARD LVDS_25 [get_ports {data_from_mux_p}]
set_property PACKAGE_PIN R6 [get_ports {data_from_mux_p}]
set_property PACKAGE_PIN R5 [get_ports {data_from_mux_n}]

## Signal from the multiplexer CDR
#set_property IOSTANDARD LVCMOS33 [get_ports {mux_cdr_los_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {mux_cdr_los_cvcc}]
set_property PACKAGE_PIN C6 [get_ports {mux_cdr_los_cvcc}]

#set_property IOSTANDARD LVCMOS33 [get_ports {mux_cdr_lol_cvcc}]
set_property IOSTANDARD LVCMOS25 [get_ports {mux_cdr_lol_cvcc}]
set_property PACKAGE_PIN C5 [get_ports {mux_cdr_lol_cvcc}]

## Differential data to flip-flops
set_property IOSTANDARD LVDS_25 [get_ports {data_ffd_p[*]}]
set_property PACKAGE_PIN L6 [get_ports {data_ffd_p[0]}]
set_property PACKAGE_PIN L5 [get_ports {data_ffd_n[0]}]
set_property PACKAGE_PIN M6 [get_ports {data_ffd_p[1]}]
set_property PACKAGE_PIN N6 [get_ports {data_ffd_n[1]}]
set_property PACKAGE_PIN L1 [get_ports {data_ffd_p[2]}]
set_property PACKAGE_PIN M1 [get_ports {data_ffd_n[2]}]

## Differential stream (clk+data) from the downstream SFPs 
set_property IOSTANDARD LVDS_25 [get_ports {clkdata_fpga_p[*]}]
set_property PACKAGE_PIN U1 [get_ports {clkdata_fpga_p[0]}]
set_property PACKAGE_PIN V1 [get_ports {clkdata_fpga_n[0]}]
set_property PACKAGE_PIN K5 [get_ports {clkdata_fpga_p[1]}]
set_property PACKAGE_PIN L4 [get_ports {clkdata_fpga_n[1]}]
set_property PACKAGE_PIN G4 [get_ports {clkdata_fpga_p[2]}]
set_property PACKAGE_PIN G3 [get_ports {clkdata_fpga_n[2]}]
set_property PACKAGE_PIN C2 [get_ports {clkdata_fpga_p[3]}]
set_property PACKAGE_PIN C1 [get_ports {clkdata_fpga_n[3]}]
set_property PACKAGE_PIN G6 [get_ports {clkdata_fpga_p[4]}]
set_property PACKAGE_PIN F6 [get_ports {clkdata_fpga_n[4]}]
set_property PACKAGE_PIN J4 [get_ports {clkdata_fpga_p[5]}]
set_property PACKAGE_PIN H4 [get_ports {clkdata_fpga_n[5]}]
set_property PACKAGE_PIN K2 [get_ports {clkdata_fpga_p[6]}]
set_property PACKAGE_PIN K1 [get_ports {clkdata_fpga_n[6]}]
set_property PACKAGE_PIN B1 [get_ports {clkdata_fpga_p[7]}]
set_property PACKAGE_PIN A1 [get_ports {clkdata_fpga_n[7]}]

## Differential data from HDMI upstream
set_property IOSTANDARD LVDS_25 [get_ports {data_from_hdmi_p}]
set_property PACKAGE_PIN C4 [get_ports {data_from_hdmi_p}]
set_property PACKAGE_PIN B4 [get_ports {data_from_hdmi_n}]

## Clock from Si5345
set_property IOSTANDARD LVDS_25 [get_ports {clk_gen_p}]
set_property PACKAGE_PIN N5 [get_ports {clk_gen_p}]
set_property PACKAGE_PIN P5 [get_ports {clk_gen_n}]

## Clock from multiplexer CDR
set_property IOSTANDARD LVDS_25 [get_ports {clk_from_mux_p}]
set_property PACKAGE_PIN E3 [get_ports {clk_from_mux_p}]
set_property PACKAGE_PIN D3 [get_ports {clk_from_mux_n}]
 