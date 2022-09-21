//
// Created by tumbar on 9/21/22.
//

#ifndef WERFEN_RPITOPOLOGYDEFS_HPP
#define WERFEN_RPITOPOLOGYDEFS_HPP

#include <Fw/Types/BasicTypes.hpp>
#include <Fw/Types/MallocAllocator.hpp>

namespace Rpi
{
    namespace Allocation {

        // Malloc allocator for topology construction
        extern Fw::MallocAllocator mallocator;

    }

    // State for topology construction
    struct TopologyState
    {
    };
}

#endif //WERFEN_RPITOPOLOGYDEFS_HPP
