//
// Created by tumbar on 1/18/23.
//

#include "motor.h"
#include "log.h"

#include "config.h"

static TIM_HandleTypeDef* step_timer = NULL;
static I32 step_channel = -1;
static TIM_HandleTypeDef* job_timer = NULL;

static MotorPosition motor_position = {0, 0};

static struct
{
    Bool direction_reversed;
    Bool is_running;
    motor_step_t step;
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

MotorPosition motor_position_add(
        MotorPosition add_a,
        MotorPosition add_b,
        U16 mul, Bool reverse)
{
    MotorPosition out = add_a;
    add_b.integer *= mul;
    add_b.sixteenth *= mul;

    out.integer += (reverse ? -1 : 1) * add_b.integer;
    out.sixteenth += (reverse ? -1 : 1) * add_b.sixteenth / 16;

    out.integer += out.sixteenth / 16;
    out.sixteenth %= 16;
    return out;
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

void motor_init(void* step_timer_,
                I32 step_channel_,
                void* job_timer_)
{
    step_timer = step_timer_;
    step_channel = step_channel_;
    job_timer = job_timer_;
}

void motor_stop(void)
{
    HAL_TIM_PWM_Stop(step_timer, step_channel);
    HAL_TIM_Base_Stop_IT(job_timer);

    MotorPosition step = {
            0, motor_get_step_size(motor_request.step)
    };

    motor_position = motor_position_add(
            motor_position,
            step,
            motor_request.n,
            motor_request.direction_reversed);

    MotorReply reply_cb = motor_request.reply_cb;

    motor_request.step = 0;
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

    job_timer->Instance->ARR = n;

    // Start the timers, they will be on a common clock
    HAL_TIM_PWM_Start(step_timer, step_channel);
    HAL_TIM_Base_Start_IT(job_timer);

    return STATUS_SUCCESS;
}

MotorPosition motor_get_position(void)
{
    if (motor_request.is_running)
    {
        // Add the current position according to the job
        // timer to the current position when the request
        // start
        MotorPosition step = {
                0, motor_get_step_size(motor_request.step)
        };

        return motor_position_add(
                motor_position,
                step,
                job_timer->Instance->CNT,
                motor_request.direction_reversed);
    }

    return motor_position;
}

void motor_set_position(const MotorPosition position)
{
    motor_position = position;
}
