//
// Created by tumbar on 3/2/23.
//

#ifndef WERFEN_LED_H
#define WERFEN_LED_H

#include <gbl.h>

/**
 * Set the led light level via directly setting pwm
 * @param pwm 0 - 1.0 pwm level
 * @return Success or failure
 */
void led_set(F32 pwm);

/**
 * Check if the LED is on
 * @return TRUE if led is on
 */
Bool led_is_on(void);

/**
 * Set the led light level by controlling the
 * voltage on the sensor. Use a PID controller
 * to keep the light at a certain level
 * @param voltage voltage to keep light sensor at
 * @return Success or failure
 */
void led_voltage(F32 voltage);

void led_set_p(F32 p);
void led_set_i(F32 i);
void led_set_d(F32 d);

/**
 * Start the ADC for the light sensor on DMA
 * @param hadc adc to start DMA on
 */
void led_sensor_init(void* hadc);

/**
 * Initialize the led task telling the task
 * which timer is triggering its service
 * @param led_tim timer controlling LED PWM
 * @param led_chan timer channel controlling LED PWM
 * @param task_tim PID task trigger timer
 */
void led_init(void* led_tim, U16 led_chan, void* task_tim);

void led_task(void);

#endif //WERFEN_LED_H
