//
// Created by tumbar on 1/19/23.
//

#ifndef WERFEN_SWITCH_H
#define WERFEN_SWITCH_H

#include <stm32l4xx_hal.h>

#include "gbl.h"

Bool switch_limit_1_get(void);
Bool switch_limit_2_get(void);
Bool switch_e_stop_get(void);

/**
 * Handle an external interrupt from a pin
 * @param event_pin pin where interrupt is coming from
 */
void switch_event(U16 event_pin);

#endif //WERFEN_SWITCH_H
