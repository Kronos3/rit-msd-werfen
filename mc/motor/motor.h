//
// Created by tumbar on 1/18/23.
//

#ifndef MC_MOTOR_H
#define MC_MOTOR_H

#include <gbl.h>

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

/**
 * Apply n steps to the motor
 * @param step
 * @param n
 */
Status motor_step(motor_step_t step, I32 n);

/**
 * Get the position of the motor on the stage
 * @return position in SIXTEENTH steps
 */
I32 motor_get_position(void);

/**
 * Check if there is a currently active motor request
 * @return TRUE if active motor request
 */
Bool motor_is_busy(void);

/**
 * Set the motor position. This does not move the
 * motor. It just sets the motor position internally
 * Useful if a limit switch is hit
 * @param position Position to set the motor to
 */
void motor_set_position(I32 position);

#endif //MC_MOTOR_H
