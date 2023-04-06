import { useCallback, useState } from "react";

import { ApiProps } from "./common";

import {
    Image,
    Select,
    Button,
    Center,
} from '@chakra-ui/react'

export default function Camera(props: ApiProps) {
    const [camera, setCamera] = useState("hq");
    const [image, setImage] = useState<Blob | undefined>();
    const [disabled, setDisabled] = useState(false);

    const onAcquire = useCallback(() => {
        // Clear the image display
        setImage(undefined);
        (async () => {
            setDisabled(true);
            const response = await fetch(`http://${props.address}:${props.port}/cam/acquire/${camera}`);
            setImage(await response.blob());
            setDisabled(false);
        })();
    }, [camera, props.address, props.port]);

    return (
        <>
            <Select disabled={disabled} value={camera} onChange={(e) => setCamera(e.target.value)}>
                <option value='hq'>HQ Camera</option>
                <option value='aux'>Auxilliary Camera</option>
            </Select>
            <Center
                marginTop={3}
                marginBottom={3}>
                <Button
                    disabled={disabled}
                    onClick={onAcquire}>Acquire</Button>
            </Center>
            {
                image ? <Image src={URL.createObjectURL(image)} /> : <></>
            }
        </>
    )
}