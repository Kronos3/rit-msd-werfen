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
} from '@chakra-ui/react'

import ApiForm from './Form';


function App() {
    const [address, setAddress] = useState("localhost");
    const [port, setPort] = useState(8000);

    const portDisclose = useDisclosure();
    const portCancelRef = React.useRef<any>();

    const [apiSchema, setApiSchema] = useState<any>();

    useEffect(() => {
        fetch(`http://${address}:${port}/openapi.json`)
            .then(async value => {
                setApiSchema(await value.json());
            });
    }, [address, port])

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
                            <Input value={`${port}`} onChange={(e) => setPort(parseInt(e.target.value))}/>
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
                        <p>three!</p>
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Container>
    );
}

export default App;
