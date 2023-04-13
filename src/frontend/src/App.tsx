import { useEffect, useState } from 'react';

import {
    Container,
    InputLeftAddon,
    InputGroup,
    Input,
    Text,
    Tabs,
    Select,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
} from '@chakra-ui/react'

import ApiForm from './Form';

import * as cookies from './cookie';
import Status from './Status';
import SingleCard from './SingleCard';
import Camera from './Camera';
import ImageOutput from './ImageOutput';


function App() {
    const [host, setHost] = useState(cookies.get("host") || window.location.host);

    const [stageSelect, setStageSelect] = useState<string>("/stage/relative");

    const [apiSchema, setApiSchema] = useState<any>();

    useEffect(() => {
        fetch(`http://${host}/openapi.json`)
            .then(async value => {
                setApiSchema(await value.json());
            });
    }, [host]);

    useEffect(() => {
        cookies.set("host", host)
    }, [host]);

    return (
        <Container>
            <>
                <Text mb='8px'>Middleware API Address</Text>
                <InputGroup size='sm'>
                    <InputLeftAddon children='http://' />
                    <Input value={host} onChange={(e) => setHost(e.target.value)} />
                </InputGroup>
            </>

            <Status host={host} />

            <Tabs>
                <TabList>
                    <Tab>Operate</Tab>
                    <Tab>Single Card</Tab>
                    <Tab>Stage</Tab>
                    <Tab>Camera</Tab>
                    <Tab>Align</Tab>
                    <Tab>Card ID</Tab>
                    <Tab>USB Mounts</Tab>
                </TabList>

                <TabPanels>
                    <TabPanel>

                    </TabPanel>
                    <TabPanel>
                        <SingleCard host={host} schema={apiSchema} />
                    </TabPanel>
                    <TabPanel>
                        <Select value={stageSelect} onChange={(e) => setStageSelect(e.target.value)}>
                            <option value='/stage/relative'>Relative Motion</option>
                            <option value='/stage/absolute'>Absolute Motion</option>
                            <option value='/stage/set_position'>Set Position</option>
                            <option value='/stage/speed'>Stage Speed</option>
                            <option value='/stage/led_pwm'>Ring Light PWM</option>
                            <option value='/stage/step_off'>Limit Switch Step Off</option>
                        </Select>
                        <ApiForm
                            host={host}
                            path={stageSelect}
                            schema={apiSchema} />
                    </TabPanel>
                    <TabPanel>
                        <Camera host={host} />
                    </TabPanel>
                    <TabPanel>
                        <ImageOutput path="/system/align" host={host} schema={apiSchema} />
                    </TabPanel>
                    <TabPanel>
                        <ImageOutput path="/system/card_id" host={host} schema={apiSchema} />
                    </TabPanel>
                    <TabPanel>
                        <ApiForm path="/linux/mounts" host={host} schema={apiSchema} />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Container>
    );
}

export default App;
