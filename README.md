# CircuitPython_TCA9535
CircuitPython library for TCA9535 and PCA9535 16-bit I2C Multiplexers

```
expander = TCA8535.TCA8535(i2c, address=0x20)
pin5 = expander.get_pin(5)
pin12 = expander.get_pin(12)

pin5.direction=digitalio.Direction.OUTPUT
pin5.value=True
```

Address Reference
-----------------

| A2 | A1 | A0 | Address |
| -- | -- | -- | ------- |
| L | L | L | 32 (decimal) 0x20 (hexadecimal) |
| L | L | H | 33 (decimal) 0x21 (hexadecimal) |
| L | H | L | 34 (decimal) 0x22 (hexadecimal) |
| L | H | H | 35 (decimal) 0x23 (hexadecimal) |
| H | L | L | 36 (decimal) 0x24 (hexadecimal) |
| H | L | H | 37 (decimal) 0x25 (hexadecimal) |
| H | H | L | 38 (decimal) 0x26 (hexadecimal) |
| H | H | H | 39 (decimal) 0x27 (hexadecimal) |
