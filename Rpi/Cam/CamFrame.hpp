#ifndef WERFEN_CAMFRAME_HPP
#define WERFEN_CAMFRAME_HPP

#include <Rpi/Cam/CamFrameBaseSerializableAc.hpp>
#include "core/stream_info.hpp"

namespace Rpi
{
    class CamFrame : public CamFrameBase
    {
    public:
        CamFrame(): CamFrameBase() {} //!< Default constructor
        CamFrame(const CamFrameBase& src): CamFrameBase(src){} //!< reference copy constructor

        U8* getData() const;
        void getData(const U8* data);

        StreamInfo getInfo() const;
        void setInfo(const StreamInfo& info);

    private:
        U64 getdata() const; //!< get member data
        void setdata(U64 val); //!< set member data
    };
}

#endif //WERFEN_CAMFRAME_HPP
