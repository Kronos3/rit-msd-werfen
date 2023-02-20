//
// Created by tumbar on 1/19/23.
//

#ifndef WERFEN_SWITCH_H
#define WERFEN_SWITCH_H

#include <stm32l4xx_hal.h>

#include "gbl.h"

GPIO_PinState switch_limit_a_set(void);
GPIO_PinState switch_limit_b_set(void);
GPIO_PinState switch_e_stop_set(void);

#endif //WERFEN_SWITCH_H
