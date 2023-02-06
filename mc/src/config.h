//
// Created by tumbar on 1/19/23.
//

#ifndef WERFEN_CONFIG_H
#define WERFEN_CONFIG_H

#include <stm32f1xx_hal.h>

#define MS1_PORT GPIOB
#define MS1_PIN GPIO_PIN_12

#define MS2_PORT GPIOB
#define MS2_PIN GPIO_PIN_13

#define MS3_PORT GPIOB
#define MS3_PIN GPIO_PIN_14

#define DIR_PORT GPIOA
#define DIR_PIN GPIO_PIN_4

#define STEP_TIMER &htim2
#define STEP_CHANNEL TIM_CHANNEL_4

#define ESTOP_PORT GPIOB
#define ESTOP_PIN GPIO_PIN_8

// TODO(tumbar)
#define LIMIT_A_PORT GPIOB
#define LIMIT_A_PIN GPIO_PIN_6

#define LIMIT_B_PORT GPIOB
#define LIMIT_B_PIN GPIO_PIN_7

#endif //WERFEN_CONFIG_H
