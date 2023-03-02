//
// Created by tumbar on 1/19/23.
//

#include "switch.h"
#include "main.h"
#include "motor.h"

Bool switch_limit_1_get(void)
{
    return HAL_GPIO_ReadPin(SWITCH1_GPIO_Port, SWITCH1_Pin) ? TRUE : FALSE;
}

Bool switch_limit_2_get(void)
{
    return HAL_GPIO_ReadPin(SWITCH2_GPIO_Port, SWITCH2_Pin) ? TRUE : FALSE;
}

Bool switch_e_stop_get(void)
{
    return HAL_GPIO_ReadPin(ENABLE_GPIO_Port, ENABLE_Pin) ? TRUE : FALSE;
}

void switch_event(U16 event_pin)
{
    switch(event_pin)
    {
        case SWITCH1_Pin:
        case SWITCH2_Pin:
        case ENABLE_Pin:
            motor_stop();
            break;
        default:
            break;
    }
}
