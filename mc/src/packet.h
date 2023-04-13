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
    OPCODE_SPEED,          //!< Set the motor tick rate
    OPCODE_STOP,           //!< Stop a running motion
    OPCODE_SET_POSITION,   //!< Set the current position of the stage
    OPCODE_GET_POSITION,   //!< Get current motor position
    OPCODE_LED_PWM,        //!< Directly set the PWM level of LED
    OPCODE_LED_VOLTAGE,    //!< PID around a voltage on the phototransistor
    OPCODE_LED_PID,        //!< Set a PID parameter on the voltage controller
    OPCODE_SWITCH_DEBOUNCE,//!< Set the limit switch debounce delay in ms
    OPCODE_EMERGENCY_STOP, //!< Lock the system until the lock is cleared
    OPCODE_EMERGENCY_CLEAR,//!< Clear the ESTOP lock
    OPCODE_LIMIT_STEP_OFF, //!< Set the size and number of steps from the limit switch to move when moving off a limit switch
} opcode_t;

typedef enum
{
    // PID Parameters
    FLAGS_PID_P = 0,
    FLAGS_PID_I = 1,
    FLAGS_PID_D = 2,

    // Response flags
    FLAGS_LIMIT_1 = 1 << 0, //!< Limit switch 1
    FLAGS_LIMIT_2 = 1 << 1, //!< Limit switch 2
    FLAGS_ESTOP = 1 << 2,   //!< E-STOP
    FLAGS_RUNNING = 1 << 3, //!< Running motor request
    FLAGS_LED = 1 << 4,     //!< LED is on
    FLAGS_FAILURE = 1 << 5, //!< The last motor request hit a limit switch
    FLAGS_CALIBRATED = 1 << 6, //!< Indicated whether a set_position() has get run yet
} flags_t;

typedef struct
{
    U8 start[2]; // 0xDEAD
    U16 opcode;
    U32 arg;
    U8 flags;
    U8 checksum;
    U8 stop[2]; // 0xBEEF
} Packet;

STATIC_ASSERT(sizeof(Packet) == 12, packet_size);

void packet_init(void* huart);
void packet_task(void* huart);

#endif //MC_PACKET_H
