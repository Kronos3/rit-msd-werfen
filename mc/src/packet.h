//
// Created by tumbar on 1/18/23.
//

#ifndef MC_PACKET_H
#define MC_PACKET_H

#include "gbl.h"
#include "motor.h"

typedef enum
{
    OPCODE_IDLE,           //!< Idle packet for pinging Mc
    OPCODE_RELATIVE,       //!< Relative motion
    OPCODE_ABSOLUTE,       //!< Absolute motion
    OPCODE_SET,            //!< Set the current position of the stage
    OPCODE_HOME,           //!< Step until limit switch
    OPCODE_GET_POSITION,   //!< Get current motor position
} opcode_t;

typedef enum
{
    FLAGS_LIMIT_A = 1 << 0, //!< Limit switch A
    FLAGS_LIMIT_B = 1 << 1, //!< Limit switch B
    FLAGS_ESTOP = 1 << 2,   //!< E-STOP

} flags_t;

typedef struct
{
    U8 start[2];
    U16 opcode;
    U32 arg1;
    U32 arg2;
    U16 flags;
    U16 checksum;
} Packet;

STATIC_ASSERT(sizeof(Packet) == 16, packet_size);

void packet_task(void* huart);

#endif //MC_PACKET_H
