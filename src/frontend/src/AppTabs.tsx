import { useCallback, useState } from 'react';

import {
    Tabs,
    Select,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
} from '@chakra-ui/react';

import ApiForm from './Form';

import { StageStatus } from './api';

import SingleCard from './SingleCard';
import Camera from './Camera';
import ImageOutput from './ImageOutput';
import Operate from './Operate';
import ViewMode from './View';


// eslint-disable-next-line @typescript-eslint/naming-convention
export default function AppTabs(props: { devMode: boolean, usb?: string, status: StageStatus, host: string, schema: any }) {
    const [stageSelect, setStageSelect] = useState<string>("/stage/relative");
    const [cardRefresh, setCardRefresh] = useState<number>(0);

    const refreshCards = useCallback(() => {
        setCardRefresh(cardRefresh + 1);
    }, [cardRefresh]);

    return (
        <Tabs>
            <TabList>
                <Tab>Operate</Tab>
                <Tab>View</Tab>
                {
                    props.devMode ?
                        <>
                            <Tab>Single Card</Tab>
                            <Tab>Stage</Tab>
                            <Tab>Camera</Tab>
                            <Tab>Align</Tab>
                            <Tab>Card ID</Tab>
                            <Tab>USB Mounts</Tab>
                        </>
                        : <></>
                }
            </TabList>

            <TabPanels>
                <TabPanel>
                    <Operate status={props.status} onRefresh={refreshCards} usb={props.usb} host={props.host} schema={props.schema} />
                </TabPanel>
                <TabPanel>
                    <ViewMode host={props.host} refresh={cardRefresh} usb={props.usb} />
                </TabPanel>
                {
                    props.devMode ? ([
                        <TabPanel key={1}>
                            <SingleCard host={props.host} schema={props.schema} />
                        </TabPanel>,
                        <TabPanel key={2}>
                            <Select value={stageSelect} onChange={(e) => setStageSelect(e.target.value)}>
                                <option value='/stage/relative'>Relative Motion</option>
                                <option value='/stage/absolute'>Absolute Motion</option>
                                <option value='/stage/set_position'>Set Position</option>
                                <option value='/stage/speed'>Stage Speed</option>
                                <option value='/stage/led_pwm'>Ring Light PWM</option>
                                <option value='/stage/step_off'>Limit Switch Step Off</option>
                            </Select>
                            <ApiForm
                                host={props.host}
                                path={stageSelect}
                                schema={props.schema} />
                        </TabPanel>,
                        <TabPanel key={3}>
                            <Camera host={props.host} />
                        </TabPanel>,
                        <TabPanel key={4}>
                            <ImageOutput path="/system/debug_align" host={props.host} schema={props.schema} sequenced={true} />
                        </TabPanel>,
                        <TabPanel key={5}>
                            <ImageOutput path="/system/card_id" host={props.host} schema={props.schema} />
                        </TabPanel>,
                        <TabPanel key={6}>
                            <ApiForm path="/linux/mounts" host={props.host} schema={props.schema} />
                        </TabPanel>
                    ]) : <></>
                }
            </TabPanels>
        </Tabs>
    );
}