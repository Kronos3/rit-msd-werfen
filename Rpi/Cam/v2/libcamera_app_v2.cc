
#include "libcamera_app_v2.h"
#include <Rpi/Cam/Cam.hpp>

namespace Rpi
{
    LibCamera::LibCamera(Cam* cam_)
    : cam(cam_), acquired(false)
    {
    }

    bool LibCamera::open(U32 camera_index)
    {
        camera_manager = std::make_unique<CameraManager>();
        int ret = camera_manager->start();
        if (ret)
        {
            cam->log_WARNING_HI_CameraManagerStartFailed(-ret);
            return false;
        }

        if (camera_manager->cameras().empty())
        {
            cam->log_WARNING_HI_NoCameras();
            return false;
        }

        if (camera_index >= camera_manager->cameras().size())
        {
            cam->log_WARNING_HI_CameraOutOfRange(camera_index, camera_manager->cameras().size());
            return false;
        }

        // Find the camera name at index
        std::string const &cam_id = camera_manager->cameras()[camera_index]->id();
        cam->log_DIAGNOSTIC_CameraName(camera_index, cam_id.c_str());

        // Get the camera object from the manager
        camera = camera_manager->get(cam_id);
        if (!camera)
        {
            cam->log_WARNING_HI_CameraFindFailed(cam_id.c_str());
            return false;
        }

        if (camera->acquire())
        {
            cam->log_WARNING_HI_CameraAcquireFailed(cam_id.c_str());
            return false;
        }

        cam->log_ACTIVITY_LO_CameraOpened(cam_id.c_str());

        acquired = true;
        return true;
    }

    void LibCamera::close()
    {
        if (acquired)
        {
            camera->release();
        }

        acquired = false;
        camera.reset();
        camera_manager.reset();
    }

    bool LibCamera::configureStreams(I32 width, I32 height, I32 rotation, bool hflip, bool vflip)
    {
        StreamRoles stream_roles = {
                StreamRole::VideoRecording,
                StreamRole::StillCapture,
        };

        configuration = camera->generateConfiguration(stream_roles);

        if (!configuration)
        {
            cam->log_WARNING_HI_CameraConfigInitFailed(cameraId());
            return false;
        }

        // Make sure we know the number of stream we have
        FW_ASSERT(configuration->size() == STREAM_N);

        configuration->transform = libcamera::Transform::Identity;
        if (rotation == 180)
            configuration->transform = libcamera::Transform::Rot180 * configuration->transform;
        if (hflip)
            configuration->transform = libcamera::Transform::HFlip * configuration->transform;
        if (vflip)
            configuration->transform = libcamera::Transform::VFlip * configuration->transform;

        configuration->at(VIDEO).bufferCount = CAMERA_BUFFER_N;
        configuration->at(CAPTURE).bufferCount = 1;

        // Validate configuration and configure the camera
        CameraConfiguration::Status validation = configuration->validate();
        switch (validation)
        {
            case CameraConfiguration::Valid:
                cam->log_DIAGNOSTIC_CameraConfigValidation(cameraId(), Cam_ConfigurationValidity::VALID);
                break;
            case CameraConfiguration::Adjusted:
                cam->log_DIAGNOSTIC_CameraConfigValidation(cameraId(), Cam_ConfigurationValidity::ADJUSTED);
                break;
            case CameraConfiguration::Invalid:
                cam->log_DIAGNOSTIC_CameraConfigValidation(cameraId(), Cam_ConfigurationValidity::INVALID);
                return false;
        }

        I32 cfgCode = camera->configure(configuration.get());
        if (cfgCode < 0)
        {
            cam->log_WARNING_HI_CameraConfigFailed(cameraId(), cfgCode);
            return false;
        }

        // Allocate the frame buffers for both streams
        allocator = new FrameBufferAllocator(camera);
        for (I32 streamId = 0; streamId < STREAM_N; streamId++)
        {
            auto stream = configuration->at(streamId);
            stream.stream();
        }

        streams[VIDEO] = std::unique_ptr<Stream>(configuration->at(VIDEO).stream());
        streams[CAPTURE] = std::unique_ptr<Stream>(configuration->at(CAPTURE).stream());

        return true;
    }

    bool LibCamera::configure(const CameraConfig &options)
    {
        controls.clear();

        // Framerate is a bit weird. If it was set programmatically, we go with that, but
        // otherwise it applies only to preview/video modes. For stills capture we set it
        // as long as possible so that we get whatever the exposure profile wants.
        if (!controls.contains(libcamera::controls::FrameDurationLimits))
        {
            if (options.frame_rate > 0)
            {
                int64_t frame_time = 1000000 / options.frame_rate; // in us
                controls.set(libcamera::controls::FrameDurationLimits, {frame_time, frame_time});
            }
        }

        if (options.exposure_time)
            controls.set(libcamera::controls::ExposureTime, options.exposure_time);
        if (options.gain != 0.0)
            controls.set(libcamera::controls::AnalogueGain, options.gain);
        controls.set(libcamera::controls::AeMeteringMode, options.metering_mode);
        controls.set(libcamera::controls::AeExposureMode, options.exposure_mode);
        controls.set(libcamera::controls::ExposureValue, options.ev);
        controls.set(libcamera::controls::AwbMode, options.awb);
        controls.set(libcamera::controls::ColourGains, {options.awb_gain_r, options.awb_gain_b});
        controls.set(libcamera::controls::Brightness, options.brightness);
        controls.set(libcamera::controls::Contrast, options.contrast);
        controls.set(libcamera::controls::Saturation, options.saturation);
        controls.set(libcamera::controls::Sharpness, options.sharpness);

        return true;
    }

    Fw::String LibCamera::cameraId() const
    {
        return camera->id().c_str();
    }

    std::vector<libcamera::Span<uint8_t>> LibCamera::mmap(LibCamera::FrameBuffer* buffer) const
    {
        auto item = mapped_buffers.find(buffer);
        if (item == mapped_buffers.end())
        {
            FW_ASSERT(0 && "Failed to find memmaped memory for DMA");
        }
        return item->second;
    }

    LibCamera::Stream* LibCamera::videoStream() const
    {
        return streams[VIDEO].get();
    }

    LibCamera::Stream* LibCamera::captureStream() const
    {
        return streams[CAPTURE].get();
    }

    void LibCamera::queue(CompletedRequest* cr)
    {
        BufferMap buffers(std::move(cr->buffers));

        Request* request = cr->request;
        delete cr;
        assert(request);

        // This function may run asynchronously so needs protection from the
        // camera stopping at the same time.
//        std::lock_guard<std::mutex> stop_lock(camera_stop_mutex_);
//        if (!camera_started)
//            return;
//
//        // An application could be holding a CompletedRequest while it stops and re-starts
//        // the camera, after which we don't want to queue another request now.
//        {
//            std::lock_guard<std::mutex> lock(completed_requests_mutex_);
//            auto it = completed_requests_.find(completed_request);
//            if (it == completed_requests_.end())
//                return;
//            completed_requests_.erase(it);
//        }

        for (auto const &p: buffers)
        {
            if (request->addBuffer(p.first, p.second) < 0)
                throw std::runtime_error("failed to add buffer to request in QueueRequest");
        }

        {
            std::lock_guard<std::mutex> lock(control_mutex);
            request->controls() = std::move(controls);
        }

        if (camera->queueRequest(request) < 0)
            throw std::runtime_error("failed to queue request");
    }

    LibCamera::Msg LibCamera::wait()
    {
        return msg_queue.wait();
    }
}
