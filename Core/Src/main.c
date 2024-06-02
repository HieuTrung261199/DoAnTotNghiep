/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
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


/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdarg.h>
#include "string.h"
#include<stdio.h>
#include "stm32f4xx_gpio_driver.h"
#include "stm32f411.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
uint32_t adc_value[4];
float v[3];
uint32_t temp;
float hh;
char Rx_data[10];
uint8_t Rx = 0;
int o = 0;
int l = 0;
char buffer[50];
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;

UART_HandleTypeDef huart6;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_USART6_UART_Init(void);
static void set_up(void);
/* USER CODE BEGIN PFP */
void Stop_Caution(void){
	GPIO_WriteToOutputPin(GPIOC,0,0);
	GPIO_WriteToOutputPin(GPIOC,1,0);
}
void Start_Caution(void){

	GPIO_WriteToOutputPin(GPIOC,0,1);
	GPIO_WriteToOutputPin(GPIOC,1,1);

}
void send_Str(char* str) {
    HAL_UART_Transmit(&huart6, (uint8_t*)str, strlen(str), 1000);
}

void uart_printf(char* format, ...) {
    va_list aptr;
    va_start(aptr, format);
    char buffer[128] = {0};
    vsprintf(buffer, format, aptr);
    send_Str(buffer);
    va_end(aptr);
}


/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

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
  MX_ADC1_Init();
  MX_USART6_UART_Init();
  set_up();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
	  l++;
	  	  	  	  	  	  	  HAL_UART_Receive_IT(&huart6, &Rx_data, 1);
	  	  	  	  	  	  	  HAL_ADC_Start(&hadc1);
	  	  	  	  			  HAL_ADC_PollForConversion(&hadc1, 100);
	  	  	  	  			  adc_value[0] = HAL_ADC_GetValue(&hadc1);

	  	  	  	  			  //hh = adc_value[0] * 3.3 / 4096.0;

	  	  	  	  			  //Lm35
	  	  	  	  			  HAL_ADC_PollForConversion(&hadc1, 100);
	  	  	  	  			  adc_value[1] = HAL_ADC_GetValue(&hadc1);
	  	  	  	  			  float voltage = adc_value[1] * 3.3 / 4096.0;
	  	  	  	  			  temp = voltage * 100.0;

	  	  	  	  		      HAL_ADC_PollForConversion(&hadc1, 100);
	  	  	  	  			  adc_value[2] = HAL_ADC_GetValue(&hadc1);

	  	  	  	  		      HAL_ADC_PollForConversion(&hadc1, 100);
	  	  	  	  			  adc_value[3] = HAL_ADC_GetValue(&hadc1);

	  	  	  	  			/*  if (temp >= 40) {
	  	  	  	  			  GPIO_WriteToOutputPin(GPIOC, GPIO_PIN_0, 0);
	  	  	  	  			  GPIO_WriteToOutputPin(GPIOC, GPIO_PIN_1, 0);
	  	  	  	  		        }*/
	  	  	  	  			  //sprintf()
							  uart_printf("%d,%d,%d,%d",temp,(int)adc_value[0],(int)adc_value[1],(int)adc_value[2]);
							  HAL_Delay(2000);




    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
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
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
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
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV4;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Configure the global features of the ADC (Clock, Resolution, Data Alignment and number of conversion)
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV2;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.ScanConvMode = ENABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 5;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = 1;
  sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_2;
  sConfig.Rank = 2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_3;
  sConfig.Rank = 3;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure for the selected ADC regular channel its corresponding rank in the sequencer and its sample time.
  */
  sConfig.Channel = ADC_CHANNEL_4;
  sConfig.Rank = 4;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }}

/**
  * @brief USART6 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART6_UART_Init(void)
{

  /* USER CODE BEGIN USART6_Init 0 */

  /* USER CODE END USART6_Init 0 */

  /* USER CODE BEGIN USART6_Init 1 */

  /* USER CODE END USART6_Init 1 */
  huart6.Instance = USART6;
  huart6.Init.BaudRate = 115200;
  huart6.Init.WordLength = UART_WORDLENGTH_8B;
  huart6.Init.StopBits = UART_STOPBITS_1;
  huart6.Init.Parity = UART_PARITY_NONE;
  huart6.Init.Mode = UART_MODE_TX_RX;
  huart6.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart6.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart6) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART6_Init 2 */
  HAL_NVIC_SetPriority(USART6_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(USART6_IRQn);
  /* USER CODE END USART6_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();

}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */


void set_up(void){
	//Open Clock

	GPIO_Handle_t GPIOHandler2,GPIOHandler1,GPIOHandler3,GPIOHandler4;
	memset(&GPIOHandler1,0,sizeof(GPIOHandler1));
	memset(&GPIOHandler2,0,sizeof(GPIOHandler2));
	memset(&GPIOHandler3,0,sizeof(GPIOHandler3));
	memset(&GPIOHandler4,0,sizeof(GPIOHandler4));
		//PC0, PC1 for Relay
		GPIOHandler1.pGPIOx = GPIOC;
		GPIOHandler1.GPIO_PinConfig.GPIO_PinNumber = GPIO_PIN_0;
		GPIOHandler1.GPIO_PinConfig.GPIO_PinMode = GPIO_MODE_OUT;
		GPIOHandler1.GPIO_PinConfig.GPIO_PinOPType = GPIO_OP_TYPE_OD;
		GPIOHandler1.GPIO_PinConfig.GPIO_PinSpeed = GPIO_SPEED_FAST;
		GPIOHandler1.GPIO_PinConfig.GPIO_PinPuPdControl = GPIO_NO_PUPD;
		GPIO_Init(&GPIOHandler1);

		GPIOHandler2.pGPIOx = GPIOC;
		GPIOHandler2.GPIO_PinConfig.GPIO_PinNumber = GPIO_PIN_1;
		GPIOHandler2.GPIO_PinConfig.GPIO_PinMode = GPIO_MODE_OUT;
		GPIOHandler2.GPIO_PinConfig.GPIO_PinOPType = GPIO_OP_TYPE_OD;
		GPIOHandler2.GPIO_PinConfig.GPIO_PinSpeed = GPIO_SPEED_FAST;
		GPIOHandler2.GPIO_PinConfig.GPIO_PinPuPdControl = GPIO_NO_PUPD;
		GPIO_Init(&GPIOHandler2);

		//PC2, PC3 for Button
		GPIOHandler3.pGPIOx = GPIOC;
		GPIOHandler3.GPIO_PinConfig.GPIO_PinNumber = GPIO_PIN_2;
		GPIOHandler3.GPIO_PinConfig.GPIO_PinMode = GPIO_MODE_IT_FT;
		GPIOHandler3.GPIO_PinConfig.GPIO_PinSpeed = GPIO_SPEED_FAST;
		GPIOHandler3.GPIO_PinConfig.GPIO_PinPuPdControl = GPIO_PIN_PU;
		GPIO_Init(&GPIOHandler3);
		GPIO_IRQPriorityConfig(IRQ_NO_EXTI2,NVIC_IRQ_PRI15);
		GPIO_IRQInterruptConfig(IRQ_NO_EXTI2,ENABLE);

		GPIOHandler4.pGPIOx = GPIOC;
		GPIOHandler4.GPIO_PinConfig.GPIO_PinNumber = GPIO_PIN_3;
		GPIOHandler4.GPIO_PinConfig.GPIO_PinMode = GPIO_MODE_IN;
		GPIOHandler4.GPIO_PinConfig.GPIO_PinSpeed = GPIO_SPEED_FAST;
		GPIOHandler4.GPIO_PinConfig.GPIO_PinPuPdControl = GPIO_PIN_PU;
	    GPIO_Init(&GPIOHandler4);

}

void EXTI2_IRQHandler(void)
{
   /// delay(); //200ms . wait till button de-bouncing gets over
	GPIO_ToggleOutputPin(GPIOC,GPIO_PIN_1);
		GPIO_ToggleOutputPin(GPIOC,GPIO_PIN_0);
	GPIO_IRQHandling(GPIO_PIN_2); //clear the pending event from exti line

}


void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if(huart->Instance==huart6.Instance)
	{
		//memset(&GPIOHandler4,0,sizeof(GPIOHandler4));

		if (strstr(Rx_data,"1") != NULL)
		    	{   GPIO_WriteToOutputPin(GPIOC, GPIO_PIN_0, 0);
	  	  			  GPIO_WriteToOutputPin(GPIOC, GPIO_PIN_1, 0);
					uart_printf("\nFire alarm system: ON\n");
					uart_printf("\n-----------------------\n");
		    		memset(Rx_data,0,sizeof(Rx_data)); //clear memory recv_data = 0, set up 7 bytes
		    	}
		else{
			GPIO_WriteToOutputPin(GPIOC, GPIO_PIN_0, 1);
				  	  			  GPIO_WriteToOutputPin(GPIOC, GPIO_PIN_1, 1);
			uart_printf("\nFire alarm system: OFF\n");
			uart_printf("\n-----------------------\n");
			memset(Rx_data,0,sizeof(Rx_data)); //clear memory recv_data = 0, set up 7 bytes
		}

		/*if (strstr(Rx_data,"OFF") != NULL)
				    	{
			GPIO_ToggleOutputPin(GPIOC,GPIO_PIN_1);
				GPIO_ToggleOutputPin(GPIOC,GPIO_PIN_0);
						uart_printf("\nFire alarm system: OFF\n");
				    		memset(Rx_data,0,sizeof(Rx_data)); //clear memory recv_data = 0, set up 7 bytes
				    	}*/


	}

}
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
