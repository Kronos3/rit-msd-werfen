
#include "Cam.hpp"
#include <core/libcamera_app.h>

namespace Rpi
{

    Cam::Cam(const char* compName)
            : CamComponentBase(compName),
              m_camera(new LibcameraApp()),
              tlm_dropped(0),
              tlm_captured(0)
    {
    }

    void Cam::init(NATIVE_INT_TYPE instance)
    {
        CamComponentBase::init(instance);
    }

    void Cam::configure(I32 width, I32 height, I32 rotation, bool vflip, bool hflip)
    {
        for (auto& buffer : m_buffers)
        {
            buffer.register_callback([this](CompletedRequest* cr) { m_camera->queueRequest(cr); });
        }

        m_camera->OpenCamera(0);
        m_camera->ConfigureCameraStream(width, height, rotation,
                                        hflip, vflip);
    }



    Cam::~Cam()
    {
        delete m_camera;
    }

    void Cam::streaming_thread()
    {
        while (true)
        {
            LibcameraApp::Msg msg = m_camera->Wait();
            if (msg.type == LibcameraApp::MsgType::Quit)
            {
                break;
            }

            FW_ASSERT(msg.type == LibcameraApp::MsgType::RequestComplete, (I32)msg.type);

            tlm_captured++;
            tlmWrite_FramesCapture(tlm_captured);

            // Get an internal frame buffer
            CamBuffer* buffer = get_buffer();
            if (!buffer)
            {
                // Ran out of frame buffers
                tlm_dropped++;
                tlmWrite_FramesDropped(tlm_dropped);
                m_camera->queueRequest(msg.payload);
                continue;
            }

            buffer->request = msg.payload;

            // Get the DMA buffer
            buffer->buffer = msg.payload->buffers[m_camera->RawStream()];
            FW_ASSERT(buffer->buffer);

            // Get the userland pointer
            buffer->span = m_camera->Mmap(buffer->buffer)[0];
            buffer->info = m_camera->GetStreamInfo(m_camera->RawStream());

            // Send the frame to the requester on the same port
            frame_out(0, buffer->id);
        }

        log_ACTIVITY_LO_CameraStopping();
        m_camera->StopCamera();
    }

    CamBuffer* Cam::get_buffer()
    {
        m_buffer_mutex.lock();
        for (auto &buf : m_buffers)
        {
            if (!buf.in_use())
            {
                buf.incref();
                m_buffer_mutex.unlock();
                return &buf;
            }
        }

        m_buffer_mutex.unlock();
        return nullptr;
    }

    void Cam::CAPTURE_cmdHandler(U32 opCode, U32 cmdSeq, const Fw::CmdStringArg &destination)
    {
        // Capture an image and save it to a file
        cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);
    }

    void Cam::get_config(CameraConfig &config)
    {
        Fw::ParamValid valid;

#define GET_PARAM(type, pname, vname) \
        do { \
            auto temp = static_cast<type>(paramGet_##pname(valid)); \
            if (valid == Fw::ParamValid::VALID) \
            { \
                config.vname = temp; \
            } \
        } while(0)
#define GET_PARAM_ENUM(type, pname, vname) \
        do { \
            auto temp = paramGet_##pname(valid); \
            if (valid == Fw::ParamValid::VALID) \
            { \
                config.vname = static_cast<type>(temp.e); \
            } \
        } while(0)

        GET_PARAM(U32, FRAME_RATE, frame_rate);
        GET_PARAM(U32, EXPOSURE_TIME, exposure_time);
        GET_PARAM(F32, GAIN, gain);
        GET_PARAM_ENUM(CameraConfig::AeMeteringModeEnum, METERING_MODE, metering_mode);
        GET_PARAM_ENUM(CameraConfig::AeExposureModeEnum, EXPOSURE_MODE, exposure_mode);
        GET_PARAM_ENUM(CameraConfig::AwbModeEnum, AWB, awb);
        GET_PARAM(F32, EV, ev);
        GET_PARAM(F32, AWB_GAIN_R, awb_gain_r);
        GET_PARAM(F32, AWB_GAIN_B, awb_gain_b);
        GET_PARAM(F32, BRIGHTNESS, brightness);
        GET_PARAM(F32, CONTRAST, contrast);
        GET_PARAM(F32, SATURATION, saturation);
        GET_PARAM(F32, SHARPNESS, sharpness);
    }

    void
    Cam::startStreamThread(const Fw::StringBase &name)
    {
        m_task.start(name, streaming_thread_entry, this);
    }

    void Cam::streaming_thread_entry(void* this_)
    {
        reinterpret_cast<Cam*>(this_)->streaming_thread();
    }

    void Cam::quitStreamThread()
    {
        // Wait for the camera to exit
        m_camera->Quit();
        m_task.join(nullptr);

        m_camera->StopCamera();
    }

    void Cam::STOP_cmdHandler(U32 opCode, U32 cmdSeq)
    {
        log_ACTIVITY_LO_CameraStopping();
        m_camera->StopCamera();
        cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);
    }

    void Cam::START_cmdHandler(U32 opCode, U32 cmdSeq)
    {
        m_camera->StopCamera();

        CameraConfig config;
        get_config(config);
        log_ACTIVITY_LO_CameraConfiguring();
        m_camera->ConfigureCamera(config);

        log_ACTIVITY_LO_CameraStarting();
        m_camera->StartCamera();
        cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);
    }

    void Cam::parametersLoaded()
    {
        CamComponentBase::parametersLoaded();

        CameraConfig config;
        get_config(config);
        log_ACTIVITY_LO_CameraConfiguring();
        m_camera->ConfigureCamera(config);

    }

    bool Cam::frameGet_handler(NATIVE_INT_TYPE portNum, U32 frameId, CamFrame &frame)
    {
        FW_ASSERT(frameId < CAMERA_BUFFER_N, frameId);
        const auto& buf = m_buffers[frameId];

        if (!buf.in_use())
        {
            log_WARNING_LO_CameraInvalidGet(frameId);
            return false;
        }

        frame = CamFrame(
                buf.id, buf.span.data(),
                buf.span.size(),
                buf.info.width, buf.info.height,
                buf.info.stride,
                buf.buffer->metadata().timestamp / 1000,
                buf.buffer->planes()[0].fd.get()
                );

        return true;
    }

    void Cam::incref_handler(NATIVE_INT_TYPE portNum, U32 frameId)
    {
        FW_ASSERT(frameId < CAMERA_BUFFER_N, frameId);

        auto& buf = m_buffers[frameId];
        if (!buf.in_use())
        {
            log_WARNING_LO_CameraInvalidIncref(frameId);
            return;
        }

        buf.incref();
    }

    void Cam::decref_handler(NATIVE_INT_TYPE portNum, U32 frameId)
    {
        FW_ASSERT(frameId < CAMERA_BUFFER_N, frameId);

        auto& buf = m_buffers[frameId];
        if (!buf.in_use())
        {
            log_WARNING_LO_CameraInvalidDecref(frameId);
            return;
        }

        buf.decref();
    }
}
