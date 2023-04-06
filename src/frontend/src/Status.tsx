import {
    Stack,
    Badge,
    Switch,
    Button,
    Center
} from '@chakra-ui/react'

import { ApiProps } from './common';
import { useCallback, useEffect, useState } from 'react';

interface StageStatus {
    limit1: boolean;
    limit2: boolean;
    estop: boolean;
    running: boolean;
    led: boolean;
    position: number;
}

function offGreen(state: boolean): string {
    return state ? 'red' : 'green'
}

export default function Status(props: ApiProps) {
    const [state, setState] = useState<StageStatus>({
        limit1: false,
        limit2: false,
        estop: false,
        running: false,
        led: false,
        position: 0
    });

    const [disableEstop, setDisableEstop] = useState(false);

    const eStopPress = useCallback(() => {
        (async () => {
            setDisableEstop(true);
            if (state.estop) {
                // Clear the estop signal
                await fetch(`http://${props.address}:${props.port}/system/estop?stop=false`);
            } else {
                await fetch(`http://${props.address}:${props.port}/system/estop?stop=true`);
            }
        })();
    }, [props.address, props.port, state]);

    const [ping, setPing] = useState<boolean>(true);

    // Ping for status @10Hz
    useEffect(() => {
        if (ping) {
            const interval = setInterval(async () => {
                const responseRaw = await fetch(`http://${props.address}:${props.port}/stage/status`);
                const response: StageStatus = await responseRaw.json();
                setState(response);
                setDisableEstop(false);
            }, 500);
            return () => clearInterval(interval);
        }
    }, [props.address, props.port, ping]);

    return (
        <>
            <Stack paddingTop={4} direction='row' spacing={1} align='center' justify='center'>
                <Badge colorScheme={offGreen(state.limit1)}>LIMIT-1</Badge>
                <Badge colorScheme={offGreen(state.limit2)}>LIMIT-2</Badge>
                <Badge colorScheme={offGreen(state.estop)}>ESTOP</Badge>
                <Badge colorScheme={state.running ? 'blue' : 'gray'}>{state.running ? 'RUNNING' : 'STOPPED'}</Badge>
                <Badge colorScheme='blue'>{state.position}</Badge>
                <Switch alignSelf='right' isChecked={ping} onChange={(e) => setPing(e.target.checked)} />
            </Stack>
            <Center paddingTop={2}>
                <Button
                    colorScheme={state.estop ? "yellow" : "red"}
                    alignSelf='center'
                    onClick={eStopPress}
                    disabled={disableEstop}
                >
                    {state.estop ? "CLEAR E-STOP" : "E-STOP"}
                </Button>
            </Center>
        </>
    )
}
