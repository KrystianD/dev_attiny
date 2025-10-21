#pragma once

#include <avr/io.h>
#include <avr/common.h>

#include <stdint.h>

#include <kdevice.h>

template<uint16_t USART>
class kSerial
{
public:
	static constexpr USART_t* Device() { return reinterpret_cast<USART_t*>(USART); }

	void put(char c)
	{
		loop_until_bit_is_set(Device()->STATUS, USART_DREIF_bp);

		Device()->TXDATAL = c;
	}

	bool available()
	{
		return Device()->STATUS & USART_RXCIF_bm;
	}

	char get()
	{
		return Device()->RXDATAL;
	}

	static constexpr int IRQ1()
	{
		return USART1_RXC_vect_num;
	}
};
