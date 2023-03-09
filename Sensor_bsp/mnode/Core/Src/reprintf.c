/**
 * @file reprintf.c
 * @author Luo-Yijie (1951578@tongji.edu.cn)
 * @brief redirect printf to serial port
 * @version 0.1
 * @date 2022-12-29
 *
 * @copyright Copyright (c) 2022
 *
 */

#include <stdio.h>
#include "stm32f1xx_hal.h"

#define STDIO_PORT huart1

extern UART_HandleTypeDef STDIO_PORT;
/**
 * @brief define printf function structure
 *
 */
struct FILE {
    int handle;
};

/**
 * @brief redirect printf to serial port
 *
 */
int fputc(int ch, FILE *f)
{

    HAL_UART_Transmit(&STDIO_PORT, (uint8_t *)&ch, 1, 0xffff);
    while (__HAL_UART_GET_FLAG(&STDIO_PORT, UART_FLAG_TC) == RESET) {}
    return ch;
}
