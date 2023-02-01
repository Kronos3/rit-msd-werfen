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
    /**
     * The idle state will stop the running motor request
     * Nominally this should not run in the motor tick
     */
    MOTOR_STATE_IDLE,

    /**
     * Set the MS1 MS2 & MS3 control
     * lines to the correct state to select
     * the step size
     */
    MOTOR_STATE_SETUP,

    /**
     * Rising edge on the step signal will run
     * a single step with the selected MS lines
     * from the setup step.
     */
    MOTOR_STATE_STEP_RISING,

    /**
     * Holds the signal high so that it stays high
     * for two clock cycles
     */
    MOTOR_STATE_STEP_HIGH_HOLD,

    /**
     * Drop the step down to low to prepare for the next
     * step
     */
    MOTOR_STATE_STEP_FALLING,

    /**
     * Keep the signal low for a second clock cycle
     */
    MOTOR_STATE_STEP_LOW_HOLD,

    /**
     * E-stop has been hit, keep the timer running to keep checking
     * the E-stop condition. This MC doesn't have an EXTI meaning
     * we need to poll via the timer
     */
    MOTOR_STATE_ESTOP,

    /**
     * This state is an early exit state that will clean up the
     * step controller signaling.
     */
    MOTOR_STATE_EXIT,
} motor_state_t;

typedef void (*MotorReply)(Status status);

void motor_init(void* timer_);

/**
 * Apply n steps to the motor
 * @param step Step size
 * @param n number of steps
 * @param reply_cb callback when motor request is done
 */
Status motor_step(motor_step_t step, I32 n, MotorReply reply_cb);

/**
 * Get the position of the motor on the stage
 * @return position in SIXTEENTH steps
 */
I32 motor_get_position(void);

/**
 * Get the current motor state
 * @return motor state
 */
motor_state_t motor_state(void);

/**
 * Set the motor position. This does not move the
 * motor. It just sets the motor position internally
 * Useful if a limit switch is hit
 * @param position Position to set the motor to
 */
void motor_set_position(I32 position);

/**
 * Run a single 0.5us clock cycle for our driver
 * Used only during an executing motor request
 */
void motor_tick(void);

#endif //MC_MOTOR_H
