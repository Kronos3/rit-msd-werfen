
#ifndef WERFEN_CAM_HPP
#define WERFEN_CAM_HPP

#include <Rpi/Cam/CamComponentAc.hpp>
#include "CamCfg.h"
#include "CameraConfig.hpp"
#include "CamBuffer.hpp"
#include <core/completed_request.hpp>
#include <queue>
#include <mutex>

namespace Rpi
{
    class LibcameraApp;
    class Cam : public CamComponentBase
    {
//        friend LibcameraApp;

    public:
        explicit Cam(const char* compName);
        ~Cam() override;

        void init(NATIVE_INT_TYPE instance);

        void configure(I32 width, I32 height,
                       I32 rotation,
                       bool vflip, bool hflip);

        void startStreamThread(const Fw::StringBase &name);
        void quitStreamThread();

    PRIVATE:
        void parametersLoaded() override;

        void get_config(CameraConfig& config);
        bool frameGet_handler(NATIVE_INT_TYPE portNum, U32 frameId, Rpi::CamFrame &frame) override;
        void incref_handler(NATIVE_INT_TYPE portNum, U32 frameId) override;
        void decref_handler(NATIVE_INT_TYPE portNum, U32 frameId) override;

        void CAPTURE_cmdHandler(U32 opCode, U32 cmdSeq, const Fw::CmdStringArg &destination) override;
        void STOP_cmdHandler(U32 opCode, U32 cmdSeq) override;
        void START_cmdHandler(U32 opCode, U32 cmdSeq) override;

        CamBuffer* get_buffer();

        static void streaming_thread_entry(void* this_);
        void streaming_thread();

    PRIVATE:
        std::mutex m_buffer_mutex;
        CamBuffer m_buffers[CAMERA_BUFFER_N];

        LibcameraApp* m_camera;
        Os::Task m_task;

        U32 tlm_dropped;
        U32 tlm_captured;
    };
}

#endif //WERFEN_CAM_HPP