//
// Created by tumbar on 1/18/23.
//

#include "motor.h"
#include "log.h"

#include "config.h"

static TIM_HandleTypeDef* step_timer = NULL;
static I32 step_channel = -1;

static MotorPosition motor_position = {0, 0};

static struct
{
    Bool direction_reversed;
    Bool is_running;
    motor_step_t step;
    I32 step_scalar;
    U16 i;
    U16 n;
    Bool direction;
    MotorReply reply_cb;
} motor_request = {
        .direction_reversed = FALSE,
        .is_running = FALSE,
        .step = MOTOR_STEP_FULL,
        .n = 0,
        .reply_cb = NULL,
};

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

void motor_init(void* step_timer_,
                I32 step_channel_)
{
    step_timer = step_timer_;
    step_channel = step_channel_;
}

void motor_tick(void)
{
    // Increment the position
    motor_position.sixteenth += motor_request.step_scalar;
    motor_position.integer = motor_position.sixteenth / 16;
    motor_position.sixteenth = motor_position.sixteenth % 16;

    motor_request.i++;

    if (motor_request.i >= motor_request.n)
    {
        motor_stop();
    }
}

void motor_stop(void)
{
    HAL_TIM_PWM_Stop(step_timer, step_channel);

    MotorReply reply_cb = motor_request.reply_cb;

    motor_request.step = 0;
    motor_request.step_scalar = 0;
    motor_request.i = 0;
    motor_request.n = 0;
    motor_request.is_running = FALSE;
    motor_request.direction_reversed = FALSE;
    motor_request.reply_cb = NULL;

    if (reply_cb)
    {
        reply_cb();
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

    if (motor_request.is_running)
    {
        log_printf("Motor is busy with another request");
        return STATUS_FAILURE;
    }

    return STATUS_SUCCESS;
}

Status motor_step(
        motor_step_t step, U16 n,
        Bool direction_reversed, MotorReply reply_cb)
{
    if (motor_is_ready(step) != STATUS_SUCCESS)
    {
        return STATUS_FAILURE;
    }

    motor_request.step = step;
    motor_request.step_scalar = motor_get_step_size(step);
    motor_request.i = 0;
    motor_request.n = n;
    motor_request.is_running = TRUE;
    motor_request.direction_reversed = direction_reversed;
    motor_request.reply_cb = reply_cb;

    // Set up the step size logic levels
    HAL_GPIO_WritePin(MS1_PORT, MS1_PIN, (motor_request.step & MOTOR_PIN_MS1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(MS2_PORT, MS2_PIN, (motor_request.step & MOTOR_PIN_MS2) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(MS3_PORT, MS3_PIN, (motor_request.step & MOTOR_PIN_MS3) ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // Enable the controller if needed
    HAL_GPIO_WritePin(ENABLE_PORT, ENABLE_PIN, GPIO_PIN_RESET);

    // Go forwards or backwards
    HAL_GPIO_WritePin(DIR_PORT, DIR_PIN, motor_request.direction_reversed ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // Wait for the MS pins to become stable
    HAL_Delay(1);

    // The PWM timer. @500Hz, timer each timer tick is a single motor step
    HAL_TIM_PWM_Start(step_timer, step_channel);

    return STATUS_SUCCESS;
}

MotorPosition motor_get_position(void)
{
    return motor_position;
}

void motor_set_position(const MotorPosition position)
{
    motor_position = position;
}
