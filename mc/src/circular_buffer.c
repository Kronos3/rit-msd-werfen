#include <assert.h>

#include "circular_buffer.h"
#include "gbl.h"

static inline U32 advance_headtail_value(U32 value, U32 max)
{
    return (value + 1) % max;
}

static void advance_head_pointer(CircularBuffer* self)
{
    assert(self);

    if (circular_buf_full(self))
    {
        self->tail = advance_headtail_value(self->tail, self->max);
    }

    self->head = advance_headtail_value(self->head, self->max);
    self->full = (self->head == self->tail);
}

void circular_buf_init(CircularBuffer* self, U8* buffer, U32 size)
{
    assert(buffer && size);
    assert(self);

    self->buffer = buffer;
    self->max = size;
    circular_buf_reset(self);

    assert(circular_buf_empty(self));
}

void circular_buf_reset(CircularBuffer* self)
{
    assert(self);

    self->head = 0;
    self->tail = 0;
    self->full = FALSE;
}

U32 circular_buf_size(const CircularBuffer* self)
{
    assert(self);

    U32 size = self->max;

    if (!circular_buf_full(self))
    {
        if (self->head >= self->tail)
        {
            size = (self->head - self->tail);
        }
        else
        {
            size = (self->max + self->head - self->tail);
        }
    }

    return size;
}

U32 circular_buf_capacity(const CircularBuffer* self)
{
    assert(self);

    return self->max;
}

void circular_buf_put(CircularBuffer* self, U8 data)
{
    assert(self && self->buffer);

    self->buffer[self->head] = data;

    advance_head_pointer(self);
}

I32 circular_buf_try_put(CircularBuffer* self, U8 data)
{
    int r = -1;

    assert(self && self->buffer);

    if (!circular_buf_full(self))
    {
        self->buffer[self->head] = data;
        advance_head_pointer(self);
        r = 0;
    }

    return r;
}

I32 circular_buf_get(CircularBuffer* self, U8* data)
{
    assert(self && data && self->buffer);

    if (circular_buf_empty(self))
    {
        return -1;
    }

    *data = self->buffer[self->tail];
    self->tail = advance_headtail_value(self->tail, self->max);
    self->full = FALSE;
    return 0;
}

U32 circular_buf_get_n(CircularBuffer* self, U8* data, U32 n)
{
    U32 i;
    for (i = 0; i < n; i++)
    {
        if (circular_buf_get(self, data + i) < 0)
        {
            break;
        }
    }

    return i;
}

Bool circular_buf_empty(const CircularBuffer* self)
{
    assert(self);

    return (!circular_buf_full(self) && (self->head == self->tail));
}

Bool circular_buf_full(const CircularBuffer* self)
{
    assert(self);

    return self->full;
}

I32 circular_buf_peek(const CircularBuffer* self, U8* data, U32 look_ahead_counter)
{
    I32 r = -1;
    U32 pos;

    assert(self && data && self->buffer);

    // We can't look beyond the current buffer size
    if (circular_buf_empty(self) || look_ahead_counter > circular_buf_size(self))
    {
        return r;
    }

    pos = self->tail;
    for (U32 i = 0; i < look_ahead_counter; i++)
    {
        data[i] = self->buffer[pos];
        pos = advance_headtail_value(pos, self->max);
    }

    return 0;
}
