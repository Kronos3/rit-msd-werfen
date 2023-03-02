//
// Created by tumbar on 1/18/23.
//

#include "packet.h"
#include "crc.h"
#include "circular_buffer.h"
#include "switch.h"
#include "led.h"

#include <stm32l4xx_hal.h>
#include <string.h>

static void packet_handler(UART_HandleTypeDef* huart);

static U8 uart_rx_buffer[sizeof(Packet) * 4] = {0};
STATIC_ASSERT(sizeof(uart_rx_buffer) == sizeof(Packet) * 4, array_sizing);

CircularBuffer rx;

static Packet packet;

void packet_init(void)
{
    // Initiate the first uart RECV
    memset(uart_rx_buffer, 0, sizeof(uart_rx_buffer));
    circular_buf_init(&rx, uart_rx_buffer, sizeof(uart_rx_buffer));

    memset(&packet, 0, sizeof(packet));
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

void packet_task(void* huart)
{
    // Wait for the start bytes
    U16 start_bytes;
    while (circular_buf_size(&rx) >= 2)
    {
        // Wait for the start two bytes
        circular_buf_peek(&rx, (U8*) &start_bytes, 2);
        if (start_bytes == 0xADDE) // little endian byte swapped
        {
            break;
        }

        // Dump a single byte
        U8 c;
        circular_buf_get(&rx, &c);
    }

    if (circular_buf_size(&rx) >= sizeof(Packet))
    {
        circular_buf_get_n(&rx, (U8*) &packet, sizeof(Packet));

        // Validate the packet
        if (packet_validate(&packet) == STATUS_FAILURE)
        {
            return;
        }

        packet_handler(huart);
    }
}

void packet_isr_c(void* huart)
{
    U8 byte;
    HAL_StatusTypeDef status = HAL_UART_Receive(huart, &byte, 1, 0);

    if (status != HAL_OK)
    {
        // Error occurred on this byte,
        // Get rid of it
        return;
    }

    // Place the byte into the buffer
    circular_buf_put(&rx, byte);
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

    HAL_UART_Transmit(huart, (U8*) &reply_packet, sizeof(Packet), 100);
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
