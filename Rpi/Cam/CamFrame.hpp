#ifndef WERFEN_CAMFRAME_HPP
#define WERFEN_CAMFRAME_HPP

#include <Fw/Types/Serializable.hpp>
#include <opencv2/core.hpp>

namespace Rpi
{
    class CamFrame : private Fw::Serializable
    {
    public:
        enum {
            SERIALIZED_SIZE = sizeof(cv::Mat*)
        };

        CamFrame();
        explicit CamFrame(cv::Mat* m);
        Fw::SerializeStatus serialize(Fw::SerializeBufferBase &buffer) const override;
        Fw::SerializeStatus deserialize(Fw::SerializeBufferBase &buffer) override;

        cv::Mat* get() const;

    private:
        cv::Mat* m_mat;
    };
}

#endif //WERFEN_CAMFRAME_HPP
