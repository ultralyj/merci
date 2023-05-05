/**
 * @file mlx90393.c
 * @author Luo-Yijie (1951578@tongji.edu.cn)
 * @brief mlx90393 drive code
 * @version 0.2
 * @date 2022-12-26
 *
 * @copyright Copyright (c) 2022
 *
 */

#include "mlx90393.h"
#include <stdio.h>

const float base_xy_sens_hc0   = 0.196f;
const float base_z_sens_hc0    = 0.316f;
const float base_xy_sens_hc0xc = 0.150f;
const float base_z_sens_hc0xc  = 0.242f;

enum {
    sensor_gain_5    = 0,
    sensor_gain_4    = 1,
    sensor_gain_3    = 2,
    sensor_gain_2_5  = 3,
    sensor_gain_2    = 4,
    sensor_gain_1_67 = 5,
    sensor_gain_1_33 = 6,
    sensor_gain_1    = 7,
} mlx90393_gain;

enum {
    resolution_0 = 0,
    resolution_1 = 1,
    resolution_2 = 2,
    resolution_3 = 3,
} mlx90393_resolution;

enum {
    MLX90393_CMD_NOP               = 0x00,
    MLX90393_CMD_EXIT              = 0x80,
    MLX90393_CMD_START_BURST       = 0x10,
    MLX90393_CMD_WAKE_ON_CHANGE    = 0x20,
    MLX90393_CMD_START_MEASUREMENT = 0x30,
    MLX90393_CMD_READ_MEASUREMENT  = 0x40,
    MLX90393_CMD_READ_REGISTER     = 0x50,
    MLX90393_CMD_WRITE_REGISTER    = 0x60,
    MLX90393_CMD_MEMORY_RECALL     = 0xd0,
    MLX90393_CMD_MEMORY_STORE      = 0xe0,
    MLX90393_CMD_RESET             = 0xf0
};


static uint8_t Mlx90393_sendI2c(uint8_t addr, uint8_t *receiveBuffer, uint8_t *sendBuffer,
                                int sendMessageLength, int receiveMessageLength);
static uint8_t Mlx90393_sendCmd(const Mlx90393TypeDef *mlx90393, uint8_t cmd);
static void Mlx90393_readMeasurement(const Mlx90393TypeDef *mlx90393, uint8_t *status, uint16_t *mdata);
static void Mlx90393_readReg(const Mlx90393TypeDef *mlx90393, uint8_t addr, uint8_t *status, uint16_t *regdata);
static void Mlx90393_writeReg(const Mlx90393TypeDef *mlx90393, uint8_t addr, uint8_t *status, uint16_t *regdata);

static void Mlx90393_setDefaultRegs(const Mlx90393TypeDef *mlx90393);
static void Mlx90393_setGainFactor(Mlx90393TypeDef *mlx90393);
static void Mlx90393_MspInit(const Mlx90393ConfTypeDef *conf);
static void Mlx90393_convData(const Mlx90393TypeDef *mlx90393, uint16_t *dataRaw, float *dataConv);

/**
 * @brief send control command to mlx90393
 *
 * @param mlx90393 handler of the sensor
 * @param cmd control command[0:7]
 * @return uint8_t status byte
 */
static uint8_t Mlx90393_sendCmd(const Mlx90393TypeDef *mlx90393, uint8_t cmd)
{
    uint8_t write_buffer[1], receive_buffer[1];
    write_buffer[0] = cmd;
    Mlx90393_sendI2c(mlx90393->addr, receive_buffer, write_buffer, 1, 1);
    return receive_buffer[0];
}

/**
 * @brief read out measurement of mlx90393(txyz)
 *
 * @param mlx90393 handler of the sensor
 * @param status status byte response
 * @param mdata measurement data pointer, space must larger than uint16_t[4]
 */
static void Mlx90393_readMeasurement(const Mlx90393TypeDef *mlx90393, uint8_t *status, uint16_t *mdata)
{
    static uint8_t write_buffer[1], receive_buffer[9];
    write_buffer[0] = MLX90393_CMD_READ_MEASUREMENT | 0x0f;
    Mlx90393_sendI2c(mlx90393->addr, receive_buffer, write_buffer, 1, 9);
    *status = receive_buffer[0];
    for (uint8_t i = 0; i < 4; i++)
        mdata[i] = (uint16_t)((uint16_t)(receive_buffer[i * 2 + 1] << 8) | (uint16_t)receive_buffer[i * 2 + 2]);
}

/**
 * @brief read register from volatile memory of mlx90393
 *
 * @param mlx90393 handler of the sensor
 * @param addr register address[0:5]
 * @param status status byte response
 * @param regdata data read out from register
 */
static void Mlx90393_readReg(const Mlx90393TypeDef *mlx90393, uint8_t addr, uint8_t *status, uint16_t *regdata)
{
    static uint8_t write_buffer[2], receive_buffer[3];
    write_buffer[0] = MLX90393_CMD_READ_REGISTER;
    write_buffer[1] = (addr & 0x3f) << 2;
    Mlx90393_sendI2c(mlx90393->addr, receive_buffer, write_buffer, 2, 3);
    *status  = receive_buffer[0];
    *regdata = (uint16_t)((uint16_t)(receive_buffer[1] << 8) | (uint16_t)receive_buffer[2]);
}

/**
 * @brief write register from volatile memory of mlx90393
 *
 * @param mlx90393 handler of the sensor
 * @param addr register address[0:5]
 * @param status status byte response
 * @param regdata data sent to the register
 */
static void Mlx90393_writeReg(const Mlx90393TypeDef *mlx90393, uint8_t addr, uint8_t *status, uint16_t *regdata)
{
    static uint8_t write_buffer[4], receive_buffer[1];
    write_buffer[0] = MLX90393_CMD_WRITE_REGISTER;
    write_buffer[1] = (*regdata & 0xff00) >> 8;
    write_buffer[2] = *regdata & 0x00ff;
    write_buffer[3] = (addr & 0x3f) << 2;
    Mlx90393_sendI2c(mlx90393->addr, receive_buffer, write_buffer, 4, 1);
    *status = receive_buffer[0];
}



/**
 * @brief base i2c communication method with mlx90393
 *
 * @param addr device address of mlx90393[0:6]
 * @param receiveBuffer pointer of receive buffer
 * @param sendBuffer pointer of send buffer
 * @param sendMessageLength the length of send buffer
 * @param receiveMessageLength the length of receive buffer
 * @return uint8_t response status, [0]:OK [1,2,3]:fail
 */
static uint8_t Mlx90393_sendI2c(uint8_t addr, uint8_t *receiveBuffer, uint8_t *sendBuffer,
                                int sendMessageLength, int receiveMessageLength)
{
    uint8_t *tempSendBuffer    = sendBuffer;
    uint8_t *tempReceiveBuffer = receiveBuffer;
    uint8_t res                = 0;
    /* i2c write */
    I2C_Start();
    I2C_Send_Byte((addr << 1) | 0x00);
    I2C_Wait_Ack();
    for (int i = 0; i < sendMessageLength; i++) {
        I2C_Send_Byte(tempSendBuffer[i]);
        res |= I2C_Wait_Ack();
    }

    /* i2c read */
    I2C_Start();
    I2C_Send_Byte((addr << 1) | 0x01);
    res |= I2C_Wait_Ack() << 1;
    if (receiveMessageLength > 1) {
        for (int i = 0; i < receiveMessageLength - 1; i++) {
            tempReceiveBuffer[i] = I2C_Read_Byte(1);
        }
    }
    tempReceiveBuffer[receiveMessageLength - 1] = I2C_Read_Byte(0);
    I2C_Stop();

    receiveBuffer = tempReceiveBuffer;
    return res;
}

/**
 * @brief write default settings to volatile memory
 * 
 * @param mlx90393 handler of the sensor
 */
static void Mlx90393_setDefaultRegs(const Mlx90393TypeDef *mlx90393)
{
    uint16_t regval[3] = {0};
    uint8_t status;
    /* get the old regsters value */
    Mlx90393_readReg(mlx90393, 0x00, &status, &regval[0]);
    Mlx90393_readReg(mlx90393, 0x01, &status, &regval[1]);
    Mlx90393_readReg(mlx90393, 0x02, &status, &regval[2]);

    /* configure REG00 */
    uint16_t gain_sel = mlx90393->gain_sel;
    uint16_t hallconf = mlx90393->hallconf;
    uint16_t z_series = 0;

    regval[0] = (regval[0] & ~(0x0070)) | ((gain_sel << 4) & 0x0070);
    regval[0] = (regval[0] & ~(0x000f)) | (hallconf & 0x000f);
    regval[0] = (regval[0] & ~(0x0080)) | (z_series & 0x0080);
    regval[0] &= 0x00ff;

    /* configure REG01 */
    uint16_t burst_sel       = 0xf;
    uint16_t burst_datareate = 0x1;
    uint16_t tcmp_en         = 0x0;
    uint16_t ext_trig        = 0x1;
    uint16_t woc_diff        = 0x0;
    uint16_t comm_mode       = 0x3;
    uint16_t trig_int_sel    = 0x0;

    regval[1] = (regval[1] & ~(0x03c0)) | ((burst_sel << 6) & 0x03c0);
    regval[1] = (regval[1] & ~(0x003f)) | (burst_datareate & 0x003f);
    regval[1] = (regval[1] & ~(0x0400)) | ((tcmp_en << 10) & 0x0400);
    regval[1] = (regval[1] & ~(0x0800)) | ((ext_trig << 11) & 0x0800);
    regval[1] = (regval[1] & ~(0x1000)) | ((woc_diff << 12) & 0x1000);
    regval[1] = (regval[1] & ~(0x6000)) | ((comm_mode << 13) & 0x6000);
    regval[1] = (regval[1] & ~(0x8000)) | ((trig_int_sel << 15) & 0x8000);

    /* configure REG02 */
    uint16_t osr      = 0;
    uint16_t dig_filt = 5;
    uint16_t res_x    = mlx90393->resolution_xyz;
    uint16_t res_y    = mlx90393->resolution_xyz;
    uint16_t res_z    = mlx90393->resolution_xyz;
    uint16_t osr2     = 0;

    regval[2] = (regval[2] & ~(0x0003)) | ((osr << 0) & 0x0003);
    regval[2] = (regval[2] & ~(0x001c)) | ((dig_filt << 2) & 0x001c);
    regval[2] = (regval[2] & ~(0x0060)) | ((res_x << 5) & 0x0060);
    regval[2] = (regval[2] & ~(0x0180)) | ((res_y << 7) & 0x0180);
    regval[2] = (regval[2] & ~(0x0600)) | ((res_z << 9) & 0x0600);
    regval[2] = (regval[2] & ~(0x1800)) | ((osr2 << 11) & 0x1800);

    /* update regsters data */
    Mlx90393_writeReg(mlx90393, 0x00, &status, &regval[0]);
    Mlx90393_writeReg(mlx90393, 0x01, &status, &regval[1]);
    Mlx90393_writeReg(mlx90393, 0x02, &status, &regval[2]);
}

/**
 * @brief set gain factor
 * 
 * @param mlx90393 handler of the sensor
 */
static void Mlx90393_setGainFactor(Mlx90393TypeDef *mlx90393)
{
    /* update the handler */
    switch (mlx90393->gain_sel) {
        case sensor_gain_5:
            mlx90393->gain_factor = 5.0f;
            break;
        case sensor_gain_4:
            mlx90393->gain_factor = 4.0f;
            break;
        case sensor_gain_3:
            mlx90393->gain_factor = 3.0f;
            break;
        case sensor_gain_2_5:
            mlx90393->gain_factor = 2.5f;
            break;
        case sensor_gain_1_67:
            mlx90393->gain_factor = 1.66666667f;
            break;
        case sensor_gain_1_33:
            mlx90393->gain_factor = 1.33333333f;
            break;
        case sensor_gain_1:
            mlx90393->gain_factor = 1.0f;
            break;
        default:
            mlx90393->gain_factor = 1.0f;
            break;
    }
}

/**
 * @brief inituialize the i2c bus and trig,drdy pin
 * 
 * @param conf configuration structure
 */
static void Mlx90393_MspInit(const Mlx90393ConfTypeDef *conf)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    /* GPIO Ports Clock Enable */
    __HAL_RCC_GPIOA_CLK_ENABLE();

    GPIO_InitStruct.Pin   = conf->drdy_pin;
    GPIO_InitStruct.Mode  = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(conf->drdy_port, &GPIO_InitStruct);

    HAL_GPIO_WritePin(conf->trig_port, conf->trig_pin, GPIO_PIN_RESET);
    GPIO_InitStruct.Pin   =  conf->trig_pin;
    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(conf->trig_port, &GPIO_InitStruct);

}


/**
 * @brief convert raw data
 * 
 * @param mlx90393 the sensor handler
 * @param dataRaw rawdata array[t, x, y, z]
 * @param dataConv converted data array[t(`c), x(uT), y(yT), z(uT)]
 */
static void Mlx90393_convData(const Mlx90393TypeDef *mlx90393, uint16_t *dataRaw, float *dataConv)
{
    uint16_t _t, _x, _y, _z;
    float t, x, y, z;
    float gain_factor = mlx90393->gain_factor;
    float xy_sens, z_sens;

    if (mlx90393->hallconf == 0x0c) {
        xy_sens = base_xy_sens_hc0xc;
        z_sens  = base_z_sens_hc0xc;
    } else {
        xy_sens = base_xy_sens_hc0;
        z_sens  = base_z_sens_hc0;
    }

    _t = dataRaw[0];
    t  = 25 + (_t - 46244.f) / 45.2f;

    _x = dataRaw[1];
    x  = ((int16_t)(_x)*xy_sens * gain_factor * (1 << (mlx90393->resolution_xyz)));

    _y = dataRaw[2];
    y  = ((int16_t)(_y)*xy_sens * gain_factor * (1 << (mlx90393->resolution_xyz)));

    _z = dataRaw[3];
    z  = ((int16_t)(_z)*z_sens * gain_factor * (1 << (mlx90393->resolution_xyz)));

    dataConv[0] = t;
    dataConv[1] = x;
    dataConv[2] = y;
    dataConv[3] = z;
}

/**
 * @brief wait the sensor for measuring
 * 
 * @param mlx90393 the sensor handler
 */
uint8_t Peri_Mlx90393_waitReady(const Mlx90393TypeDef *mlx90393)
{
    Mlx90393ConfTypeDef msp = mlx90393->msp;
    uint16_t timeout = 0;
    while (timeout++<100 && !HAL_GPIO_ReadPin(msp.drdy_port, msp.drdy_pin))
    {
        HAL_Delay(1);
    } 
	if(timeout>=100)
		return 1;
	else
		return 0;
}

/**
 * @brief send trig pulse to sensor
 * 
 * @param mlx90393 the sensor handler
 */
void Peri_Mlx90393_Trig(const Mlx90393TypeDef *mlx90393)
{
    Mlx90393ConfTypeDef msp = mlx90393->msp;
    uint16_t timeout = 0;
    HAL_GPIO_WritePin(msp.trig_port, msp.trig_pin, GPIO_PIN_SET);
    Delay_us(2);
    HAL_GPIO_WritePin(msp.trig_port, msp.trig_pin, GPIO_PIN_RESET);
}

/**
 * @brief read measurement and then convert it
 * 
 * @param mlx90393 the sensor handler
 * @param dataConv Converted data
 * @return uint8_t 
 */
uint8_t Peri_Mlx90393_readData(const Mlx90393TypeDef *mlx90393, float *dataConv)
{
    uint8_t status = 0;
    uint16_t meas[4] = {0};
    Mlx90393_readMeasurement(mlx90393,&status,meas);
    Mlx90393_convData(mlx90393,meas,dataConv);
	return 0;
}

/**
 * @brief Inituialize the mlx90393 sensor
 * 
 * @param mlx90393 the sensor handler
 * @param conf MspConf structrue
 * @return uint8_t [0]:ok [1]:failed
 */
uint8_t Peri_Mlx90393_Init(Mlx90393TypeDef *mlx90393, const Mlx90393ConfTypeDef *conf)
{
    uint8_t status   = 0;
    uint16_t meas[4] = {0};
    float conv[4];
    /* basic settings */
    mlx90393->addr           = MLX90393_BASE_ADDR | (conf->A1 ? 2 : 0) | (conf->A0 ? 1 : 0);
    mlx90393->gain_sel       = sensor_gain_1;
    mlx90393->resolution_xyz = 1;
    mlx90393->hallconf       = 0x0c;
    mlx90393->msp = *conf;
    Mlx90393_setGainFactor(mlx90393);
    
    /* init the i2c bus and gpio port of drdy, trig */
    Mlx90393_MspInit(conf);

    /* reset the chip */
    status = Mlx90393_sendCmd(mlx90393, MLX90393_CMD_EXIT);
    status = Mlx90393_sendCmd(mlx90393, MLX90393_CMD_RESET);
    HAL_Delay(20);

    /* write default settings to volatile memory */
    Mlx90393_setDefaultRegs(mlx90393);

    /* the first measurement maybe unexact */
    status = Mlx90393_sendCmd(mlx90393, MLX90393_CMD_START_MEASUREMENT | 0x0f);
    Peri_Mlx90393_waitReady(mlx90393);
    Mlx90393_readMeasurement(mlx90393, &status, meas);

    if (status & 0x10)
        return 1;
    else
        return 0;
}
