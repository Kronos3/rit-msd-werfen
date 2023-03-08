//
// Created by tumbar on 1/18/23.
//

#include "packet.h"
#include "crc.h"
#include "switch.h"
#include "led.h"

#include "main.h"

#include <stm32l4xx_hal.h>
#include <string.h>

static void packet_handler(UART_HandleTypeDef* huart);

static Packet rx_buffer = {0};
static volatile Bool packet_ready = FALSE;
static Packet packet = {0};

static void packet_receive(UART_HandleTypeDef* huart)
{
    HAL_UART_Receive_IT(huart, (U8*)&rx_buffer, sizeof(Packet));
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    memcpy(&packet, &rx_buffer, sizeof(Packet));
    packet_ready = TRUE;

    // Receive the next packet into a new buffer
    packet_receive(huart);
}

void packet_init(void* huart)
{
    // Initiate the first uart RECV
    memset(&rx_buffer, 0, sizeof(rx_buffer));
    memset(&packet, 0, sizeof(packet));

    packet_receive(huart);
}

static Status packet_validate(const Packet* self)
{
    U8 crc = crc8((U8*)self, offsetof(Packet, checksum));
    if (crc != self->checksum)
    {
        return STATUS_FAILURE;
    }

    return (
            self->start[0] == 0xDE &&
            self->start[1] == 0xAD &&
            self->stop[0] == 0xBE &&
            self->stop[1] == 0xEF
            ) ? STATUS_SUCCESS : STATUS_FAILURE;
}

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
    static Bool on = FALSE;
    on = !on;
    HAL_GPIO_WritePin(LED_GPIO_Port, LED_Pin, on ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // do nothing here
}

void packet_task(void* huart)
{
    if (packet_ready)
    {
        packet_ready = FALSE;

        // Make sure the packet is ok
        if (packet_validate(&packet) == STATUS_FAILURE)
        {
            return;
        }

        packet_handler(huart);
    }
}

static U8 packet_compute_checksum(const Packet* pkt)
{
    return crc8((const U8*) pkt, sizeof(Packet) - 2);
}

static void reply(UART_HandleTypeDef* huart, U32 arg)
{
    static Packet reply_packet;
    reply_packet = packet;
    reply_packet.arg = arg;
    reply_packet.checksum = packet_compute_checksum(&reply_packet);

    reply_packet.flags = (
        switch_limit_1_get() ? FLAGS_LIMIT_1 : 0 |
        switch_limit_2_get() ? FLAGS_LIMIT_2 : 0 |
        switch_e_stop_get() ? FLAGS_ESTOP : 0 |
        motor_is_running() ? FLAGS_RUNNING : 0 |
        led_is_on() ? FLAGS_LED : 0
    );

    HAL_UART_Transmit_IT(huart, (U8*) &reply_packet, sizeof(Packet));
}

static void clear_ms_lines(void)
{
    // Clear out the motor step size signals to turn off
    // the LEDs
    motor_set_ms(0);
}

static void packet_handler(UART_HandleTypeDef* huart)
{
    switch((opcode_t)packet.opcode)
    {
        case OPCODE_IDLE:
            reply(huart, 0);
            break;
        case OPCODE_RELATIVE: {
            motor_step_t step = packet.flags & MOTOR_MASK_STEP;
            Bool reversed = (packet.flags & MOTOR_MASK_DIRECTION) ? TRUE : FALSE;
            Status status = motor_step(step, packet.arg, reversed, clear_ms_lines);
            reply(huart, status);
        }
            break;
        case OPCODE_ABSOLUTE: {
            I32 desired_position = (I32)packet.arg;
            I32 delta = desired_position - motor_get_position();

            // Compute how many steps at the requested size to take
            motor_step_t step = packet.flags & MOTOR_MASK_STEP;
            I32 nsteps = delta / motor_get_step_size(step, FALSE);
            nsteps = nsteps < 0 ? -nsteps : nsteps;

            Bool reversed = delta < 0;
            Status status = motor_step(step, nsteps, reversed, clear_ms_lines);
            reply(huart, status);
        }
            break;
        case OPCODE_SPEED: {
            // Compute prescaler + arr from Hz
            U16 psc = 80; // 1 Mhz clock
            U16 arr = (SystemCoreClock / psc) / packet.arg;
            Status status = motor_speed(psc, arr);
            reply(huart, status);
        }
            break;
        case OPCODE_SET_POSITION:
            motor_set_position((I32)packet.arg);
            reply(huart, 0);
            break;
        case OPCODE_GET_POSITION:
            reply(huart, motor_get_position());
            break;
        case OPCODE_LED_PWM:
            led_set(*(F32*)&packet.arg);
            break;
        case OPCODE_LED_VOLTAGE:
            led_voltage(*(F32*)&packet.arg);
            break;
        case OPCODE_LED_PID:
            switch(packet.flags)
            {
                case FLAGS_PID_P:
                    led_set_p(*(F32*)&packet.arg);
                    break;
                case FLAGS_PID_I:
                    led_set_i(*(F32*)&packet.arg);
                    break;
                case FLAGS_PID_D:
                    led_set_d(*(F32*)&packet.arg);
                    break;
            }
            reply(huart, 0);
            break;
        default:
            reply(huart, 0);
            break;
    }
}
