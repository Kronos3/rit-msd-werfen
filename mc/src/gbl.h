//
// Created by tumbar on 1/18/23.
//

#ifndef MC_GBL_H
#define MC_GBL_H

#include <stdint.h>

typedef int8_t I8;
typedef uint8_t U8;
typedef int16_t I16;
typedef uint16_t U16;
typedef int32_t I32;
typedef uint32_t U32;

typedef enum
{
    FALSE = 0,
    TRUE = 1,
} Bool;

typedef enum
{
    STATUS_FAILURE = -1,
    STATUS_SUCCESS = 0
} Status;

#define STATIC_ASSERT(condition, name) typedef U8 __##name##_assert__[(condition) ? 1 : -1]

#endif //MC_GBL_H
