import { useCallback, useEffect, useState } from 'react';

import {
    HStack,
    Heading,
    Input,
    Text,
    Button,
    Select,
    VStack,
    IconButton,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalCloseButton,
    ModalBody,
    ModalFooter,
    useDisclosure
} from '@chakra-ui/react';
import { MdRefresh, MdEject, MdSettings } from "react-icons/md";

import { UsbDrive } from './api';
import * as cookies from './cookie';


export default function Usb(props: { host: string, usb: string, setUsb: (usb: string) => void }) {
    const [usbDrives, setUsbDrives] = useState<UsbDrive[]>([]);
    const [isDisabled, setDisabled] = useState<boolean>(false);

    const { isOpen, onOpen, onClose } = useDisclosure();

    const [mountPointFilter, setMountPointFilter] = useState<string>(cookies.get("mountPointFilter") || "/media");
    const [filesystemTypeFilter, setFilesystemTypeFilter] = useState<string>(cookies.get("filesystemTypeFilter") || "vfat");

    useEffect(() => {
        cookies.set("mountPointFilter", mountPointFilter)
    }, [mountPointFilter]);

    useEffect(() => {
        cookies.set("filesystemTypeFilter", filesystemTypeFilter)
    }, [filesystemTypeFilter]);


    const refreshUsb = useCallback(() => {
        setDisabled(true);

        (async () => {
            const responseRaw = await fetch(`http://${props.host}/linux/mounts?mount_point_filter=${mountPointFilter}&fs_type_filter=${filesystemTypeFilter}`,
                { method: "POST" }
            );

            const response = await responseRaw.json() as UsbDrive[];
            if (!props.usb && response.length > 0) {
                props.setUsb(response[0].mountpoint);
            }

            setUsbDrives(response);
            setDisabled(false);
        })();
    }, [props.host, props.usb, isDisabled, props.setUsb, mountPointFilter, filesystemTypeFilter]);

    const unmount = useCallback(() => {
        setDisabled(true);

        (async () => {
            await fetch(`http://${props.host}/linux/unmount?mountpoint=${props.usb}`,
                { method: "POST" }
            );

            refreshUsb();
        })();
    }, [props.host, props.usb]);

    useEffect(() => {
        refreshUsb();
    }, []);

    return (
        <>
            <Modal isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>USB Device Search Parameters</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Heading as='h4' size='md'>Mountpoint Filter</Heading>
                        <Text>Where USB devices will automount to, use '/' for all device mounts</Text>
                        <Input value={mountPointFilter} onChange={(e) => setMountPointFilter(e.target.value)}></Input>

                        <Heading style={{ paddingTop: 10 }} as='h4' size='md'>Filesystem Type Filter</Heading>
                        <Text>Filesystems to show in the USB dropdown, 'vfat' is recommended</Text>
                        <Input value={filesystemTypeFilter} onChange={(e) => setFilesystemTypeFilter(e.target.value)}></Input>
                    </ModalBody>

                    <ModalFooter>
                        <Button colorScheme='blue' mr={3} onClick={onClose}>
                            Close
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
            <VStack>
                <HStack>
                    <Text>USB Drives</Text>
                    <IconButton
                        disabled={isDisabled}
                        onClick={onOpen}
                        aria-label='Settings'
                        fontSize='20px'
                        icon={<MdSettings />}
                    />
                    <IconButton
                        disabled={isDisabled}
                        onClick={refreshUsb}
                        aria-label='Refresh'
                        fontSize='20px'
                        icon={<MdRefresh />}
                    />
                </HStack>
                {
                    usbDrives.length > 0 ? (
                        <HStack>
                            <Select
                                disabled={isDisabled}
                                value={props.usb}
                                onChange={(e) => props.setUsb(e.target.value)}
                            >
                                {
                                    usbDrives.map(v => <option value={v.mountpoint}>{v.mountpoint} ({v.device})</option>)
                                }
                            </Select>
                            {
                                <IconButton
                                    disabled={isDisabled}
                                    onClick={unmount}
                                    aria-label='Unmount'
                                    fontSize='20px'
                                    icon={<MdEject />}
                                />
                            }
                        </HStack>
                    ) : <Text>No USB Drives Found</Text>
                }
            </VStack>
        </>
    );
}
