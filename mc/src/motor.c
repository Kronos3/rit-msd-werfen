//
// Created by tumbar on 1/18/23.
//

#include "motor.h"
#include "log.h"

#include "config.h"
#include "switch.h"

static I32 motor_position = 0;
static TIM_HandleTypeDef* timer = NULL;

static struct
{
    Bool direction_reversed;
    motor_step_t step;
    I32 n;
    motor_state_t state;
    void (*reply_cb)(Status status);
} motor_request = {
        .direction_reversed = FALSE,
        .step = MOTOR_STEP_FULL,
        .n = 0,
        .state = MOTOR_STATE_IDLE,
        .reply_cb = NULL,
};

void motor_init(void* timer_)
{
    timer = timer_;
}

static void motor_run_request(motor_step_t step, I32 n,
                              MotorReply reply_cb)
{
    motor_request.step = step;
    motor_request.n = n;
    motor_request.state = MOTOR_STATE_SETUP;
    motor_request.direction_reversed = FALSE;
    motor_request.reply_cb = reply_cb;

    if (motor_request.n < 0)
    {
        motor_request.direction_reversed = TRUE;
        motor_request.n = -motor_request.n;
    }

    HAL_TIM_Base_Start_IT(timer);
}

static void motor_stop(Status status)
{
    motor_request.step = 0;
    motor_request.n = 0;
    motor_request.state = MOTOR_STATE_IDLE;
    motor_request.direction_reversed = FALSE;

    HAL_TIM_Base_Stop_IT(timer);

    MotorReply cb = motor_request.reply_cb;
    motor_request.reply_cb = NULL;

    if (cb)
    {
        cb(status);
    }

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

void motor_tick(void)
{
    // Check if E-stop signal
    if (switch_e_stop_set() || motor_request.state == MOTOR_STATE_ESTOP)
    {
        motor_request.state = MOTOR_STATE_ESTOP;
    }
    else if (switch_limit_a_set()
             || switch_limit_b_set())
    {
        motor_request.state = MOTOR_STATE_EXIT;
    }

    switch(motor_request.state)
    {
        case MOTOR_STATE_SETUP:
            // Set up the step size logic levels
            HAL_GPIO_WritePin(MS1_PORT, MS1_PIN, (motor_request.step & MOTOR_PIN_MS1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(MS2_PORT, MS2_PIN, (motor_request.step & MOTOR_PIN_MS2) ? GPIO_PIN_SET : GPIO_PIN_RESET);
            HAL_GPIO_WritePin(MS3_PORT, MS3_PIN, (motor_request.step & MOTOR_PIN_MS3) ? GPIO_PIN_SET : GPIO_PIN_RESET);

            // Enable the controller if needed
            HAL_GPIO_WritePin(ENABLE_PORT, ENABLE_PIN, GPIO_PIN_RESET);

            // Step should already be low
            HAL_GPIO_WritePin(STEP_PORT, STEP_PIN, GPIO_PIN_RESET);

            // Go forwards or backwards
            HAL_GPIO_WritePin(DIR_PORT, DIR_PIN, motor_request.direction_reversed ? GPIO_PIN_SET : GPIO_PIN_RESET);

            motor_request.state = MOTOR_STATE_STEP_RISING;
            break;
        case MOTOR_STATE_STEP_RISING:
            // Check if there are any cycles left
            if (motor_request.n > 0)
            {
                HAL_GPIO_WritePin(STEP_PORT, STEP_PIN, GPIO_PIN_SET);
                motor_request.state = MOTOR_STATE_STEP_HIGH_HOLD;

                // The motor steps on a rising STEP edge
                // Increment the internal motor position
                motor_position += motor_get_step_size(motor_request.step) *
                        (motor_request.direction_reversed ? -1 : 1);
                break;
            }
            // No more cycles, fallthrough
        case MOTOR_STATE_EXIT:
        case MOTOR_STATE_IDLE:
            motor_stop(STATUS_SUCCESS);
            break;
        case MOTOR_STATE_STEP_HIGH_HOLD:
            motor_request.state = MOTOR_STATE_STEP_FALLING;
            break;
        case MOTOR_STATE_STEP_FALLING:
            HAL_GPIO_WritePin(STEP_PORT, STEP_PIN, GPIO_PIN_RESET);
            motor_request.n--;
            motor_request.state = MOTOR_STATE_STEP_LOW_HOLD;
            break;
        case MOTOR_STATE_STEP_LOW_HOLD:
            // Next cycle
            motor_request.state = MOTOR_STATE_STEP_RISING;
            break;
        case MOTOR_STATE_ESTOP:
            // Disable the controller
            HAL_GPIO_WritePin(ENABLE_PORT, ENABLE_PIN, GPIO_PIN_SET);

            // Once the ESTOP is tripped during an executing motor request,
            //   we will hang here forever. The only way to exit out of this
            //   state is to release the ESTOP and hard reset the microcontroller
            motor_stop(STATUS_FAILURE);
            break;
    }
}

static Status motor_is_ready(motor_step_t step)
{
    switch(step)
    {
        case MOTOR_STEP_FULL:
        case MOTOR_STEP_HALF:
        case MOTOR_STEP_QUARTER:
        case MOTOR_STEP_EIGHTH:
        case MOTOR_STEP_SIXTEENTH:
            break;
        default:
            log_printf("Invalid step size %d", step);
            return STATUS_FAILURE;
    }

    if (motor_request.state != MOTOR_STATE_IDLE)
    {
        log_printf("Motor is busy with another request, state %d", motor_request.state);
        return STATUS_FAILURE;
    }

    return STATUS_SUCCESS;
}

Status motor_step(motor_step_t step, I32 n, MotorReply reply_cb)
{
    if (motor_is_ready(step) != STATUS_SUCCESS)
    {
        return STATUS_FAILURE;
    }

    motor_run_request(step, n, reply_cb);
    return STATUS_SUCCESS;
}

I32 motor_get_position(void)
{
    return motor_position;
}

void motor_set_position(I32 position)
{
    motor_position = position;
}
