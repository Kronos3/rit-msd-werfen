import {
    Stack,
    Badge,
    Switch
} from '@chakra-ui/react'

import { useEffect, useState } from 'react';
import { StageStatus } from './api';

function offGreen(state: boolean): string {
    return state ? 'red' : 'green'
}

function onGreen(state: boolean): string {
    return state ? 'green' : 'red'
}

export default function Status(props: { host: string, status: StageStatus, setStatus: (status: StageStatus) => void }) {
    const [ping, setPing] = useState<boolean>(true);

    const refresh = async () => {
        const responseRaw = await fetch(`http://${props.host}/stage/status`);
        const response: StageStatus = await responseRaw.json();

        if (JSON.stringify(response) !== JSON.stringify(props.status)) {
            props.setStatus(response);
        }

        if (ping) {
            setTimeout(refresh, 500);
        }
    };

    useEffect(() => {
        if (ping) {
            refresh();
        }
    }, [props.host, props.status, ping]);

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
