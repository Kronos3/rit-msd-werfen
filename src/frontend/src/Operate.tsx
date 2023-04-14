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

import { useCallback, useEffect, useState } from 'react';

import { StageStatus, UsbDrive } from './api';
import * as cookies from './cookie';
import { generateQuery } from './Form';
import SettingsForm from './SettingsForm';
import { MdSettings } from 'react-icons/md';

function OperateCalibrated(props: { host: string }) {
    return (
        <>
        </>
    )
}

function OperateUncalibrated(props: { host: string, schema: any }) {
    const [isDisabled, setDisabled] = useState<boolean>(false);
    const { isOpen, onOpen, onClose } = useDisclosure();

    const alignmentParams = cookies.get("alignmentParams")
    console.log(alignmentParams);
    const [settings, setSettings] = useState(alignmentParams ? JSON.parse(alignmentParams) : undefined);

    useEffect(() => {
        if (settings) {
            cookies.set("alignmentParams", JSON.stringify(settings));
        }
    }, [settings]);

    const onAlign = useCallback(() => {
        setDisabled(true);
        (async () => {
            const query = generateQuery(settings);
            await fetch(`http://${props.host}/system/align?${query}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });

            setDisabled(false);
        })();
    }, [settings]);

    return (
        <VStack align="stretch">
            <Modal isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Alignment Parameters</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <SettingsForm value={settings} setValue={setSettings} path="/system/align" schema={props.schema} />
                    </ModalBody>

                    <ModalFooter>
                        <Button colorScheme='blue' mr={3} onClick={onClose}>
                            Close
                        </Button>
                    </ModalFooter>
                </ModalContent>
            </Modal>
            <HStack>
                <Text>Stage must be aligned before continuing</Text>
                <IconButton
                    disabled={isDisabled}
                    onClick={onOpen}
                    aria-label='Settings'
                    fontSize='20px'
                    icon={<MdSettings />}
                />
            </HStack>
            <Button
                disabled={isDisabled}
                onClick={onAlign}
                colorScheme='blue'
            >
                Align
            </Button>
        </VStack>
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
