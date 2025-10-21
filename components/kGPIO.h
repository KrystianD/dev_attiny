#pragma once

#include <avr/io.h>
#include <avr/common.h>

#include <stdint.h>

#include <kdevice.h>

#define PORT_FROM_ADDRESS(addr) ((PORT_t*)addr)

template<uint16_t PortAddr, uint8_t Pin>
class kGPIO
{
	static constexpr PORT_t* Port() { return reinterpret_cast<PORT_t*>(PortAddr); }

public:
	constexpr void input() const { Port()->DIRCLR = _BV(Pin); }
	constexpr void pushPull() const { Port()->DIRSET = _BV(Pin); }
	constexpr void high() const { Port()->OUTSET = _BV(Pin); }
	constexpr void low() const { Port()->OUTCLR = _BV(Pin); }
	constexpr void toggle() const { Port()->OUTTGL = _BV(Pin); }
	constexpr bool read() const { return Port()->IN & _BV(Pin); }

	constexpr bool isHigh() const { return read(); }
	constexpr bool isLow() const { return !read(); }

	constexpr void setMode(PORT_ISC_t mode) const
	{
		register8_t* pin0 = &Port()->PIN0CTRL;
		register8_t* pinX = pin0 + Pin;
		*pinX = (*pinX & ~PORT_ISC_gm) | mode;
	}

	constexpr void pullUp(bool enabled = true) const
	{
		register8_t* pin0 = &Port()->PIN0CTRL;
		register8_t* pinX = pin0 + Pin;

		if (enabled)
			*pinX |= PORT_PULLUPEN_bm;
		else
			*pinX &= ~PORT_PULLUPEN_bm;
	}

	constexpr void set(bool enabled) const
	{
		if (enabled) high();
		else low();
	}

	constexpr void clearInterruptFlag() const
	{
		Port()->INTFLAGS = _BV(Pin);
	}
};
