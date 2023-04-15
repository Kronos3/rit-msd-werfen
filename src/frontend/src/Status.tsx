import {
    Stack,
    Badge,
    Switch
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
    const [ping, setPing] = useState<boolean>(true);

    const refresh = useCallback(async () => {
        const responseRaw = await fetch(`http://${props.host}/stage/status`);
        const response: StageStatus = await responseRaw.json();

        if (JSON.stringify(response) !== JSON.stringify(props.status)) {
            props.setStatus(response);
        }
    }, [props.host, props.status]);

    useEffect(() => {
        if (ping) {
            // Refresh state immediately on effect
            refresh();

            // Keep polling state @2Hz
            const interval = setInterval(refresh, 500);
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
        </>
    )
}
