onbreak {quit -f}
onerror {quit -f}

vsim -t 1ps -lib xil_defaultlib mac_fifo_axi4_opt

do {wave.do}

view wave
view structure
view signals

do {mac_fifo_axi4.udo}

run -all

quit -force
