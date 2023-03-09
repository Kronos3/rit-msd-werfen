//
// Created by tumbar on 1/19/23.
//

#include "switch.h"
#include "main.h"
#include "motor.h"

static TIM_HandleTypeDef* debounce_timer;

static Bool use_debounce = TRUE;
static Bool debounce_check_limit_1 = FALSE;
static volatile Bool debounce_running = FALSE;

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

void switch_init(void* debounce_timer_)
{
    debounce_timer = debounce_timer_;
}

void switch_debounce_period(U16 ms)
{
    use_debounce = ms > 0;

    if (use_debounce)
    {
        __HAL_TIM_SET_AUTORELOAD(debounce_timer, ms - 1);
    }
}

void switch_debounce_check(void)
{
    debounce_running = FALSE;

    if ((debounce_check_limit_1 && switch_limit_1_get()) ||
        (!debounce_check_limit_1 && switch_limit_2_get()))
    {
        motor_stop();
    }
}

static void switch_debounce(U16 event_pin)
{
    if (debounce_running)
    {
        return;
    }

    debounce_running = TRUE;
    debounce_check_limit_1 = event_pin == SWITCH1_Pin;
    HAL_TIM_Base_Start_IT(debounce_timer);
}

void switch_event(U16 event_pin)
{
    switch(event_pin)
    {
        case ENABLE_Pin:
            motor_stop();
            break;
        case SWITCH1_Pin:
        case SWITCH2_Pin:
            if (use_debounce)
            {
                switch_debounce(event_pin);
            }
            else
            {
                motor_stop();
            }
        default:
            break;
    }
}
