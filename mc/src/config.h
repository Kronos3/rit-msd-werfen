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
#define JOB_TIMER &htim3

#define ENABLE_PORT GPIOA
#define ENABLE_PIN GPIO_PIN_3

#define SLEEP_PORT GPIOA
#define SLEEP_PIN GPIO_PIN_4

#define RESET_PORT GPIOA
#define RESET_PIN GPIO_PIN_5

#define ESTOP_PORT GPIOA
#define ESTOP_PIN GPIO_PIN_6

// TODO(tumbar)
#define LIMIT_A_PORT GPIOA
#define LIMIT_A_PIN GPIO_PIN_3

#define LIMIT_B_PORT GPIOA
#define LIMIT_B_PIN GPIO_PIN_3

#endif //WERFEN_CONFIG_H
