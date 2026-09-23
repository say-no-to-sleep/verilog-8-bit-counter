<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This design is an 8-bit counter with an asynchronous reset, a synchronous load input, and tri-state output control. The counter increments on each clock edge while COUNT_EN is high, and a value can be loaded into the counter when LOAD is asserted. The shared UIO bus acts as an input bus when OE is low and as an output bus when OE is high, allowing the current count to be driven onto the pins when enabled.

## How to test

Reset it, set COUNT_EN to count up, and watch uo_out. To load a value, set OE=0, put the value on the uio pins, set LOAD=1, and pulse the clock.

## External hardware

none
