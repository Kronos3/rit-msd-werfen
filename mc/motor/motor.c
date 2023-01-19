//
// Created by tumbar on 1/18/23.
//

#include <motor.h>
#include "log.h"

typedef enum
{
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
} motor_state_t;

static I32 motor_position = 0;

static struct
{
    Bool is_busy;
    Bool direction_reversed;
    motor_step_t step;
    I32 n;
    motor_state_t state;
} motor_request;

static void motor_run_request(motor_step_t step, I32 n)
{
    motor_request.is_busy = TRUE;
    motor_request.step = step;
    motor_request.n = n;
    motor_request.state = MOTOR_STATE_SETUP;
    motor_request.direction_reversed = FALSE;

    if (motor_request.n < 0)
    {
        motor_request.direction_reversed = TRUE;
        motor_request.n = -motor_request.n;
    }

    // TODO(tumbar) Start timer
}

static void motor_clear_request(void)
{
    motor_request.is_busy = FALSE;
    motor_request.step = 0;
    motor_request.n = 0;
    motor_request.state = MOTOR_STATE_SETUP;
}

static I32 motor_get_step_size(motor_step_t step)
{
    switch(step)
    {
        case MOTOR_STEP_FULL: return 16;
        case MOTOR_STEP_HALF: return 8;
        case MOTOR_STEP_QUARTER: return 4;
        case MOTOR_STEP_EIGHTH: return 2;
        case MOTOR_STEP_SIXTEENTH: return 1;
    }
}

static void motor_tick(void)
{
    // TODO(tumbar) Check for e-stop
    // TODO(tumbar) Check for limit switch

    switch(motor_request.state)
    {
        case MOTOR_STATE_SETUP:
            // Set up the step size logic levels
            pin_set(MS1, motor_request.step & MOTOR_PIN_MS1);
            pin_set(MS2, motor_request.step & MOTOR_PIN_MS2);
            pin_set(MS3, motor_request.step & MOTOR_PIN_MS3);

            // Step should already be low
            pin_set(STEP, LOW);
            pin_set(DIR, motor_request.direction_reversed ? HIGH : LOW);

            motor_request.state = MOTOR_STATE_STEP_RISING;
            break;
        case MOTOR_STATE_STEP_RISING:
            // Check if there are any cycles left
            if (motor_request.n > 0)
            {
                pin_set(STEP, HIGH);
                motor_request.state = MOTOR_STATE_STEP_HIGH_HOLD;

                // The motor steps on a rising STEP edge
                // Increment the internal motor position
                motor_position += motor_get_step_size(motor_request.step) *
                        (motor_request.direction_reversed ? -1 : 1);
            }
            else
            {
                // No more cycles
                motor_clear_request();
                // TODO(tumbar) Stop timer
            }
            break;
        case MOTOR_STATE_STEP_HIGH_HOLD:
            motor_request.state = MOTOR_STATE_STEP_FALLING;
            break;
        case MOTOR_STATE_STEP_FALLING:
            pin_set(STEP, LOW);
            motor_request.n--;
            motor_request.state = MOTOR_STATE_STEP_LOW_HOLD;
            break;
        case MOTOR_STATE_STEP_LOW_HOLD:
            // Next cycle
            motor_request.state = MOTOR_STATE_STEP_RISING;
            break;
    }
}

Status motor_step(motor_step_t step, I32 n)
{
    switch(step)
    {
        case MOTOR_STEP_FULL:
        case MOTOR_STEP_HALF:
        case MOTOR_STEP_QUARTER:
        case MOTOR_STEP_EIGHTH:
        case MOTOR_STEP_SIXTEENTH:
            log_printf("Invalid step size %d", step);
            return STATUS_FAILURE;
    }

    if (motor_request.is_busy)
    {
        log_printf("Motor is busy with another request");
        return STATUS_FAILURE;
    }

    motor_run_request(step, n);
    return STATUS_SUCCESS;
}

I32 motor_get_position(void)
{
    return motor_position;
}

Bool motor_is_busy(void)
{
    return motor_request.is_busy;
}

void motor_set_position(I32 position)
{
    motor_position = position;
}
