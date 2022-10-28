
#include "Cam.hpp"

#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>

namespace Rpi
{
    struct CamImpl
    {
        cv::VideoCapture cam;
    };

    Cam::Cam(const char* compName)
            : CamComponentBase(compName),
              m_cam_id(0),
              m_camera(new CamImpl),
              m_streaming(false),
              m_listener(-1),
              tlm_dropped(0),
              tlm_captured(0),
              tlm_failed(0)
    {
        U32 id = 0;
        for (auto& iter : m_buffers)
        {
            iter.id = id++;
        }
    }

    void Cam::init(NATIVE_INT_TYPE queueDepth, NATIVE_INT_TYPE instance)
    {
        CamComponentBase::init(queueDepth, instance);

        Os::QueueString s("CAM-Q");
        m_queue.create(s, 10, sizeof(CamState));
    }

    Cam::~Cam()
    {
        delete m_camera;
    }

    void Cam::streaming_thread()
    {
        CamState state = IDLE;
        Os::Queue::QueueBlocking blocking = Os::Queue::QUEUE_BLOCKING;

        U8 buf_prv[sizeof(CamState)];
        Fw::ExternalSerializeBuffer buf(buf_prv, sizeof(CamState));

        NATIVE_INT_TYPE priority;

        while (true)
        {
            // Wait for a change of state message
            buf.resetSer();
            Os::Queue::QueueStatus status = m_queue.receive(
                    buf, priority, blocking);

            if (Os::Queue::QUEUE_BLOCKING == blocking)
            {
                // Make sure we actually got a message from the queue
                FW_ASSERT(Os::Queue::QUEUE_OK == status, status);
            }
            else
            {
                FW_ASSERT(Os::Queue::QUEUE_OK == status ||
                          Os::Queue::QUEUE_NO_MORE_MSGS == status, status);
            }

            if (Os::Queue::QUEUE_OK == status)
            {
                // Read the message and set the state based on this state
                U32 c_state;
                buf.deserialize(c_state);
                state = static_cast<CamState>(c_state);
            }

            switch(state)
            {
                case IDLE:
                    // Empty cycle, wait for another message
                    blocking = Os::Queue::QUEUE_BLOCKING;
                    break;
                case STREAM:
                    // Continuously stream the frames
                    blocking = Os::Queue::QUEUE_NONBLOCKING;
                    capture_frame();
                    break;
                case CAPTURE:
                    // Capture a single image, then wait for more msgs
                    blocking = Os::Queue::QUEUE_BLOCKING;
                    capture_frame();
                    state = IDLE;
                    break;
                case QUIT:
                    return;
                default:
                    FW_ASSERT(0, state);
            }
        }
    }

    CamBuffer* Cam::get_buffer()
    {
        m_buffer_mutex.lock();
        for (auto &buf: m_buffers)
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

        GET_PARAM(U32, FRAME_RATE, frame_rate);
        GET_PARAM(U32, EXPOSURE_TIME, exposure_time);
        GET_PARAM(F32, GAIN, gain);
        GET_PARAM(F32, AWB_GAIN_R, awb_gain_r);
        GET_PARAM(F32, AWB_GAIN_B, awb_gain_b);
        GET_PARAM(F32, BRIGHTNESS, brightness);
        GET_PARAM(F32, CONTRAST, contrast);
        GET_PARAM(F32, SATURATION, saturation);
        GET_PARAM(F32, SHARPNESS, sharpness);
    }

    void Cam::streaming_thread_entry(void* this_)
    {
        reinterpret_cast<Cam*>(this_)->streaming_thread();
    }

    void Cam::configure(const CameraConfig &config)
    {
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_FPS, config.frame_rate);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_EXPOSURE, config.exposure_time);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_GAIN, config.gain);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_WHITE_BALANCE_RED_V, config.awb_gain_r);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_WHITE_BALANCE_BLUE_U, config.awb_gain_b);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_BRIGHTNESS, config.brightness);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_CONTRAST, config.contrast);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_SATURATION, config.saturation);
        m_camera->cam.set(cv::VideoCaptureProperties::CAP_PROP_SHARPNESS, config.sharpness);
    }

    void Cam::parametersLoaded()
    {
        CamComponentBase::parametersLoaded();

        CameraConfig config;
        get_config(config);
        log_ACTIVITY_LO_CameraConfiguring();

        configure(config);
    }

    bool Cam::frameGet_handler(NATIVE_INT_TYPE portNum, U32 frameId, CamFrame &frame)
    {
        FW_ASSERT(frameId < CAMERA_BUFFER_N, frameId);
        auto &buf = m_buffers[frameId];

        if (!buf.in_use())
        {
            log_WARNING_LO_CameraInvalidGet(frameId);
            return false;
        }

        frame = CamFrame(&buf.mat);

        return true;
    }

    void Cam::incref_handler(NATIVE_INT_TYPE portNum, U32 frameId)
    {
        FW_ASSERT(frameId < CAMERA_BUFFER_N, frameId);

        auto &buf = m_buffers[frameId];
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

        auto &buf = m_buffers[frameId];
        if (!buf.in_use())
        {
            log_WARNING_LO_CameraInvalidDecref(frameId);
            return;
        }

        buf.decref();
    }

    void Cam::preamble()
    {
        ActiveComponentBase::preamble();

        m_camera->cam.open(m_cam_id);

        Fw::String task_name = "CAM_STREAM";
        m_task.start(task_name, streaming_thread_entry, this);
    }

    void Cam::finalizer()
    {
        ActiveComponentBase::finalizer();

        send_message(QUIT);

        // Wait for the camera to exit
        m_task.join(nullptr);
        m_camera->cam.release();
    }

    void Cam::start_handler(NATIVE_INT_TYPE portNum)
    {
        if (m_streaming)
        {
            log_WARNING_LO_CameraBusy();
            return;
        }

        CameraConfig config;
        get_config(config);
        log_ACTIVITY_LO_CameraConfiguring();
        configure(config);

        // Frame will be coming from the continuous stream
        m_listener = portNum;
        m_streaming = true;

        log_ACTIVITY_LO_CameraStarting();
        send_message(STREAM);
    }

    void Cam::stop_handler(NATIVE_INT_TYPE portNum)
    {
        log_ACTIVITY_LO_CameraStopping();

        // Single frame requests can come in now
        m_listener = -1;
        m_streaming = false;
        send_message(IDLE);
    }

    void Cam::capture_handler(NATIVE_INT_TYPE portNum)
    {
        if (m_streaming)
        {
            log_WARNING_LO_CameraBusy();
            return;
        }

        m_streaming = false;
        m_listener = portNum;
        send_message(CAPTURE);
    }

    void Cam::capture_frame()
    {
        CamBuffer* buffer = get_buffer();
        if (!buffer)
        {
            // Ran out of frame buffers
            tlm_dropped++;
            tlmWrite_FramesDropped(tlm_dropped);
            return;
        }

        // Read an image from the camera
        if (m_camera->cam.read(buffer->mat))
        {
            tlm_captured++;
            tlmWrite_FramesCapture(tlm_captured);

            if (m_listener < 0)
            {
                log_WARNING_LO_CameraNoListener(buffer->id);
                return;
            }

            frame_out(m_listener, buffer->id);
        }
        else
        {
            tlm_failed++;
            tlmWrite_FramesFailed(tlm_failed);

            // Put us in idle since we might get an overflow here
            // TODO(tumbar) Do we want this?
            send_message(IDLE);
        }
    }

    void Cam::send_message(Cam::CamState msg)
    {
        U8 buf_prv[sizeof(CamState)];
        Fw::ExternalSerializeBuffer buf(buf_prv, sizeof(CamState));

        buf.serialize(msg);
        m_queue.send(buf, 0, Os::Queue::QUEUE_BLOCKING);
    }
}
