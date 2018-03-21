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


-- ipbus_example
--
-- selection of different IPBus slaves without actual function,
-- just for performance evaluation of the IPbus/uhal system
--
-- Kristian Harder, March 2014
-- based on code by Dave Newbold, February 2011

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use work.ipbus.all;
use work.ipbus_reg_types.all;
use work.ipbus_decode_fanout.all;
--use work.ipbus_decode_ipbus_example.all;

entity ipbus_fanout_slaves is
    generic(
        constant FW_VERSION : unsigned(31 downto 0):= X"059a0008" -- Firmware revision. Remember to change this as needed.
    );
	port(
		ipb_clk: in std_logic;
		ipb_rst: in std_logic;
		ipb_in: in ipb_wbus;
		ipb_out: out ipb_rbus;
		nuke: out std_logic;
		soft_rst: out std_logic;
		userled: out std_logic;
		i2c_scl_b: in std_logic; -- I2C clock line
        i2c_sda_b: in std_logic; -- I2C data line
        i2c_rst_b: out std_logic; --Reset line for the expander serial lines
        i2c_scl_enb_o : OUT    std_logic;
        i2c_sda_enb_o : OUT    std_logic
	);

end ipbus_fanout_slaves;

architecture rtl of ipbus_fanout_slaves is

	signal ipbw: ipb_wbus_array(N_SLAVES - 1 downto 0);
	signal ipbr: ipb_rbus_array(N_SLAVES - 1 downto 0);
	signal ctrl, stat: ipb_reg_v(0 downto 0);
	signal s_i2c_scl_enb         : std_logic;
    signal s_i2c_sda_enb         : std_logic;
	
    COMPONENT i2c_master
    PORT (
       i2c_scl_i     : IN     std_logic;
       i2c_sda_i     : IN     std_logic;
       ipbus_clk_i   : IN     std_logic;
       ipbus_i       : IN     ipb_wbus;
       ipbus_reset_i : IN     std_logic;
       i2c_scl_enb_o : OUT    std_logic;
       i2c_sda_enb_o : OUT    std_logic;
       ipbus_o       : OUT    ipb_rbus
    );
    END COMPONENT i2c_master;
    FOR ALL : i2c_master USE ENTITY work.i2c_master;

begin

-- ipbus address decode
		
	fabric: entity work.ipbus_fabric_sel
    generic map(
    	NSLV => N_SLAVES,
    	SEL_WIDTH => IPBUS_SEL_WIDTH)
    port map(
      ipb_in => ipb_in,
      ipb_out => ipb_out,
      sel => ipbus_sel_ipbus_example(ipb_in.ipb_addr),
      ipb_to_slaves => ipbw,
      ipb_from_slaves => ipbr
    );

-- Slave 0: id / rst reg

	slave0: entity work.ipbus_ctrlreg_v
		port map(
			clk => ipb_clk,
			reset => ipb_rst,
			ipbus_in => ipbw(N_SLV_CTRL_REG),
			ipbus_out => ipbr(N_SLV_CTRL_REG),
			d => stat,
			q => ctrl
		);
		
		--stat(0) <= X"abcdfedc";
		stat(0) <= std_logic_vector(FW_VERSION);-- <-Let's use this as firmware revision number
		soft_rst <= ctrl(0)(0);
		nuke <= ctrl(0)(1);

-- Slave 1: register

	slave1: entity work.ipbus_reg_v
		port map(
			clk => ipb_clk,
			reset => ipb_rst,
			ipbus_in => ipbw(N_SLV_REG),
			ipbus_out => ipbr(N_SLV_REG),
			q => open
		);

---- Slave 2: 1kword RAM

--	slave4: entity work.ipbus_ram
--		generic map(ADDR_WIDTH => 10)
--		port map(
--			clk => ipb_clk,
--			reset => ipb_rst,
--			ipbus_in => ipbw(N_SLV_RAM),
--			ipbus_out => ipbr(N_SLV_RAM)
--		);
	
---- Slave 3: peephole RAM

--	slave5: entity work.ipbus_peephole_ram
--		generic map(ADDR_WIDTH => 10)
--		port map(
--			clk => ipb_clk,
--			reset => ipb_rst,
--			ipbus_in => ipbw(N_SLV_PRAM),
--			ipbus_out => ipbr(N_SLV_PRAM)
--		);

    -- I2C master to control lines to slaves on board

    --i2c_scl_b <= '0' when (s_i2c_scl_enb = '0') else 'Z';
    --i2c_sda_b <= '0' when (s_i2c_sda_enb = '0') else 'Z';
    i2c_rst_b <= '1';
		
    I3 : i2c_master
    PORT MAP (
        i2c_scl_i     => i2c_scl_b,
        i2c_sda_i     => i2c_sda_b,
        ipbus_clk_i   => ipb_clk,
        ipbus_i       => ipbw(N_SLV_I2C_0),
        ipbus_reset_i => ipb_rst,
        i2c_scl_enb_o => s_i2c_scl_enb,
        i2c_sda_enb_o => s_i2c_sda_enb,
        ipbus_o       => ipbr(N_SLV_I2C_0)
    );
    i2c_scl_enb_o <= s_i2c_scl_enb;
    i2c_sda_enb_o <= s_i2c_sda_enb;

end rtl;
