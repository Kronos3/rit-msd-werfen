/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32l4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define B1_Pin GPIO_PIN_13
#define B1_GPIO_Port GPIOC
#define B1_EXTI_IRQn EXTI15_10_IRQn
#define LIGHT_S_Pin GPIO_PIN_1
#define LIGHT_S_GPIO_Port GPIOB
#define SWITCH2_Pin GPIO_PIN_12
#define SWITCH2_GPIO_Port GPIOB
#define SWITCH2_EXTI_IRQn EXTI15_10_IRQn
#define SWITCH1_Pin GPIO_PIN_14
#define SWITCH1_GPIO_Port GPIOB
#define SWITCH1_EXTI_IRQn EXTI15_10_IRQn
#define ENABLE_Pin GPIO_PIN_15
#define ENABLE_GPIO_Port GPIOB
#define ENABLE_EXTI_IRQn EXTI15_10_IRQn
#define STEP_Pin GPIO_PIN_8
#define STEP_GPIO_Port GPIOC
#define MS1_Pin GPIO_PIN_8
#define MS1_GPIO_Port GPIOA
#define MS2_Pin GPIO_PIN_9
#define MS2_GPIO_Port GPIOA
#define MS3_Pin GPIO_PIN_10
#define MS3_GPIO_Port GPIOA
#define DIR_Pin GPIO_PIN_11
#define DIR_GPIO_Port GPIOA
#define TMS_Pin GPIO_PIN_13
#define TMS_GPIO_Port GPIOA
#define TCK_Pin GPIO_PIN_14
#define TCK_GPIO_Port GPIOA
#define LED_Pin GPIO_PIN_12
#define LED_GPIO_Port GPIOC
#define SWO_Pin GPIO_PIN_3
#define SWO_GPIO_Port GPIOB
#define LIGHT_Pin GPIO_PIN_8
#define LIGHT_GPIO_Port GPIOB
/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
