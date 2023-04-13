import {
    Stack,
    Badge,
    Switch,
    Button,
    Center
} from '@chakra-ui/react'

import { useCallback, useEffect, useState } from 'react';
import { StageStatus } from './api';

function offGreen(state: boolean): string {
    return state ? 'red' : 'green'
}

function onGreen(state: boolean): string {
    return state ? 'green' : 'red'
}

export default function Status(props: { host: string, status: StageStatus, setStatus: (status: StageStatus) => void }) {
    const [disableEstop, setDisableEstop] = useState(false);

    const eStopPress = useCallback(() => {
        (async () => {
            setDisableEstop(true);
            if (props.status.estop) {
                // Clear the estop signal
                await fetch(`http://${props.host}/system/estop?stop=false`);
            } else {
                await fetch(`http://${props.host}/system/estop?stop=true`);
            }
        })();
    }, [props.host, props.status]);

    const [ping, setPing] = useState<boolean>(true);

    // Ping for status @10Hz
    useEffect(() => {
        if (ping) {
            const interval = setInterval(async () => {
                const responseRaw = await fetch(`http://${props.host}/stage/status`);
                const response: StageStatus = await responseRaw.json();
                props.setStatus(response);
                setDisableEstop(false);
            }, 500);
            return () => clearInterval(interval);
        }
    }, [props.host, ping]);

    return (
        <>
            <Stack paddingTop={4} direction='row' spacing={1} align='center' justify='center'>
                <Badge colorScheme={onGreen(props.status.calibrated)}>CALIBRATED</Badge>
                <Badge colorScheme={offGreen(props.status.limit1)}>LIMIT-1</Badge>
                <Badge colorScheme={offGreen(props.status.limit2)}>LIMIT-2</Badge>
                <Badge colorScheme={offGreen(props.status.estop)}>ESTOP</Badge>
                <Badge colorScheme={onGreen(props.status.led)}>RING</Badge>
                <Badge colorScheme={props.status.running ? 'blue' : 'gray'}>{props.status.running ? 'RUNNING' : 'STOPPED'}</Badge>
                <Badge colorScheme='blue'>{props.status.position}</Badge>
                <Switch alignSelf='right' isChecked={ping} onChange={(e) => setPing(e.target.checked)} />
            </Stack>
            <Center paddingTop={2}>
                <Button
                    colorScheme={props.status.estop ? "yellow" : "red"}
                    alignSelf='center'
                    onClick={eStopPress}
                    disabled={disableEstop}
                >
                    {props.status.estop ? "CLEAR E-STOP" : "E-STOP"}
                </Button>
            </Center>
        </>
    )
}
