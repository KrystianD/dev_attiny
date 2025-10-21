#include <avr/io.h>
#include <avr/interrupt.h>

// Letting the compiler know there will be something called main
extern int main(void);

// Being nice to the compiler by predeclaring the ISRs
void __vector_cvt_nmi(void) __attribute__((weak, alias("dummy_handler")));
void __vector_cvt_lvl1(void) __attribute__((weak, alias("dummy_handler")));
void __vector_cvt_lvl0(void) __attribute__((weak, alias("dummy_handler")));

void __do_copy_data(void);
void __do_clear_bss(void);

// Setting up the vector section
// The rjmp instruction can handle 8k code space, so this is used for
// vector tables on devices with 8k flash or smaller. Other devices
// use the jmp instruction.

__attribute__((section(".vectors"), naked))
void vectors(void)
{
#if (PROGMEM_SIZE <= 0x2000)
	__asm__("rjmp init2");
	__asm__("rjmp __vector_cvt_nmi");
	__asm__("rjmp __vector_cvt_lvl1");
	__asm__("rjmp __vector_cvt_lvl0");
#else
	__asm__("jmp init2");
	__asm__("jmp __vector_cvt_nmi");
	__asm__("jmp __vector_cvt_lvl1");
	__asm__("jmp __vector_cvt_lvl0");
#endif
}

// Initialize the AVR core
__attribute__((section(".init2"), naked)) void init2(void)
{
	// GCC expects r1 to be zero
	__asm__("clr r1");

	// Make sure the status register has a known state
	SREG = 0;

	// Point the stack pointer to the end of stack
	SPL = (INTERNAL_SRAM_END >> 0) & 0xff; // (low byte)
	SPH = (INTERNAL_SRAM_END >> 8) & 0xff; // (high byte)
}

// __do_copy_data, __do_global_ctors etc are generaged between init2 and init9

__attribute__((section(".init9"), naked)) void init9(void)
{
	__asm__("rcall main");

	// Jump to avr libc defined exit handler
	// (Disables interrupts and runs an empty loop forever)
	__asm__("jmp _exit");
}

void dummy_handler(void)
{
	while (1);
}
