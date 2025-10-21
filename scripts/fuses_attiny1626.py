WDT_PERIOD_OFF_gc = (0x00 << 0)
WDT_PERIOD_8CLK_gc = (0x01 << 0)
WDT_PERIOD_16CLK_gc = (0x02 << 0)
WDT_PERIOD_32CLK_gc = (0x03 << 0)
WDT_PERIOD_64CLK_gc = (0x04 << 0)
WDT_PERIOD_128CLK_gc = (0x05 << 0)
WDT_PERIOD_256CLK_gc = (0x06 << 0)
WDT_PERIOD_512CLK_gc = (0x07 << 0)
WDT_PERIOD_1KCLK_gc = (0x08 << 0)
WDT_PERIOD_2KCLK_gc = (0x09 << 0)
WDT_PERIOD_4KCLK_gc = (0x0A << 0)
WDT_PERIOD_8KCLK_gc = (0x0B << 0)

WDT_WINDOW_OFF_gc = (0x00 << 4)
WDT_WINDOW_8CLK_gc = (0x01 << 4)
WDT_WINDOW_16CLK_gc = (0x02 << 4)
WDT_WINDOW_32CLK_gc = (0x03 << 4)
WDT_WINDOW_64CLK_gc = (0x04 << 4)
WDT_WINDOW_128CLK_gc = (0x05 << 4)
WDT_WINDOW_256CLK_gc = (0x06 << 4)
WDT_WINDOW_512CLK_gc = (0x07 << 4)
WDT_WINDOW_1KCLK_gc = (0x08 << 4)
WDT_WINDOW_2KCLK_gc = (0x09 << 4)
WDT_WINDOW_4KCLK_gc = (0x0A << 4)
WDT_WINDOW_8KCLK_gc = (0x0B << 4)

BOD_LVL_BODLEVEL0_gc = (0x00 << 5)  # 1.80 V
BOD_LVL_BODLEVEL1_gc = (0x01 << 5)  # 2.15 V
BOD_LVL_BODLEVEL2_gc = (0x02 << 5)  # 2.60 V
BOD_LVL_BODLEVEL3_gc = (0x03 << 5)  # 2.95 V
BOD_LVL_BODLEVEL4_gc = (0x04 << 5)  # 3.30 V
BOD_LVL_BODLEVEL5_gc = (0x05 << 5)  # 3.70 V
BOD_LVL_BODLEVEL6_gc = (0x06 << 5)  # 4.00 V
BOD_LVL_BODLEVEL7_gc = (0x07 << 5)  # 4.30 V

bod_lvl_map = {
    1.80: BOD_LVL_BODLEVEL0_gc,
    2.15: BOD_LVL_BODLEVEL1_gc,
    2.60: BOD_LVL_BODLEVEL2_gc,
    2.95: BOD_LVL_BODLEVEL3_gc,
    3.30: BOD_LVL_BODLEVEL4_gc,
    3.70: BOD_LVL_BODLEVEL5_gc,
    4.00: BOD_LVL_BODLEVEL6_gc,
    4.30: BOD_LVL_BODLEVEL7_gc,
}

BOD_SAMPFREQ_1KHZ_gc = (0x00 << 4)  # 1kHz sampling frequency
BOD_SAMPFREQ_125HZ_gc = (0x01 << 4)  # 125Hz sampling frequency

BOD_ACTIVE_DIS_gc = (0x00 << 2)  # Disabled
BOD_ACTIVE_ENABLED_gc = (0x01 << 2)  # Enabled
BOD_ACTIVE_SAMPLED_gc = (0x02 << 2)  # Sampled
BOD_ACTIVE_ENWAKE_gc = (0x03 << 2)  # Enabled with wake-up halted until BOD is ready

BOD_SLEEP_DIS_gc = (0x00 << 0)  # Disabled
BOD_SLEEP_ENABLED_gc = (0x01 << 0)  # Enabled
BOD_SLEEP_SAMPLED_gc = (0x02 << 0)  # Sampled

OSCCFG_RESERVED_bm = 0b01111100
OSCCFG_FUSE_OSCLOCK_bm = 0x80
OSCCFG_FREQSEL_16MHZ_gc = (0x01 << 0)
OSCCFG_FREQSEL_20MHZ_gc = (0x02 << 0)

SYSCFG0_RESERVED_bm = 0b00100010
SYSCFG0_CRCSRC_FLASH_gc = (0x00 << 6)
SYSCFG0_CRCSRC_BOOT_gc = (0x01 << 6)
SYSCFG0_CRCSRC_BOOTAPP_gc = (0x02 << 6)
SYSCFG0_CRCSRC_NOCRC_gc = (0x03 << 6)

SYSCFG0_TOUDIS_bm = 0b00010000

SYSCFG0_RSTPINCFG_GPIO_gc = (0x00 << 2)
SYSCFG0_RSTPINCFG_UPDI_gc = (0x01 << 2)
SYSCFG0_RSTPINCFG_RST_gc = (0x02 << 2)
SYSCFG0_RSTPINCFG_PDIRST_gc = (0x03 << 2)

SYSCFG0_EESAVE_NOT_ERASE_bm = 0b00000001


def build_fuses(config):
    watchdog_window = WDT_PERIOD_OFF_gc | WDT_WINDOW_OFF_gc

    bod = BOD_SAMPFREQ_125HZ_gc

    bod_level = config["fuses"].get("bod_level")
    if bod_level is None:
        bod |= BOD_ACTIVE_DIS_gc | BOD_SLEEP_DIS_gc
    else:
        assert bod_level in bod_lvl_map.keys()

        bod |= BOD_ACTIVE_ENABLED_gc | BOD_SLEEP_ENABLED_gc
        bod |= bod_lvl_map[bod_level]

    freq = config["fuses"].get("frequency")
    assert freq in (16, 20)
    if freq == 16:
        osccfg = OSCCFG_RESERVED_bm | OSCCFG_FREQSEL_16MHZ_gc
    elif freq == 20:
        osccfg = OSCCFG_RESERVED_bm | OSCCFG_FREQSEL_20MHZ_gc

    syscfg0 = SYSCFG0_RESERVED_bm | SYSCFG0_CRCSRC_NOCRC_gc | SYSCFG0_RSTPINCFG_UPDI_gc | SYSCFG0_TOUDIS_bm | SYSCFG0_EESAVE_NOT_ERASE_bm

    syscfg1 = 0b11111000 | 0x07  # default
    app_end = 0  # blocks of 256
    boot_end = 0
    # boot_end = 16  # blocks of 256 = 16*256 = 4kb

    return [watchdog_window, bod, osccfg, 0xff, 0x00, syscfg0, syscfg1, app_end, boot_end]
