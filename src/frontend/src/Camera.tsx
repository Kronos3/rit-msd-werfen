import { useCallback, useState } from "react";

import {
    Image,
    Select,
    Button,
    Center,
    NumberInput,
    Text,
    NumberInputField,
    Input
} from '@chakra-ui/react';

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Camera(props: { host: string }) {
    const [camera, setCamera] = useState("hq");
    const [image, setImage] = useState<string | undefined>();
    const [disabled, setDisabled] = useState(false);
    const [scale, setScale] = useState<number>(0.2);

    const onAcquire = useCallback(() => {
        // Clear the image display
        setImage(undefined);
        setDisabled(true);
        (async () => {
            const response = await fetch(`http://${props.host}/cam/acquire/${camera}?scale=${scale}`);
            setImage(URL.createObjectURL(await response.blob()));
        })().finally(() => setDisabled(false));
    }, [camera, props.host]);

    return (
        <>
            <Select disabled={disabled} value={camera} onChange={(e) => setCamera(e.target.value)}>
                <option value='hq'>HQ Camera</option>
                <option value='aux'>Auxiliary Camera</option>
            </Select>
            <Text>Scale</Text>
            <Input
                value={scale}
                onChange={(v) => setScale(parseFloat(v.target.value))}>
            </Input>
            <Center
                marginTop={3}
                marginBottom={3}>
                <Button
                    disabled={disabled}
                    onClick={onAcquire}>Acquire</Button>
            </Center>
            {
                image ? <Image src={image} /> : <></>
            }
        </>
    );
}