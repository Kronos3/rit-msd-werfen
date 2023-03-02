//
// Created by tumbar on 2/20/23.
//

#ifndef WERFEN_CIRCULAR_BUFFER_H
#define WERFEN_CIRCULAR_BUFFER_H


#include "gbl.h"

/// Opaque circular buffer structure
typedef struct
{
    U8* buffer;
    U32 head;
    U32 tail;
    U32 max; // of the buffer
    Bool full;
} CircularBuffer;

/// Pass in a storage buffer and size, returns a circular buffer handle
/// Requires: buffer is not NULL, size > 0 (size > 1 for the threadsafe
//  version, because it holds size - 1 elements)
/// Ensures: self has been created and is returned in an empty state
void circular_buf_init(CircularBuffer* self, U8* buffer, U32 size);

/// Reset the circular buffer to empty, head == tail. Data not cleared
/// Requires: self is valid and created by circular_buf_init
void circular_buf_reset(CircularBuffer* self);

/// Put that continues to add data if the buffer is full
/// Old data is overwritten
/// Note: if you are using the threadsafe version, this API cannot be used, because
/// it modifies the tail pointer in some cases. Use circular_buf_try_put instead.
/// Requires: self is valid and created by circular_buf_init
void circular_buf_put(CircularBuffer* self, U8 data);

/// Put that rejects new data if the buffer is full
/// Note: if you are using the threadsafe version, *this* is the put you should use
/// Requires: self is valid and created by circular_buf_init
/// Returns 0 on success, -1 if buffer is full
I32 circular_buf_try_put(CircularBuffer* self, U8 data);

/// Retrieve a value from the buffer
/// Requires: self is valid and created by circular_buf_init
/// Returns 0 on success, -1 if the buffer is empty
I32 circular_buf_get(CircularBuffer* self, U8* data);

/// Retrieve multiple bytes from the buffer
/// Requires: self is valid and created by circular_buf_init
/// Returns number of bytes read
U32 circular_buf_get_n(CircularBuffer* self, U8* data, U32 n);

/// CHecks if the buffer is empty
/// Requires: self is valid and created by circular_buf_init
/// Returns true if the buffer is empty
Bool circular_buf_empty(const CircularBuffer* self);

/// Checks if the buffer is full
/// Requires: self is valid and created by circular_buf_init
/// Returns true if the buffer is full
Bool circular_buf_full(const CircularBuffer* self);

/// Check the capacity of the buffer
/// Requires: self is valid and created by circular_buf_init
/// Returns the maximum capacity of the buffer
U32 circular_buf_capacity(const CircularBuffer* self);

/// Check the number of elements stored in the buffer
/// Requires: self is valid and created by circular_buf_init
/// Returns the current number of elements in the buffer
U32 circular_buf_size(const CircularBuffer* self);

/// Look ahead at values stored in the circular buffer without removing the data
/// Requires:
///		- self is valid and created by circular_buf_init
///		- look_ahead_counter is less than or equal to the value returned by circular_buf_size()
/// Returns 0 if successful, -1 if data is not available
I32 circular_buf_peek(const CircularBuffer* self, U8* data, U32 look_ahead_counter);

// TODO: int circular_buf_get_range(circular_buf_t self, U8 *data, U32 len);
// TODO: int circular_buf_put_range(circular_buf_t self, U8 * data, U32 len);

#endif //WERFEN_CIRCULAR_BUFFER_H
