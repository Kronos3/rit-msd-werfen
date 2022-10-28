#ifndef WERFEN_CAMBUFFER_HPP
#define WERFEN_CAMBUFFER_HPP

#include "fprime/Fw/Types/Serializable.hpp"
#include "opencv2/core/mat.hpp"
//#include "libcamera/libcamera/framebuffer.h"
//#include "Rpi/Cam/v2/libcamera_app_v2.h"

#include <functional>
#include <atomic>

namespace Rpi
{
    class CamBuffer
    {
    public:
        CamBuffer();
        explicit CamBuffer(U32 id_);

        U32 id;
        cv::Mat mat;

        void incref();
        void decref();
        bool in_use() const;

    private:
        I32 ref_count;
    };
}

#endif //WERFEN_CAMBUFFER_HPP
