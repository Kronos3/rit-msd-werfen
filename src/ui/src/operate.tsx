import { View, Text, ComboBox, useEventHandler } from "@nodegui/react-nodegui";
import { QComboBoxSignals } from "@nodegui/nodegui";

import React, { useState } from "react";


enum Actions {
    singleCard,
    absoluteMotion,
}

function SingleCard(props: { setRequest: (state: unknown) => void }) {
    return <>
        <Text>Single Card</Text>
    </>
}

function AbsoluteMotion(props: { setRequest: (state: unknown) => void }) {
    return <>
        <Text>Absolute Motion</Text>
    </>
}

function ActionSelect(props: { action: Actions, setRequest: (state: unknown) => void }) {
    switch (props.action) {
        case Actions.singleCard:
            return <SingleCard setRequest={props.setRequest} />
        case Actions.absoluteMotion:
            return <AbsoluteMotion setRequest={props.setRequest} />
        default:
            throw new Error()
    }
}

export default function Operate() {
    const [action, setAction] = useState<Actions>(Actions.singleCard);
    const [request, setRequest] = useState<unknown>();

    const actionHandler = useEventHandler<QComboBoxSignals>(
        { currentIndexChanged: (index) => setAction(index) }, []
    );

    return (
        <View>
            <ComboBox items={[
                { text: "Single Card" },
                { text: "Absolute Motion" }
            ]} on={actionHandler} currentIndex={action} />
            <ActionSelect action={action} setRequest={setRequest} />
        </View>
    );
}
