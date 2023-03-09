/**
 * @file mlx90393.h
 * @author Luo-Yijie (1951578@tongji.edu.cn)
 * @brief mlx90393 drive code (header)
 * @version 0.1
 * @date 2022-12-26
 *
 * @copyright Copyright (c) 2022
 *
 */

#ifndef __MLX90393_H__
#define __MLX90393_H__

#include "stm32f4xx_hal.h"
#include "softI2c.h"

#define MLX90393_BASE_ADDR 0x14


/**
 * @brief MspConf
 * 
 */
typedef struct
{
    uint8_t A0;
    uint8_t A1;
    GPIO_TypeDef* trig_port;
    GPIO_TypeDef* drdy_port;
    uint16_t trig_pin;
    uint16_t drdy_pin;
} Mlx90393ConfTypeDef;

/**
 * @brief GPIO Init structure definition
 */
typedef struct
{
    uint8_t addr;
    uint8_t resolution_xyz;
    uint8_t gain_sel;
    uint8_t hallconf;
    float gain_factor;
    Mlx90393ConfTypeDef msp;
} Mlx90393TypeDef;

/**
 * @brief Inituialize the mlx90393 sensor
 * 
 * @param mlx90393 the sensor handler
 * @param conf MspConf structrue
 * @return uint8_t [0]:ok [1]:failed
 */
uint8_t Peri_Mlx90393_Init(Mlx90393TypeDef *mlx90393, const Mlx90393ConfTypeDef *conf);

/**
 * @brief wait the sensor for measuring
 * 
 * @param mlx90393 the sensor handler
 */
uint8_t Peri_Mlx90393_waitReady(const Mlx90393TypeDef *mlx90393);

/**
 * @brief send trig pulse to sensor
 * 
 * @param mlx90393 the sensor handler
 */
void Peri_Mlx90393_Trig(const Mlx90393TypeDef *mlx90393);

/**
 * @brief read measurement and then convert it
 * 
 * @param mlx90393 the sensor handler
 * @param dataConv Converted data
 * @return uint8_t 
 */
uint8_t Peri_Mlx90393_readData(const Mlx90393TypeDef *mlx90393, float *dataConv);

#endif
