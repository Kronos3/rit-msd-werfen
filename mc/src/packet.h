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
    OPCODE_STEP,           //!< Single step of motor
    OPCODE_SET,            //!< Set the current position of the stage
    OPCODE_GO_TO,          //!< Go to position
    OPCODE_HOME,           //!< Step until limit switch
} opcode_t;

typedef struct
{
    U8 start[2];
    U16 opcode;
    U32 argument;
    U16 checksum;
    U8 end[2];
} Packet;

STATIC_ASSERT(sizeof(Packet) == 12, packet_size);

void packet_task(void);

#endif //MC_PACKET_H
