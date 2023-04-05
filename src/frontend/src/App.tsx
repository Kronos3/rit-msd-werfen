import React, { useEffect, useState } from 'react';

import {
    AlertDialog,
    Container,
    InputLeftAddon,
    InputRightAddon,
    InputGroup,
    Input,
    Text,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    useDisclosure,
    AlertDialogOverlay,
    AlertDialogContent,
    AlertDialogHeader,
    Button,
    AlertDialogBody,
    AlertDialogFooter,
    Select
} from '@chakra-ui/react'

import ApiForm from './Form';

import * as cookies from './cookie';


function App() {
    const [address, setAddress] = useState(cookies.get("address") || "localhost");
    const [port, setPort] = useState(parseInt(cookies.get("port") || "8000"));

    const [stageSelect, setStageSelect] = useState<string>("/stage/relative");

    const portDisclose = useDisclosure();
    const portCancelRef = React.useRef<any>();

    const [apiSchema, setApiSchema] = useState<any>();

    useEffect(() => {
        fetch(`http://${address}:${port}/openapi.json`)
            .then(async value => {
                setApiSchema(await value.json());
            });
    }, [address, port]);

    useEffect(() => {
        cookies.set("address", address)
    }, [address]);

    useEffect(() => {
        cookies.set("port", `${port}`)
    }, [port]);

    return (
        <Container>
            <>
                <Text mb='8px'>Middleware API Address</Text>
                <InputGroup size='sm'>
                    <InputLeftAddon children='http://' />
                    <Input placeholder='localhost' value={address} onChange={(e) => setAddress(e.target.value)} />
                    <InputRightAddon onClick={portDisclose.onOpen} children={`:${port}`} />
                </InputGroup>
            </>

            <AlertDialog
                isOpen={portDisclose.isOpen}
                leastDestructiveRef={portCancelRef}
                onClose={portDisclose.onClose}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize='lg' fontWeight='bold'>
                            Set port
                        </AlertDialogHeader>

                        <AlertDialogBody>
                            <Input value={`${port}`} onChange={(e) => setPort(parseInt(e.target.value))} />
                        </AlertDialogBody>

                        <AlertDialogFooter>
                            <Button ref={portCancelRef} onClick={portDisclose.onClose}>
                                Close
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>

            <Tabs>
                <TabList>
                    <Tab>Operate</Tab>
                    <Tab>Single Card</Tab>
                    <Tab>Stage</Tab>
                    <Tab>Calibrate</Tab>
                </TabList>

                <TabPanels>
                    <TabPanel></TabPanel>
                    <TabPanel>
                        <ApiForm
                            address={address}
                            port={port}
                            path="/system/single_card"
                            schema={apiSchema}
                            onReply={(response) => {

                            }} />
                    </TabPanel>
                    <TabPanel>
                        <Select value={stageSelect} onChange={(e) => setStageSelect(e.target.value)} placeholder='Select option'>
                            <option value='/stage/relative'>Relative Motion</option>
                            <option value='/stage/absolute'>Absolute Motion</option>
                            <option value='/stage/speed'>Stage Speed</option>
                            <option value='/stage/led_pwm'>Ring Light PWM</option>
                        </Select>
                        <ApiForm
                            address={address}
                            port={port}
                            path={stageSelect}
                            schema={apiSchema}/>
                    </TabPanel>
                    <TabPanel>
                        <p>Calibrate</p>
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Container>
    );
}

export default App;
