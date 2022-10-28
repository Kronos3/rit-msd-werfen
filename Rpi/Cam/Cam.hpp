
#ifndef WERFEN_CAM_HPP
#define WERFEN_CAM_HPP

#include <Rpi/Cam/CamComponentAc.hpp>
#include <Rpi/Cam/CamCfg.h>
#include <Rpi/Cam/CameraConfig.hpp>
#include <Rpi/Cam/CamBuffer.hpp>

#include <queue>
#include <mutex>

namespace Rpi
{
    struct CamImpl;
    class Cam : public CamComponentBase
    {
    public:
        explicit Cam(const char* compName);
        ~Cam() override;

        void init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance);

    PRIVATE:
        enum CamState
        {
            IDLE,
            STREAM,
            CAPTURE,
            QUIT
        };

        static void streaming_thread_entry(void* this_);
        void send_message(CamState msg);

        void capture_frame();
        void streaming_thread();

        void preamble() override;
        void finalizer() override;

        void parametersLoaded() override;

        void get_config(CameraConfig& config);
        void configure(const CameraConfig& config);
        bool frameGet_handler(NATIVE_INT_TYPE portNum, U32 frameId, Rpi::CamFrame &frame) override;
        void incref_handler(NATIVE_INT_TYPE portNum, U32 frameId) override;
        void decref_handler(NATIVE_INT_TYPE portNum, U32 frameId) override;

        void start_handler(NATIVE_INT_TYPE portNum) override;
        void stop_handler(NATIVE_INT_TYPE portNum) override;
        void capture_handler(NATIVE_INT_TYPE portNum) override;

        CamBuffer* get_buffer();

    PRIVATE:

        I32 m_cam_id;

        std::mutex m_buffer_mutex;
        CamBuffer m_buffers[CAMERA_BUFFER_N];

        CamImpl* m_camera;

        Os::Queue m_queue;

        bool m_streaming;
        I32 m_listener;

        Os::Task m_task;

        U32 tlm_dropped;
        U32 tlm_captured;
        U32 tlm_failed;
    };
}

#endif //WERFEN_CAM_HPP
