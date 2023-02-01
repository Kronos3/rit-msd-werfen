//
// Created by tumbar on 1/18/23.
//

#include "packet.h"
#include "crc.h"

#include <stm32f1xx_hal.h>
#include <string.h>

static U8 uart_rx_buffer[sizeof(Packet)];
static Packet packet;

static inline void packet_receive(UART_HandleTypeDef* huart)
{
    HAL_UART_Receive_DMA(huart, uart_rx_buffer, sizeof(Packet));
}

void packet_task(void* huart)
{
    packet_receive(huart);
}

static U16 packet_compute_checksum(const Packet* pkt)
{
    return crc16((const U8*) pkt, sizeof(Packet) - 2);
}

static void reply(UART_HandleTypeDef* huart, U32 arg1, U32 arg2)
{
    static Packet reply_packet;
    reply_packet = packet;
    reply_packet.arg1 = arg1;
    reply_packet.arg2 = arg2;
    reply_packet.checksum = packet_compute_checksum(&reply_packet);

    HAL_UART_Transmit(huart, (U8*) &reply_packet, sizeof(Packet), 100);
}

static void packet_handler(UART_HandleTypeDef* huart)
{
    switch((opcode_t)packet.opcode)
    {
        case OPCODE_IDLE:
            reply(huart, 0, 0);
            break;
        case OPCODE_RELATIVE: {
            motor_step_t step = packet.arg1 & MOTOR_MASK_STEP;
            Bool reversed = (packet.arg1 & MOTOR_MASK_DIRECTION) != 0;
            Status status = motor_step(step, packet.arg2 & 0xFFFF, reversed, NULL);

            reply(huart, status, 0);
        }
            break;
        case OPCODE_ABSOLUTE:
            break;
        case OPCODE_SET:
            break;
        case OPCODE_HOME:
            break;
        case OPCODE_GET_POSITION: {
            MotorPosition position = motor_get_position();
            reply(huart, position.integer, position.sixteenth);
        }
            break;
    }
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef* huart)
{
    memcpy(&packet, uart_rx_buffer, sizeof(Packet));
    packet_receive(huart);
    packet_handler(huart);
}
