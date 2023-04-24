import {
    Text,
    Button,
    VStack,
    useToast,
    HStack,
    IconButton,
    NumberInput,
    NumberInputField,
    NumberInputStepper,
    NumberIncrementStepper,
    NumberDecrementStepper,
    Select,
} from '@chakra-ui/react';

import { useCallback, useState } from 'react';
import { SystemStatus } from './api';
import { MdEast, MdLightbulbOutline, MdWest } from 'react-icons/md';
import { generateQuery } from './Form';

// eslint-disable-next-line @typescript-eslint/naming-convention
function Relative(props: { host: string, status: SystemStatus, isDisabled: boolean }) {
    const [steps, setSteps] = useState<number>(300);
    const [size, setSize] = useState<string>("QUARTER");

    const toast = useToast();

    const onLeft = useCallback(() => {
        fetch(`http://${props.host}/stage/relative?${generateQuery({
            n: steps,
            size: size
        })}`, { method: "POST" })
            .then(async (r) => {
                if (r.ok) {
                    return await r.text();
                } else {
                    throw new Error(await r.text());
                }
            })
            .catch((err) => {
                toast({
                    status: "error",
                    title: "Failed to move left",
                    description: `${err}`
                });
            });
    }, [props.host, steps, size]);

    const onRight = useCallback(() => {
        fetch(`http://${props.host}/stage/relative?${generateQuery({
            n: -steps,
            size: size
        })}`, { method: "POST" })
            .then(async (r) => {
                if (r.ok) {
                    return await r.text();
                } else {
                    throw new Error(await r.text());
                }
            })
            .catch((err) => {
                toast({
                    status: "error",
                    title: "Failed to move right",
                    description: `${err}`
                });
            });
    }, [props.host, steps, size]);

    const onLight = useCallback(() => {
        if (props.status.led) {
            fetch(`http://${props.host}/stage/led_pwm?pwm=0`, { method: "POST" });
        } else {
            fetch(`http://${props.host}/stage/led_pwm?pwm=0.2`, { method: "POST" });
        }
    }, [props.host, props.status]);

    return (
        <HStack alignSelf="center">
            <IconButton
                isDisabled={props.isDisabled}
                onClick={onLeft}
                aria-label='Left'
                fontSize='20px'
                icon={<MdWest />}
            />
            <NumberInput step={10} value={steps} width={200} onChange={(_, v) => setSteps(v)} min={0}>
                <NumberInputField />
                <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                </NumberInputStepper>
            </NumberInput>
            <Select size="md" width={100} value={size} onChange={(v) => setSize(v.target.value)}>
                <option value='FULL'>1</option>
                <option value='HALF'>½</option>
                <option value='QUARTER'>¼</option>
                <option value='EIGHTH'>⅛</option>
            </Select>
            <IconButton
                colorScheme={props.status.led ? 'blue' : 'gray'}
                onClick={onLight}
                aria-label='Light'
                fontSize='20px'
                icon={<MdLightbulbOutline />}
            />
            <IconButton
                isDisabled={props.isDisabled}
                onClick={onRight}
                aria-label='Right'
                fontSize='20px'
                icon={<MdEast />}
            />
        </HStack>
    );
}

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Focus(props: { status: SystemStatus, host: string }) {
    const toast = useToast();

    const [isDisabled, setDisabled] = useState(false);

    const onStart = useCallback((cam: string) => {
        setDisabled(true);

        fetch(`http://${props.host}/cam/preview/start/${cam}`)
            .then(async (r) => {
                if (r.ok) {
                    return await r.text();
                } else {
                    throw new Error(await r.text());
                }
            })
            .then(() => {
                toast({
                    status: "success",
                    title: `Started ${cam} camera`,
                    duration: 1000
                });
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
            .then(async (r) => {
                if (r.ok) {
                    return await r.text();
                } else {
                    throw new Error(await r.text());
                }
            })
            .then(() => {
                toast({
                    status: "success",
                    title: `Stopped ${cam} camera`,
                    duration: 1000
                });
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
            <Relative host={props.host} status={props.status} isDisabled={isDisabled} />
            <Button
                colorScheme={props.status.aux_preview ? 'blue' : 'gray'}
                isDisabled={isDisabled}
                onClick={onAuxToggle}
            >
                {props.status.aux_preview ? "Stop" : "Start"} Aux
            </Button>
            <Button
                colorScheme={props.status.hq_preview ? 'blue' : 'gray'}
                isDisabled={isDisabled}
                onClick={onHqToggle}
            >
                {props.status.hq_preview ? "Stop" : "Start"} HQ
            </Button>
        </VStack>
    );
}
