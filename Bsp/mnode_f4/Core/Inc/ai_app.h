#ifndef __AI_APP_H__
#define __AI_APP_H__

#include <stdio.h>
#include "stm32f4xx_hal.h"
#include "ai_platform.h"
#include "network.h"
#include "network_data.h"

int ai_Init(void);
int ai_Run(void *data_in, void *data_out);

#endif