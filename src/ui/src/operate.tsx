import { View, ComboBox } from "@nodegui/react-nodegui";
import React from "react";


export default function Operate() {
    return (
        <View>
            <ComboBox items={[
                { text: "Single Card" },
                { text: "Absolute Motion" }
            ]} />
        </View>
    )
}
