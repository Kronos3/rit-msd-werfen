//
// Created by tumbar on 1/18/23.
//

#include "motor.h"
#include "log.h"

#include "main.h"
#include "switch.h"

static TIM_HandleTypeDef* step_timer = NULL;
static I32 step_channel = -1;

static I32 motor_position = 0;

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

I32 motor_get_step_size(motor_step_t step, Bool reversed)
{
    I32 scalar = reversed ? -1 : 1;

    switch(step)
    {
        case MOTOR_STEP_FULL: return scalar * 8;
        case MOTOR_STEP_HALF: return scalar * 4;
        case MOTOR_STEP_QUARTER: return scalar * 2;
        case MOTOR_STEP_EIGHTH:
        case MOTOR_STEP_SIXTEENTH:
            // 1/16 step on this controller will not
            // change the speed compared to 1/8
            return scalar * 1;
    }
}

Status motor_speed(U16 prescaler, U16 arr)
{
    if (motor_is_running())
    {
        return STATUS_FAILURE;
    }

    step_timer->Init.Prescaler = prescaler - 1;
    step_timer->Init.Period = arr - 1;

    TIM_OC_InitTypeDef sConfigOC = {0};
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = arr/2-1;
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;

    if (HAL_TIM_PWM_ConfigChannel(
            step_timer, &sConfigOC, step_channel)
            != HAL_OK)
    {
        return STATUS_FAILURE;
    }

    return STATUS_SUCCESS;
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
    motor_position += motor_request.step_scalar;
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

Status motor_is_ready(motor_step_t step)
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

Bool motor_is_running()
{
    return motor_request.is_running;
}

void motor_set_ms(motor_step_t step)
{
    HAL_GPIO_WritePin(MS1_GPIO_Port, MS1_Pin, (step & MOTOR_PIN_MS1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(MS2_GPIO_Port, MS2_Pin, (step & MOTOR_PIN_MS2) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(MS3_GPIO_Port, MS3_Pin, (step & MOTOR_PIN_MS3) ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

Status motor_step(
        motor_step_t step, U16 n,
        Bool direction_reversed, MotorReply reply_cb)
{
    if (motor_is_ready(step) != STATUS_SUCCESS)
    {
        return STATUS_FAILURE;
    }

    // Check if we are against the limit switches
    if (direction_reversed && switch_limit_2_get() ||
        (!direction_reversed && switch_limit_1_get()))
    {
        return STATUS_FAILURE;
    }

    motor_request.step = step;
    motor_request.step_scalar = motor_get_step_size(step, direction_reversed);
    motor_request.i = 0;
    motor_request.n = n;
    motor_request.is_running = TRUE;
    motor_request.direction_reversed = direction_reversed;
    motor_request.reply_cb = reply_cb;

    // Set up the step size logic levels
    motor_set_ms(motor_request.step);

    // Go forwards or backwards
    HAL_GPIO_WritePin(DIR_GPIO_Port, DIR_Pin,
                      motor_request.direction_reversed ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // Wait for the MS pins to become stable
    HAL_Delay(1);

    // The PWM timer. @500Hz, timer each timer tick is a single motor step
    HAL_TIM_PWM_Start_IT(step_timer, step_channel);

    return STATUS_SUCCESS;
}

I32 motor_get_position(void)
{
    return motor_position;
}

void motor_set_position(const I32 position)
{
    motor_position = position;
}
