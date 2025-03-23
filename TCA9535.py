# SPDX-FileCopyrightText: Copyright (c) 2024 Chris Burton
#
# SPDX-License-Identifier: MIT

"""
`TCA9535`
=======

CircuitPython library for TCA9535/PCA9535 16-bit I2C Multiplexers.

* Author(s): Chris Burton

Usage Notes
-----------
Inversion only applies when reading a pin.

"""

try:
    # This is only needed for typing
    from typing import Optional
    import busio
except ImportError:
    pass

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const
import digitalio

_TCA9535_DEFAULT_I2C_ADDR: int = const(0x20)                # Default I2C address
_TCA9535_REGISTER_INPUT_PORT0: int = const(0x00)            # Default XXXX XXXX
_TCA9535_REGISTER_INPUT_PORT1: int = const(0x01)	    # Default XXXX XXXX
_TCA9535_REGISTER_OUTPUT_PORT0: int = const(0x02)           # Default 1111 1111 
_TCA9535_REGISTER_OUTPUT_PORT1: int = const(0x03)           # Default 1111 1111
_TCA9535_REGISTER_INVERSION0: int = const(0x04)             # Default 0000 0000 (No inversion)
_TCA9535_REGISTER_INVERSION1: int = const(0x05)             # Default 0000 0000 (No inversion)
_TCA9535_REGISTER_CONFIGURATION0: int = const(0x06)         # Default 1111 1111 (All inputs)
_TCA9535_REGISTER_CONFIGURATION1: int = const(0x07)         # Default 1111 1111 (All inputs)

class TCA9535:
    def __init__(self, i2c: I2C, address: int = _TCA9535_DEFAULT_I2C_ADDR, reset: bool = True) -> None:
        self.i2c_device = I2CDevice(i2c, address)
        self._output0 = bytearray(1)
        self._output1 = bytearray(1)
        self._inversion0 = bytearray(1)
        self._inversion1 = bytearray(1)
        self._configuration0 = bytearray(1)
        self._configuration1 = bytearray(1)

        if reset:
            # Reset to all inputs, disable inversion, set outputs to 1.
		with self.i2c_device as i2c:
	                i2c.write( bytearray([_TCA9535_REGISTER_CONFIGURATION0, 0xFF]) )
			i2c.write( bytearray([_TCA9535_REGISTER_CONFIGURATION1, 0xFF]) )
	                i2c.write( bytearray([_TCA9535_REGISTER_INVERSION0, 0x00]) )
			i2c.write( bytearray([_TCA9535_REGISTER_INVERSION1, 0x00]) )
	                i2c.write( bytearray([_TCA9535_REGISTER_OUTPUT_PORT0, 0xFF]) )
			i2c.write( bytearray([_TCA9535_REGISTER_OUTPUT_PORT1, 0xFF]) )

        with self.i2c_device as i2c:
		i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_OUTPUT_PORT0, ]), self._output0 )
		i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_OUTPUT_PORT1, ]), self._output1 )
		i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_INVERSION0, ]), self._inversion0 )
		i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_INVERSION1, ]), self._inversion1 )
		i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_CONFIGURATION0, ]), self._configuration0 )
		i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_CONFIGURATION1, ]), self._configuration1 )

    def read_gpio(self) -> int:
        buf0 = bytearray(1)
        buf1 = bytearray(1)
        with self.i2c_device as i2c:
            i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_INPUT_PORT0, ]), buf0 )
            i2c.write_then_readinto( bytearray([_TCA9535_REGISTER_INPUT_PORT1, ]), buf1 )
        return (buf1[0]<<8)+buf0[0]

    def write_gpio(self, val: int) -> None:
        self._output0[0] = val & 0xFF
        self._output1[0] = (val >> 8) & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_TCA9535_REGISTER_OUTPUT_PORT0, self._output0[0], ]) )
            i2c.write( bytearray([_TCA9535_REGISTER_OUTPUT_PORT1, self._output1[0], ]) )

    def set_iodir(self, val: int) -> None:
        self._configuration0[0] = val & 0xFF
        self._configuration1[0] = (val >> 8) & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_TCA9535_REGISTER_CONFIGURATION0, self._configuration0[0]]) )
            i2c.write( bytearray([_TCA9535_REGISTER_CONFIGURATION1, self._configuration1[0]]) )

    def get_iodir(self) -> int:
        return (self._configuration1[0]<<8)+self._configuration0[0]

    def get_inv(self) -> int:
        return (self._inversion1[0]<<8)+self._inversion0[0]

    def set_inv(self, val: int) -> None: # Inversion only applies to inputs
        self._inversion0[0] = val & 0xFF
        self._inversion1[0] = (val >> 8) & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_TCA9535_REGISTER_INVERSION0, self._inversion0[0], ]) )
            i2c.write( bytearray([_TCA9535_REGISTER_INVERSION1, self._inversion1[0], ]) )

    def get_pin(self, pin: int) -> "DigitalInOut":
        assert 0<= pin <= 15
        return DigitalInOut(pin, self)

    def write_pin(self, pin: int, val: bool) -> None:
        if val:
            self.write_gpio(self.output | (1<<pin))
        else:
            self.write_gpio(self.output & ~(1<<pin))

    def read_pin(self, pin: int) -> bool:
        assert 0<= pin <= 15
        return ((self.read_gpio() >> pin) & 0x1) > 0

class DigitalInOut:
    def __init__(self, pin_number: int, tca: TCA9535) -> None:
        self._pin = pin_number
        self._tca = tca

    def switch_to_output(self, value: bool = False, **kwargs) -> None:
        self._tca.set_iodir( self._tca.get_iodir() & ~( 1<<self._pin ) )

    def switch_to_input(self, **kwargs) -> None:
        self._tca.set_iodir( self._tca.get_iodir() | ( 1<<self._pin ) )

    @property
    def value(self) -> bool:
		return (self._tca.read_gpio() & (1<<self._pin)) > 0

    @value.setter
    def value(self, val: bool) -> None:
        if val:
            self._tca.write_gpio( ((self._tca._output1[0]<<8)+self._tca._output0[0]) | ( 1<<self._pin ) )
        else:
            self._tca.write_gpio( ((self._tca._output1[0]<<8)+self._tca._output0[0]) & ~( 1<<self._pin ) )

    @property
    def direction(self) -> digitalio.Direction:
        if (self._tca.get_iodir() & (1<<self._pin)) > 0:
            return digitalio.Direction.INPUT
        else:
            return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self,val: digitalio.Direction) -> None:
        if val == digitalio.Direction.INPUT:
            self._tca.set_iodir( self._tca.get_iodir() | (1<<self._pin) )
        elif val == digitalio.Direction.OUTPUT:
            self._tca.set_iodir( self._tca.get_iodir() & ~(1<<self._pin) )
        else:
            raise ValueError("Expected INPUT or OUTPUT direction!")

    @property
    def invert_polarity(self) -> bool:
        return (self._xra.get_inv() & (1<<self._pin)) > 0

    @invert_polarity.setter
    def invert_polarity(self, val: bool) -> None:
        if val:
            self._tca.set_inv( self._tca.get_inv() | (1<<self._pin) )
        else:
            self._tca.set_inv( self._tca.get_inv() & ~(1<<self._pin) )
