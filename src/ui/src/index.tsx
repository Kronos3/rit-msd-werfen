import { Renderer, Text, Window, View, Tabs, TabItem } from "@nodegui/react-nodegui";
import React from "react";

import Operate from './operate';

function App() {
    return (
        <Window windowTitle="RIT Inspection">
            <View>
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

Renderer.render(<App />);
