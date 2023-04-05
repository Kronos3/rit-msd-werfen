//
// Created by tumbar on 1/19/23.
//

#ifndef WERFEN_SWITCH_H
#define WERFEN_SWITCH_H

#include <stm32l4xx_hal.h>

#include "gbl.h"

void switch_init(void* debounce_timer);

/**
 * Set debounce time delay
 * Sets the responsiveness of limit switches
 * @param ms ms delay to account to debounce
 */
void switch_debounce_period(U16 ms);
void switch_debounce_check(void);

Bool switch_limit_1_get(void);
Bool switch_limit_2_get(void);
Bool switch_e_stop_get(void);

void emergency_stop(void);
void emergency_clear(void);

/**
 * Handle an external interrupt from a pin
 * @param event_pin pin where interrupt is coming from
 */
void switch_event(U16 event_pin);

#endif //WERFEN_SWITCH_H
