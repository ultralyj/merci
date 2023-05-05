#include "softI2c.h"
#include <stdio.h>

void I2C_SCAN(void)
{
	I2C_Init();
	uint8_t ack=0;
	for(uint8_t addr=0; addr<128; addr++)
	{
		I2C_Start();
		I2C_Send_Byte((addr << 1) | 0x00);
		ack = I2C_Wait_Ack();
		if(ack == 0)
		{
			printf(" %02x",addr);
		}
		else
		{
			printf(" --");
		}
		if(addr%8==7)
		{
			printf("\r\n");
		}
	}
}
