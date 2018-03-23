---------------------------------------------------------------------------------
--
--   Copyright 2017 - Rutherford Appleton Laboratory and University of Bristol
--
--   Licensed under the Apache License, Version 2.0 (the "License");
--   you may not use this file except in compliance with the License.
--   You may obtain a copy of the License at
--
--       http://www.apache.org/licenses/LICENSE-2.0
--
--   Unless required by applicable law or agreed to in writing, software
--   distributed under the License is distributed on an "AS IS" BASIS,
--   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--   See the License for the specific language governing permissions and
--   limitations under the License.
--
--                                     - - -
--
--   Additional information about ipbus-firmare and the list of ipbus-firmware
--   contacts are available at
--
--       https://ipbus.web.cern.ch/ipbus
--
---------------------------------------------------------------------------------


-- Top-level design for ipbus demo
--
-- This version is for Enclustra AX3 module, using the RGMII PHY on the PM3 baseboard
--
-- You must edit this file to set the IP and MAC addresses
--
-- Dave Newbold, 4/10/16

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
library UNISIM;
use UNISIM.vcomponents.all;

use work.ipbus.ALL;

entity top is port(
		sysclk: in std_logic;
		leds: out std_logic_vector(3 downto 0); -- status LEDs on FPGA
		--cfg: in std_logic_vector(3 downto 0); -- switches
		rgmii_txd: out std_logic_vector(3 downto 0);
		rgmii_tx_ctl: out std_logic;
		rgmii_txc: out std_logic;
		rgmii_rxd: in std_logic_vector(3 downto 0);
		rgmii_rx_ctl: in std_logic;
		rgmii_rxc: in std_logic;
		phy_rstn: out std_logic;
        i2c_scl: inout std_logic; -- Main I2C clock line
        i2c_sda: inout std_logic; -- Main I2C data line
        i2c_reset: out std_logic; --Reset line for the expander serial lines
        rst_clk_cvcc: out std_logic; --Reset the Si5345 chip. Active low
        rst_i2cmux_cvcc: out std_logic; --Reset signal for the 1:8 I2C multiplexer. Active low
        ext_rst:out std_logic; --Reset signal sent to 0.1" header for external I2C. Active low
        led_fmc_disable: out std_logic_vector(2 downto 0); -- status LEDs on the SFP board
        sfp_los: in std_logic_vector(7 downto 0); -- "Loss of signal" from SFP cages (downstream)
        inmux_cvcc: out std_logic_vector(2 downto 0); -- Control pins to select the line connected to the input multiplexer
        clk_lol_cvcc: in std_logic; -- LOL sisgnal from the Si5345. Active LOW
        clk_intr_cvcc: in std_logic; -- Interrupt signal from the Si5345. Active LOW
        sfp_ups_los:in std_logic; -- LOS signal from the upstream SFP cage
        ups_cdr_los_cvcc: in std_logic; -- LOS signal from the upstream CDR
        mux_cdr_los_cvcc: in std_logic; -- LOS signal from the multiplexer CDR
        mux_cdr_lol_cvcc: in std_logic; -- LOL signal from the multiplexer CDR
        sfp_ups_fault_cvcc: in std_logic; -- FAULT signal from the upstream SFP
        sfp_ups_tx_disable_cvcc: out std_logic; -- TX disable signal for the upstream SFP
        ups_cdr_lol_cvcc: in  std_logic; -- LOL signal from the upstream CDR
        data_ffd_p: out std_logic_vector(2 downto 0); -- Differential pairs sending DATA to the flip-flops
        data_ffd_n: out std_logic_vector(2 downto 0); -- Differential pairs sending DATA to the flip-flops
        clkdata_fpga_p: in std_logic_vector(7 downto 0); -- Differential stream (CLK+DATA) from SFPs downstream
        clkdata_fpga_n: in std_logic_vector(7 downto 0); -- Differential stream (CLK+DATA) from SFPs downstream
        data_from_hdmi_p: in std_logic; -- Differential data from HDMI upstream
        data_from_hdmi_n: in std_logic; -- Differential data from HDMI upstream
        data_cdr_ups_p: in std_logic; -- Differential data from CDR upstream
        data_cdr_ups_n: in std_logic; -- Differential data from CDR upstream
        data_from_mux_p: in std_logic; -- Differential data from downstream multiplexer (via CDR)
        data_from_mux_n: in std_logic; -- Differential data from downstream multiplexer (via CDR)
        clk_gen_p: in  std_logic; -- Clock from Si5345
        clk_gen_n: in  std_logic; -- Clock from Si5345
        clk_from_mux_p: in  std_logic; -- Clock from multiplexer CDR
        clk_from_mux_n: in  std_logic; -- Clock from multiplexer CDR
        i2c_scl_sfp: inout std_logic; -- Secondary I2C clock line for SFP upstream
        i2c_sda_sfp: inout std_logic; -- Secondary I2C clock line for SFP upstream
        gpio_pins: out std_logic_vector(5 downto 0) -- general purpose pins. For now set as outputs for testing
	);

end top;

architecture rtl of top is

	signal clk_ipb, rst_ipb, nuke, soft_rst, phy_rst_e, userled: std_logic;
	signal mac_addr: std_logic_vector(47 downto 0);
	signal ip_addr: std_logic_vector(31 downto 0);
	signal ipb_out: ipb_wbus;
	signal ipb_in: ipb_rbus;
	signal inf_leds: std_logic_vector(1 downto 0);
	signal s_i2c_scl_enb         : std_logic; -- Signal for main I2C master
    signal s_i2c_sda_enb         : std_logic; -- Signal for main I2C master
    signal s_i2c_scl_sfp_enb         : std_logic; -- Signal for secondary I2C master
    signal s_i2c_sda_sfp_enb         : std_logic; -- Signal for secondary I2C master
    signal clk_gen : std_logic; --signal for the clock from Si5345
	
    
	
begin

-- Assign values to constant signals here (even if just temporary)
    rst_clk_cvcc <= '1';
    rst_i2cmux_cvcc <= '1';
    ext_rst <= '1';
    led_fmc_disable <= not ('0' & '1' & '0');
    gpio_pins <= ('0' & '1' & '0' & sysclk & '0' & clk_gen);
    inmux_cvcc <= ('0' & '0' & '0');
    sfp_ups_tx_disable_cvcc <= '0';
    

--    i2c_scl_b <= '0' when (s_i2c_scl_enb = '0') else 'Z';
--    i2c_sda_b <= '0' when (s_i2c_sda_enb = '0') else 'Z';
--    i2c_reset <= '1';

-- Infrastructure

	infra: entity work.enclustra_ax3_pm3_infra
		port map(
			sysclk => sysclk,
			clk_ipb_o => clk_ipb,
			rst_ipb_o => rst_ipb,
			rst125_o => phy_rst_e,
			nuke => nuke,
			soft_rst => soft_rst,
			leds => inf_leds,
			rgmii_txd => rgmii_txd,
			rgmii_tx_ctl => rgmii_tx_ctl,
			rgmii_txc => rgmii_txc,
			rgmii_rxd => rgmii_rxd,
			rgmii_rx_ctl => rgmii_rx_ctl,
			rgmii_rxc => rgmii_rxc,
			mac_addr => mac_addr,
			ip_addr => ip_addr,
			ipb_in => ipb_in,
			ipb_out => ipb_out
		);
		
	leds <= not ('0' & userled & inf_leds);
	phy_rstn <= not phy_rst_e;
		
	--mac_addr <= X"020ddba1151" & not cfg; -- Careful here, arbitrary addresses do not always work
	mac_addr <= X"020ddba11511" ; -- Careful here, arbitrary addresses do not always work
	--ip_addr <= X"c0a8c81" & not cfg; -- 192.168.200.16+n
	ip_addr <= X"c0a8c81C"; -- 192.168.200.28 (hardwired for now)

-- ipbus slaves live in the entity below, and can expose top-level ports
-- The ipbus fabric is instantiated within.

    i2c_scl <= '0' when (s_i2c_scl_enb = '0') else 'Z';
    i2c_sda <= '0' when (s_i2c_sda_enb = '0') else 'Z';
    i2c_scl_sfp <= '0' when (s_i2c_scl_sfp_enb = '0') else 'Z';
    i2c_sda_sfp <= '0' when (s_i2c_sda_sfp_enb = '0') else 'Z';
    

	slaves: entity work.ipbus_fanout_slaves
		port map(
			ipb_clk => clk_ipb,
			ipb_rst => rst_ipb,
			ipb_in => ipb_out,
			ipb_out => ipb_in,
			nuke => nuke,
			soft_rst => soft_rst,
			userled => userled,
			i2c_scl_b => i2c_scl,
            i2c_sda_b => i2c_sda,
            i2c_scl_sfp_b => i2c_scl_sfp,
            i2c_sda_sfp_b => i2c_sda_sfp,
            i2c_rst_b => i2c_reset,
            i2c_scl_enb_o => s_i2c_scl_enb,
            i2c_sda_enb_o => s_i2c_sda_enb,
            i2c_scl_enb_sfp_o => s_i2c_scl_sfp_enb,
            i2c_sda_enb_sfp_o => s_i2c_sda_sfp_enb
		);
	
	output_buffers_loop: for iBuf in 0 to 2 generate
        OBUFDS_inst: OBUFDS
        generic map(
            IOSTANDARD => "DEFAULT")
            port map(
            O =>  data_ffd_p(iBuf),--Diff_poutput(connectdirectlytotop-levelport)
            OB => data_ffd_n(iBuf),--Diff_noutput(connectdirectlytotop-levelport)
            I =>  '0' --Bufferinput
        );
    end generate output_buffers_loop;
    
    input_buffers_loop: for iBuf in 0 to 7 generate
        IBUFDS_inst: IBUFDS
        generic map(
            IOSTANDARD => "DEFAULT",
            DIFF_TERM => TRUE)        
        port map(
            O => open,
            I => clkdata_fpga_p(iBuf),
            IB => clkdata_fpga_n(iBuf)   
        );
                
    end generate input_buffers_loop;
    
    IBUFDS_hdmi: IBUFDS
        generic map(
            IOSTANDARD => "DEFAULT",
            DIFF_TERM => TRUE)        
        port map(
            O => open,
            I => data_from_hdmi_p,
            IB => data_from_hdmi_n   
        );
        
    IBUFDS_CDR_UPS: IBUFDS
        generic map(
            IOSTANDARD => "DEFAULT",
            DIFF_TERM => TRUE)        
        port map(
            O => open,
            I => data_cdr_ups_p,
            IB => data_cdr_ups_n   
        );    

    IBUFDS_MUX: IBUFDS
        generic map(
            IOSTANDARD => "DEFAULT",
            DIFF_TERM => TRUE)        
        port map(
            O => open,
            I => data_from_mux_p,
            IB => data_from_mux_n   
        );
        
    IBUFDS_CLK_GEN: IBUFGDS
            generic map(
                IOSTANDARD => "DEFAULT",
                DIFF_TERM => TRUE)        
            port map(
                O => clk_gen,
                I => clk_gen_p,
                IB => clk_gen_n   
            );   
                  
    IBUFDS_CLK_FROM_MUX: IBUFGDS
            generic map(
                IOSTANDARD => "DEFAULT",
                DIFF_TERM => TRUE)        
            port map(
                O => open,
                I => clk_from_mux_p,
                IB => clk_from_mux_n   
            );         

end rtl;
