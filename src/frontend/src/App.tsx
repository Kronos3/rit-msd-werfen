import { useCallback, useEffect, useState } from 'react';

import {
    InputLeftAddon,
    InputGroup,
    Input,
    Flex,
    Box,
    Spacer,
    Checkbox,
    Container,
    VStack,
    Button
} from '@chakra-ui/react';

import { SystemStatus } from './api';

import * as cookies from './cookie';
import Status from './Status';
import AppTabs from './AppTabs';
import Usb from './Usb';


// eslint-disable-next-line @typescript-eslint/naming-convention
function App() {
    const [host, setHost] = useState(cookies.get("host") || window.location.host);
    const [schema, setSchema] = useState<any>();
    const [usb, setUsb] = useState<string | undefined>();

    const [devMode, setDevMode] = useState<boolean>(false);
    const [statusValid, setStatusValid] = useState<boolean>(false);

    const [status, setStatus] = useState<SystemStatus>({
        limit1: false,
        limit2: false,
        estop: false,
        running: false,
        led: false,
        calibrated: false,
        position: 0,
        // eslint-disable-next-line @typescript-eslint/naming-convention
        hq_preview: false,
        // eslint-disable-next-line @typescript-eslint/naming-convention
        aux_preview: false
    });

    useEffect(() => {
        fetch(`http://${host}/openapi.json`)
            .then(async value => {
                setSchema(await value.json());
            });
    }, [host]);

    useEffect(() => {
        cookies.set("host", host);
    }, [host]);

    const eStopPress = useCallback(() => {
        (async () => {
            if (status.estop) {
                // Clear the estop signal
                await fetch(`http://${host}/system/estop?stop=false`);
            } else {
                await fetch(`http://${host}/system/estop?stop=true`);
            }
        })();
    }, [host, status]);

    return (
        <Container maxW="container.md">
            <VStack align="stretch">
                <div>
                    <Flex>
                        <Box p='4'>
                            Middleware API Address
                        </Box>
                        <Spacer />
                        <Box p='2'>
                            <Button
                                colorScheme={status.estop ? "yellow" : "red"}
                                alignSelf='center'
                                onClick={eStopPress}
                            >
                                {status.estop ? "CLEAR E-STOP" : "E-STOP"}
                            </Button>
                        </Box>
                        <Spacer />
                        <Box p='4'>
                            <Checkbox isChecked={devMode} onChange={(e) => setDevMode(e.target.checked)}>Dev Mode</Checkbox>
                        </Box>
                    </Flex>
                    <InputGroup size='sm'>
                        <InputLeftAddon children='http://' />
                        <Input isInvalid={!statusValid} value={host} onChange={(e) => setHost(e.target.value)} />
                    </InputGroup>
                    <Status status={status} setStatusValid={setStatusValid} setStatus={setStatus} host={host} />
                </div>

                <Usb host={host} setUsb={setUsb} usb={usb} />
                <AppTabs devMode={devMode} usb={usb} status={status} host={host} schema={schema} />
            </VStack>
        </Container>
    );
}

export default App;
