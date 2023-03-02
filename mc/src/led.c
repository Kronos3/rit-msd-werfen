//
// Created by tumbar on 3/2/23.
//


#include <stm32l4xx_hal.h>
#include <string.h>
#include "led.h"

#define ADC_TO_VOLTAGE(adc_) ((((F32)(adc_)) / (1 << 12)) * 3.3f)
#define ADC_NUM_INTEGRAL (20)

static Bool led_running = FALSE;
static Bool led_task_running = FALSE;
static F32 led_keep_voltage = 0.0f;

static F32 pid_p = 1.0f;
static F32 pid_i = 0.0f;
static F32 pid_d = 0.0f;

static F32 last_errors[ADC_NUM_INTEGRAL] = {0};
STATIC_ASSERT(sizeof(last_errors) / sizeof(last_errors[0]) == ADC_NUM_INTEGRAL, check_i_length);

static U32 last_errors_i = 0;
static F32 last_error_d = 0.0f;

static TIM_HandleTypeDef* led_tim = NULL;
static U16 led_chan = 0;

static TIM_HandleTypeDef* led_task_tim = NULL;

static volatile U16 light_sensor_adc = 0;

void led_sensor_init(void* hadc)
{
    // This DMA request is on circular buffer with length of 1
    // Which means that the value at this point will be the latest
    // value from ADC measuring the light level
    HAL_ADC_Start_DMA(hadc, (U32*)&light_sensor_adc, 1);

    // This timer tick at 100Hz will keep the light at a certain voltage
    // on the phototransistor when requested. The timer will always be on
    // and the requests will be process or ignored based on the type of
    // lighting that is requested.
    HAL_TIM_Base_Start_IT(led_task_tim);
}

void led_init(void* led_tim_, U16 led_chan_, void* task_tim_)
{
    led_tim = led_tim_;
    led_chan = led_chan_;
    led_task_tim = task_tim_;
}

static inline void led_start(void)
{
    HAL_TIM_PWM_Start(led_tim, led_chan);
    led_running = TRUE;
}

static inline F32 led_clamp(F32 pwm)
{
    if (pwm < 0.0)
    {
        pwm = 0.0f;
    }
    else if (pwm > 1.0)
    {
        pwm = 1.0f;
    }

    return pwm;
}

static inline void led_set_direct(F32 pwm)
{
    if (pwm == 0.0)
    {
        led_stop();
        return;
    }
    else if (!led_running)
    {
        led_start();
    }
    __HAL_TIM_SET_COMPARE(led_tim, led_chan, pwm * led_tim->Init.Period);
}

void led_set(F32 pwm)
{
    led_task_running = FALSE;
    led_set_direct(led_clamp(pwm));
}

Bool led_is_on(void)
{
    return led_running;
}

void led_voltage(F32 voltage)
{
    led_keep_voltage = voltage;

    memset(last_errors, 0, sizeof(last_errors));
    last_errors_i = 0;
    last_error_d = 0.0f;

    led_task_running = TRUE;
}

void led_stop()
{
    if (led_running)
    {
        HAL_TIM_PWM_Stop(led_tim, led_chan);
        led_running = FALSE;
    }
}

void led_set_p(F32 p)
{
    pid_p = p;
}

void led_set_i(F32 i)
{
    pid_i = i;
}

void led_set_d(F32 d)
{
    pid_d = d;
}


void led_task(void)
{
    if (!led_task_running)
    {
        return;
    }

    F32 current = ADC_TO_VOLTAGE(light_sensor_adc);
    F32 error = led_keep_voltage - current;

    // Push the latest error to the 'I' term
    last_errors[last_errors_i++] = error;
    last_errors_i %= ADC_NUM_INTEGRAL;

    F32 integral = 0.0f;
    for (U32 i = 0; i < sizeof(last_errors) / sizeof(last_errors[0]); i++)
    {
        integral += last_errors[i];
    }

    F32 u = (pid_p * error) + (pid_i * integral) + pid_d * (error - last_error_d);

    F32 pwm = led_clamp(u);
    led_set_direct(pwm);
}
