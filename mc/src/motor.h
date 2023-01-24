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
    MOTOR_MASK_STEP = 0xFFFF,
    MOTOR_MASK_DIRECTION = 0xFFFF0000
} motor_mask;

typedef struct
{
    U32 integer;
    U32 sixteenth;
} MotorPosition;

typedef void (*MotorReply)(void);

/**
 * Initialize the timers and channels being used to
 * operate the motor
 * @param step_timer Timer used for PWM output generation
 * @param step_channel Channel on step timer for step pin
 * @param job_timer Slave of step timer used for step counting
 */
void motor_init(void* step_timer,
                I32 step_channel,
                void* job_timer);

/**
 * Apply n steps to the motor
 * @param step Step size
 * @param n number of steps
 * @param direction_reversed TRUE for forward and false for backward
 * @param reply_cb callback when motor request is done
 */
Status motor_step(motor_step_t step, U16 n,
                  Bool direction_reversed,
                  MotorReply reply_cb);

void motor_stop(void);

/**
 * Apply arithmetic addition operation
 * A + (R ? -1 : 1) * N * B
 * @param add_a A
 * @param add_b B
 * @param mul N
 * @param reverse R
 * @return
 */
MotorPosition motor_position_add(
        MotorPosition add_a,
        MotorPosition add_b,
        U16 mul, Bool reverse);

/**
 * Get the position of the motor on the stage
 * @return position in SIXTEENTH steps
 */
MotorPosition motor_get_position(void);

/**
 * Set the motor position. This does not move the
 * motor. It just sets the motor position internally
 * Useful if a limit switch is hit
 * @param position Position to set the motor to
 */
void motor_set_position(MotorPosition position);

/**
 * Run a single 0.5us clock cycle for our driver
 * Used only during an executing motor request
 */
void motor_tick(void);

#endif //MC_MOTOR_H
