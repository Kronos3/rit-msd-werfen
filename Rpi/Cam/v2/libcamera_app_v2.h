
#ifndef WERFEN_LIBCAMERA_APP_V2_H
#define WERFEN_LIBCAMERA_APP_V2_H

#include <Fw/Types/String.hpp>

#include <libcamera/base/span.h>
#include <libcamera/camera.h>
#include <libcamera/camera_manager.h>
#include <libcamera/control_ids.h>
#include <libcamera/controls.h>
#include <libcamera/formats.h>
#include <libcamera/framebuffer_allocator.h>
#include <libcamera/property_ids.h>
#include <queue>
#include <mutex>
#include <condition_variable>
#include "CameraConfig.hpp"

namespace Rpi
{
    struct CompletedRequest
    {
        using BufferMap = libcamera::Request::BufferMap;
        using ControlList = libcamera::ControlList;
        using Request = libcamera::Request;

        CompletedRequest(unsigned int seq, Request *r)
                : sequence(seq), buffers(r->buffers()), metadata(r->metadata()), request(r), framerate(0.0)
        {
            r->reuse();
        }
        unsigned int sequence;
        BufferMap buffers;
        ControlList metadata;
        Request *request;
        float framerate;
        //	Metadata post_process_metadata;
    };

    struct StreamInfo
    {
        StreamInfo() : width(0), height(0), stride(0) {}
        unsigned int width;
        unsigned int height;
        unsigned int stride;
        libcamera::PixelFormat pixel_format;
        std::optional<libcamera::ColorSpace> colour_space;
    };

    class Cam;
    struct LibCamera
    {
        enum StreamId
        {
            VIDEO,
            CAPTURE,
            STREAM_N
        };

        using Stream = libcamera::Stream;
        using FrameBuffer = libcamera::FrameBuffer;
        using ControlList = libcamera::ControlList;
        using Request = libcamera::Request;
        using CameraManager = libcamera::CameraManager;
        using Camera = libcamera::Camera;
        using CameraConfiguration = libcamera::CameraConfiguration;
        using FrameBufferAllocator = libcamera::FrameBufferAllocator;
        using StreamRole = libcamera::StreamRole;
        using StreamRoles = libcamera::StreamRoles;
        using PixelFormat = libcamera::PixelFormat;
        using StreamConfiguration = libcamera::StreamConfiguration;
        using BufferMap = Request::BufferMap;
        using Size = libcamera::Size;
        using Rectangle = libcamera::Rectangle;

        enum class MsgType
        {
            REQUEST_COMPLETE,
            QUIT
        };

        struct Msg
        {
            explicit Msg(MsgType const &t) : type(t), payload(nullptr)
            {}

            template<typename T>
            Msg(MsgType const &t, T p) : type(t), payload(std::forward<T>(p))
            {
            }

            MsgType type;
            CompletedRequest* payload;
        };

        explicit LibCamera(Cam* cam);

        /**
         * Camera ID according to the kernel
         * @return cam id
         */
        Fw::String cameraId() const;

        /**
         * Open camera with index
         * @param camera index of camera /dev/video[N]
         */
        bool open(U32 camera);

        /**
         * Release the video device
         */
        void close();

        /**
         * Configure two streams:
         *    VIDEO   (continuous stream)
         *    CAPTURE (single capture)
         * @param width width in pixels
         * @param height height in pixels
         * @param rotation frame rotation: -90, 0, 90, 180
         * @param hflip horizontal flip
         * @param vflip vertical flip
         */
        bool configureStreams(I32 width, I32 height, I32 rotation, bool hflip, bool vflip);
        bool configure(const CameraConfig& options);

        std::vector<libcamera::Span<uint8_t>> mmap(FrameBuffer* buffer) const;

        Stream* videoStream() const;
        Stream* captureStream() const;

        void queue(CompletedRequest* cr);

        Msg wait();

        void start();
        void stop();
        void capture();

        static StreamInfo streamInfo(Stream* stream);
    private:

        template<typename T>
        class MessageQueue
        {
        public:
            template<typename U>
            void post(U &&msg)
            {
                std::unique_lock<std::mutex> lock(mutex_);
                queue_.push(std::forward<U>(msg));
                cond_.notify_one();
            }

            T wait()
            {
                std::unique_lock<std::mutex> lock(mutex_);
                cond_.wait(lock, [this]
                { return !queue_.empty(); });
                T msg = std::move(queue_.front());
                queue_.pop();
                return msg;
            }

            void clear()
            {
                std::unique_lock<std::mutex> lock(mutex_);
                queue_ = {};
            }

        private:
            std::queue<T> queue_;
            std::mutex mutex_;
            std::condition_variable cond_;
        };

        std::unique_ptr<CameraManager> camera_manager;
        std::shared_ptr<Camera> camera;

        std::unique_ptr<CameraConfiguration> configuration;

        std::unique_ptr<Stream> streams[STREAM_N];
        std::queue<FrameBuffer*> frame_buffers[STREAM_N];

        MessageQueue<Msg> msg_queue;

        std::mutex control_mutex;
        ControlList controls;

        // Keeps track of memory we need to unmap during teardown
        std::map<FrameBuffer*, std::vector<libcamera::Span<uint8_t>>> mapped_buffers;

        FrameBufferAllocator* allocator;

        bool acquired;

        Cam* cam;
    };
}

#endif //WERFEN_LIBCAMERA_APP_V2_H
