# Tests for the 8-bit counter. Run with "make" inside the test folder.
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, Timer

LOAD = 1 << 0
OE = 1 << 1
COUNT_EN = 1 << 2


async def setup(dut):
    """Start the clock and reset the design."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())  # 100 kHz
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await FallingEdge(dut.clk)  # we always change inputs and check outputs on the falling edge


async def step(dut, n=1):
    """Let n rising clock edges happen, then stop at a falling edge so values are settled."""
    for _ in range(n):
        await FallingEdge(dut.clk)


@cocotb.test()
async def test_reset_value(dut):
    await setup(dut)
    assert int(dut.uo_out.value) == 0, "count should be 0 after reset"


@cocotb.test()
async def test_count_up(dut):
    await setup(dut)
    dut.ui_in.value = COUNT_EN
    for expected in range(1, 20):
        await step(dut)
        assert int(dut.uo_out.value) == expected, f"expected {expected}, got {int(dut.uo_out.value)}"


@cocotb.test()
async def test_hold_when_disabled(dut):
    await setup(dut)
    dut.ui_in.value = COUNT_EN
    await step(dut, 7)
    dut.ui_in.value = 0          # stop counting
    await step(dut, 10)
    assert int(dut.uo_out.value) == 7, "count should stay at 7 when COUNT_EN is 0"


@cocotb.test()
async def test_synchronous_load(dut):
    await setup(dut)
    dut.uio_in.value = 0xA5
    dut.ui_in.value = LOAD       # OE is 0, so the uio pins are inputs
    await Timer(1, unit="us")    # wait a bit, but NOT a clock edge
    assert int(dut.uo_out.value) == 0, "load must wait for a clock edge (synchronous)"
    await step(dut)
    assert int(dut.uo_out.value) == 0xA5, "count should be the loaded value"
    # Load beats counting if both are on
    dut.uio_in.value = 0x10
    dut.ui_in.value = LOAD | COUNT_EN
    await step(dut)
    assert int(dut.uo_out.value) == 0x10
    # Then keep counting from the loaded value
    dut.ui_in.value = COUNT_EN
    await step(dut, 3)
    assert int(dut.uo_out.value) == 0x13


@cocotb.test()
async def test_wraparound(dut):
    await setup(dut)
    dut.uio_in.value = 0xFE
    dut.ui_in.value = LOAD
    await step(dut)
    dut.ui_in.value = COUNT_EN
    await step(dut)
    assert int(dut.uo_out.value) == 0xFF
    await step(dut)
    assert int(dut.uo_out.value) == 0x00, "should wrap from 255 to 0"
    await step(dut)
    assert int(dut.uo_out.value) == 0x01


@cocotb.test()
async def test_tristate_output(dut):
    await setup(dut)
    dut.ui_in.value = COUNT_EN
    await step(dut, 42)
    dut.ui_in.value = 0
    await step(dut)
    # OE off: pins must be inputs (high impedance)
    assert int(dut.uio_oe.value) == 0x00, "uio pins should be released when OE=0"
    # OE on: pins drive the count
    dut.ui_in.value = OE
    await Timer(1, unit="us")
    assert int(dut.uio_oe.value) == 0xFF, "uio pins should be outputs when OE=1"
    assert int(dut.uio_out.value) == 42, "uio_out should show the count"


@cocotb.test()
async def test_asynchronous_reset(dut):
    await setup(dut)
    dut.ui_in.value = COUNT_EN
    await step(dut, 50)
    assert int(dut.uo_out.value) == 50
    # Pull reset low in the middle of the clock's low half, away from any rising edge
    await Timer(1, unit="us")
    dut.rst_n.value = 0
    await Timer(1, unit="us")    # still no rising edge has happened
    assert int(dut.uo_out.value) == 0, "reset should clear the count without waiting for the clock"
    dut.rst_n.value = 1