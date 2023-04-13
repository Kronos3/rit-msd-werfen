import {
    HStack,
    Text,
    Button,
    Select,
    VStack
} from '@chakra-ui/react'
import { useCallback, useEffect, useState } from 'react'

import { StageStatus, UsbDrive } from './api';
import ApiForm from './Form';


function Usb(props: { host: string, usbSelect?: string, setUsbSelect: (usb: string) => void }) {
    const [usbDrives, setUsbDrives] = useState<UsbDrive[]>([]);

    const refreshUsb = useCallback(() => {
        (async () => {
            const responseRaw = await fetch(`http://${props.host}/linux/mounts?mount_point_filter=/media&fs_type_filter=vfat`,
                { method: "POST" }
            );

            const response = await responseRaw.json() as UsbDrive[];
            if (!props.usbSelect && response.length > 0) {
                props.setUsbSelect(response[0].mountpoint);
            }

            setUsbDrives(response);
        })();
    }, [props.host, props.usbSelect, props.setUsbSelect]);

    const unmount = useCallback(() => {
        (async () => {
            await fetch(`http://${props.host}/linux/unmount?mountpoint=${props.usbSelect}`,
                { method: "POST" }
            );

            refreshUsb();
        })();
    }, [props.host, props.usbSelect]);

    useEffect(() => {
        refreshUsb();
    }, []);

    return (
        <VStack>
            <Text>USB Drives</Text>
            <HStack>
                <Select value={props.usbSelect} onChange={(e) => props.setUsbSelect(e.target.value)}>
                    {
                        usbDrives.map(v => <option value={v.mountpoint}>{v.mountpoint} ({v.device})</option>)
                    }
                </Select>
                <Button onClick={refreshUsb}>Refresh</Button>
                <Button onClick={unmount}>Unmount</Button>
            </HStack>
        </VStack>
    );
}

const AlignmentDefaults = {

}

function OperateCalibrated(props: { host: string }) {
    const [usb, setUsb] = useState<string>();

    return (
        <>
            <Usb usbSelect={usb} setUsbSelect={setUsb} host={props.host} />
        </>
    )
}

function OperateUncalibrated(props: { host: string, schema: any }) {


    return (
        <>
            <Text>Stage must be aligned before continuing</Text>
            <ApiForm path="/system/align" host={props.host} schema={props.schema} onReply={() => {}} />
        </>
    )
}

export default function Operate(props: { status: StageStatus, host: string, schema: any }) {
    return <>
        {
            props.status.calibrated ?
                <OperateCalibrated host={props.host} />
                : <OperateUncalibrated host={props.host} schema={props.schema} />
        }
    </>
}
