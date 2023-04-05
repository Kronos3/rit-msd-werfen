import { Renderer, useEventHandler, Text, LineEdit, Window, View, Tabs, TabItem } from "@nodegui/react-nodegui";
import { QLineEditSignals } from "@nodegui/nodegui";

import React, { useState } from "react";

import Operate from './operate';

function App() {

    const [address, setAddress] = useState<string>("localhost");
    const [port, setPort] = useState<number>(8000);

    const onAddress = useEventHandler<QLineEditSignals>(
        { textChanged: (address) => setAddress(address) }, []
    );
    const onPort = useEventHandler<QLineEditSignals>(
        { textChanged: (port) => setPort(parseInt(address)) }, []
    );

    return (
        <Window
            windowTitle="RIT Inspection"
            styleSheet={styleSheet}
        >
            <View id="top" style={containerStyle}>
                <Text>Address</Text>
                <LineEdit style="padding-bottom: 6px"  text={address} on={onAddress} />

                <Text>Port</Text>
                <LineEdit style="padding-bottom: 6px" text={`${port}`} on={onPort} />

                <Tabs>
                    <TabItem title="Operate">
                        <Operate />
                    </TabItem>
                    <TabItem title="Calibrate">
                        <Text>Calibrate Tab</Text>
                    </TabItem>
                </Tabs>
            </View>
        </Window>
    );
}

const containerStyle = `
  flex: 1; 
`;

const styleSheet = `
#top {
    padding-top: 6px;
    padding-bottom: 6px;
    padding-horizontal: 15px;
}
`;

Renderer.render(<App />);
