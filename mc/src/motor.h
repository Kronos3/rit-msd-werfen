//
// Created by tumbar on 1/18/23.
//

#ifndef MC_MOTOR_H
#define MC_MOTOR_H

#include "gbl.h"

typedef enum
{
    MOTOR_STEP_FULL = 0,
    MOTOR_STEP_HALF = 1,
    MOTOR_STEP_QUARTER = 2,
    MOTOR_STEP_EIGHTH = 3,
    MOTOR_STEP_SIXTEENTH = 7,
} motor_step_t;

typedef enum
{
    MOTOR_PIN_MS1 = 1 << 0,
    MOTOR_PIN_MS2 = 1 << 1,
    MOTOR_PIN_MS3 = 1 << 2,
} motor_pin_mask;

typedef enum
{
    MOTOR_MASK_STEP = 0x0F,
    MOTOR_MASK_DIRECTION = 1 << 5,
    MOTOR_IGNORE_LIMITS = 1 << 6
} motor_mask;

typedef void (*MotorReply)(void);

/**
 * Initialize the timers and channels being used to
 * operate the motor
 * @param step_timer Timer used for PWM output generation
 * @param step_channel Channel on step timer for step pin
 */
void motor_init(void* step_timer,
                I32 step_channel);

/**
 * Set the step rate of the motor
 * @param hz Trigger frequency in Hz
 * @return FAILURE or SUCCESS
 */
Status motor_speed(U32 hz);

/**
 *
 */
void motor_tick(void);

/**
 * Apply n steps to the motor
 * @param step Step size
 * @param n number of steps
 * @param direction_reversed TRUE for forward and false for backward
 * @param reply_cb callback when motor request is done
 * @param ignore_limits Execute the motor motion event through we are sitting on a limit switch
 */
Status motor_step(motor_step_t step, U16 n,
                  Bool direction_reversed,
                  MotorReply reply_cb,
                  Bool ignore_limits);

I32 motor_get_step_size(motor_step_t step, Bool reversed);

/**
 * Set the logic lines on the motor driver to
 * select a step size
 * @param step step size to select
 */
void motor_set_ms(motor_step_t step);

void motor_stop(Bool motion_failed);
void motor_set_limit_step_off(motor_step_t step, U32 nstep);
void motor_limit_step_off(void);

Status motor_is_ready(motor_step_t step);
Bool motor_is_running();
Bool motor_has_failure(void);

/**
 * Get position of the motor in eighth steps
 */
I32 motor_get_position(void);

/**
 * Set the motor position. This does not move the
 * motor. It just sets the motor position internally
 * Useful if a limit switch is hit
 * @param position Position to set the motor to
 */
void motor_set_position(I32 position);

#endif //MC_MOTOR_H
