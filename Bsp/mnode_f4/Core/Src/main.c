/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2023 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "crc.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "mlx90393.h"
#include "tickus.h"
#include "ai_app.h"
#include <stdio.h>
#include <math.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
typedef struct{
    uint8_t header[4];
    float_t flux[12];
    float_t crc;
    uint32_t time;
    float_t x;
    float_t y;
    float_t F;
    uint32_t status;
}frameStructure;
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define AI_EABLE 1
#define AI_DEBUG 0
#define OUTPUT_FORMAT_ASCII 0
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/**
 * @brief configuration data of 4 mlx90393 chips, including I2C address(A0|A1), drdy PIN and trig PIN
 *
 */
const Mlx90393ConfTypeDef mag_conf[4] =
{
    [0] = {
        .A0 = 0,
        .A1 = 0,
        .drdy_port = GPIOA,
        .drdy_pin = GPIO_PIN_2,
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_6},
    [1] = {
        .A0 = 1,
        .A1 = 0,
        .drdy_port = GPIOA,
        .drdy_pin = GPIO_PIN_0,
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_4},
    [2] = {
        .A0 = 0,
        .A1 = 1,
        .drdy_port = GPIOA,
        .drdy_pin = GPIO_PIN_3,
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_7},
    [3] = {
        .A0 = 1,
        .A1 = 1,
        .drdy_port = GPIOA,
        .drdy_pin = GPIO_PIN_1,
        .trig_port = GPIOA,
        .trig_pin = GPIO_PIN_5}
};

/**
 * @brief temperature and magnitude data after converting from raw frame
 *
 */
static float dataConv[4][4];
static float dataBias[4][4];

/**
 * @brief handler of 4 mlx90393 chips
 */
static Mlx90393TypeDef hmag[4];

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
void get_dataBias(float dataBias[4][4]);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/* USER CODE BEGIN 0 */


/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_CRC_Init();
  /* USER CODE BEGIN 2 */
    /* scan I2C devices on the bus(0-127) */
    // I2C_SCAN(); //addr: 14 15 16 17

	#if AI_ENABLE
	ai_Init();
	
	/* brief information */
    printf("\r\nmlx90393_f4_v1.0 with AI on board\r\n");
    printf("auther:ultrlyj, build:%s,%s\r\n", __DATE__, __TIME__);
	#else
	printf("\r\nmlx90393_f4_v1.0 without AI on board\r\n");
    printf("auther:ultrlyj, build:%s,%s\r\n", __DATE__, __TIME__);
	#endif
    
    /* initialize the I2C bus and 4 mlx90393 chips */
    I2C_Init();
	
    for (uint8_t i = 0; i < 4; i++)
		if(!Peri_Mlx90393_Init(&hmag[i], &mag_conf[i]))
		{
			printf("ok ");
		}
        else
		{
			printf("failed");
		}
	printf("\r\n");

    static frameStructure frame;
    frame.header[0] = '$';
    frame.header[1] = 'M';
    frame.header[2] = 'A';
    frame.header[3] = 'G';
	
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
#if AI_EABLE
	#if AI_DEBUG
    extern const float test_in[100][12];
    extern const float y_pc[100][2];
	float test_out[2]={0,0};
	for(int i=0;i<100;i++)
	{
		uint32_t time_start = getCurrentMicros();
		ai_Run((float*)(test_in[i]),test_out);
		uint32_t time_end = getCurrentMicros();
		float error = sqrt((y_pc[i][0]-test_out[0])*(y_pc[i][0]-test_out[0]) + (y_pc[i][1]-test_out[1])*(y_pc[i][1]-test_out[1]));
		printf("%f,%f,%f,%d\r\n",test_out[0],test_out[1],error,time_end-time_start);
       HAL_GPIO_TogglePin(LED0_GPIO_Port, LED0_Pin | LED1_Pin | LED2_Pin | LED3_Pin);
	}
	#endif	
#endif
	/* get flux density bias */
	get_dataBias(dataBias);

    while (1)
    {
        uint32_t time_tick = HAL_GetTick();
        /* send tirg signal at the same time*/
        for (uint8_t i = 0; i < 4; i++)
            Peri_Mlx90393_Trig(&hmag[i]);
    
        /* wait until 4 sensor finish their measurement */
        for (uint8_t i = 0; i < 4; i++)
        {
            if (!Peri_Mlx90393_waitReady(&hmag[i]))
                Peri_Mlx90393_readData(&hmag[i], dataConv[i]);
        }
        
        /* get crc check value */
		float crc = 0.0f;
        for (uint8_t i = 0; i < 4; i++)
        {
            for (uint8_t j = 1; j < 4; j++)
            {
				float x = dataConv[i][j]-dataBias[i][j];
				frame.flux[i*3+j-1] = x;
				crc+=x;			
            }
        }
        /* CNN model predict */
		#if AI_EABLE
        float predict[2];
        ai_Run((float*)(frame.flux), predict);
		frame.x = predict[0];
        frame.y = predict[1];
		#endif
        frame.crc = crc;
        frame.time = time_tick;
        
        frame.status = 0;

        #if OUTPUT_FORMAT_ASCII
        /* support IPC: mevis, serialplot, mevis calibrate unity */
        for (uint8_t i = 0; i < 12; i++)
            printf("%.2f,",frame.flux[i]);
        printf("%.2f\n", frame.crc);
        #else
        HAL_UART_Transmit(&huart1, (uint8_t *)&frame, 76, 0xffff);
        while (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_TC) == RESET);
        #endif
		HAL_GPIO_TogglePin(LED0_GPIO_Port, LED0_Pin | LED1_Pin | LED2_Pin | LED3_Pin);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    }
  /* USER CODE END 3 */
}

void get_dataBias(float dataBias[4][4])
{
	const uint16_t times = 200;
	for (uint8_t i = 0; i < 4; i++)
		for (uint8_t j = 0; j < 4; j++)
		dataBias[i][j] = 0.0f;
	for (uint16_t t = 0; t < times; t++)
	{
		/* send tirg signal at the same time*/
		for (uint8_t i = 0; i < 4; i++)
			Peri_Mlx90393_Trig(&hmag[i]);

		/* wait until 4 sensor finish their measurement */
		for (uint8_t i = 0; i < 4; i++)
		{
			if (!Peri_Mlx90393_waitReady(&hmag[i]))
				Peri_Mlx90393_readData(&hmag[i], dataConv[i]);
		}
		
		/* output data(ascii data only for test) */
		float crc = 0.0f;
		for (uint8_t i = 0; i < 4; i++)
		{
			for (uint8_t j = 1; j < 4; j++)
			{
				float x = dataConv[i][j];
				x=(int)100*x+0.5;
				x=x/100;
				dataBias[i][j] += x;			
			}
		}
	}
	for (uint8_t i = 0; i < 4; i++)
		for (uint8_t j = 0; j < 4; j++)
		dataBias[i][j] /= times;
	
}
/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 100;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
    /* User can add his own implementation to report the HAL error return state */
    __disable_irq();
    while (1)
    {
    }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
    /* User can add his own implementation to report the file name and line number,
       ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
