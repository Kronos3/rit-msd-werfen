import {
    Text,
    Button,
    VStack,
    useToast,
} from '@chakra-ui/react';

import { useCallback, useState } from 'react';
import { SystemStatus } from './api';

export default function Focus(props: { status: SystemStatus, host: string }) {
    const toast = useToast();

    const [isDisabled, setDisabled] = useState(false);

    const onStart = useCallback((cam: string) => {
        setDisabled(true);

        fetch(`http://${props.host}/cam/preview/start/${cam}`)
            .then(() => {
                toast({
                    status: "success",
                    title: `Started ${cam} camera`,
                    duration: 1000
                })
            })
            .catch((err) => {
                toast({
                    status: "error",
                    title: `Failed to start ${cam} camera`,
                    description: `${err}`
                });
            })
            .finally(() => setDisabled(false));
    }, [props.host]);

    const onStop = useCallback((cam: string) => {
        setDisabled(true);
        fetch(`http://${props.host}/cam/preview/stop/${cam}`)
            .then(() => {
                toast({
                    status: "success",
                    title: `Stopped ${cam} camera`,
                    duration: 1000
                })
            })
            .catch((err) => {
                toast({
                    status: "error",
                    title: `Failed to stop ${cam} camera`,
                    description: `${err}`
                });
            })
            .finally(() => setDisabled(false));
    }, [props.host]);

    const onAuxToggle = useCallback(() => {
        if (props.status.aux_preview) {
            onStop("aux");
        } else {
            onStart("aux");
        }
    }, [props.status, onStart]);

    const onHqToggle = useCallback(() => {
        if (props.status.hq_preview) {
            onStop("hq");
        } else {
            onStart("hq");
        }
    }, [props.status, onStart]);

    return (
        <VStack align="stretch">
            <Text>
                Toggle preview window for live camera feed.
                Window will open on the local Raspberry Pi display.
                (A screen must be plugged into the Raspberry Pi).
            </Text>
            <Text>
                Use the live feed on the display to focus the lens on either
                the HQ Camera (high zoom, sensor imager), or the auxilliary
                camera (images the card IDs).
            </Text>
            <Button isDisabled={isDisabled} onClick={onAuxToggle}>{props.status.aux_preview ? "Stop" : "Start"} Aux</Button>
            <Button isDisabled={isDisabled} onClick={onHqToggle}>{props.status.hq_preview ? "Stop" : "Start"} HQ</Button>
        </VStack>
    )
}
