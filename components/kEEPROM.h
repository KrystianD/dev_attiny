#pragma once

#include <avr/io.h>
#include <avr/common.h>
#include <avr/eeprom.h>
#include <util/crc16.h>

#include <stdint.h>

#pragma pack(1)
template<typename T>
class EEPROMMemory
{
public:
	T get()
	{
		uint8_t calcCrc = crc8((uint8_t*)&storage + EEPROMStart, sizeof(T));

		if (calcCrc == getFromEEPROMAddress(crc)) {
			return getFromEEPROMAddress(storage);
		}
		else {
			return T();
		}
	}

	void set(T val)
	{
		uint8_t calcCrc = crc8((uint8_t*)&val, sizeof(T));

		eeprom_busy_wait();
		putToEEPROMAddress(crc, calcCrc);
		_PROTECTED_WRITE_SPM(NVMCTRL.CTRLA, CMD_ERWP);

		for (uint8_t i = 0; i < sizeof(T); i++) {
			eeprom_busy_wait();
			putToEEPROMAddress(((uint8_t*)&storage)[i], ((uint8_t*)&val)[i]);
			_PROTECTED_WRITE_SPM(NVMCTRL.CTRLA, CMD_ERWP);
		}

		eeprom_busy_wait();
	}

	static constexpr uint8_t CMD_ERWP = 0x03;

private:
	uint8_t crc;
	T storage;

	static constexpr uint16_t EEPROMStart = 0x1400;

	static uint8_t crc8(const uint8_t* data, uint8_t len)
	{
		uint8_t crc = 0;
		for (uint8_t i = 0; i < len; i++) {
			crc = _crc8_ccitt_update(crc, data[i]);
		}
		return crc;
	}

	template<typename T2>
	static T2 getFromEEPROMAddress(T2& addr)
	{
		return *(T2*)(((uint8_t*)&addr) + EEPROMStart);
	}
	template<typename T2>
	static void putToEEPROMAddress(T2& addr, T2 val)
	{
		*(T2*)(((uint8_t*)&addr) + EEPROMStart) = val;
	}
};
#pragma pack()

class EEPROM
{
	static constexpr uint8_t CMD_ERWP = 0x03;

public:
	static void writeEEPROM(void* data)
	{
		uint16_t* userrowPtr = (uint16_t*)0x1400;

		eeprom_busy_wait();

		uint16_t* data_ = (uint16_t*)data;
		for (int i = 0; i < 16; i++)
			userrowPtr[i] = data_[i];

		_PROTECTED_WRITE_SPM(NVMCTRL.CTRLA, CMD_ERWP);
	}
};
