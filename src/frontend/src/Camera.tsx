import { useCallback, useState } from "react";

import {
    Image,
    Select,
    Button,
    Center,
} from '@chakra-ui/react';

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Camera(props: { host: string }) {
    const [camera, setCamera] = useState("hq");
    const [image, setImage] = useState<string | undefined>();
    const [disabled, setDisabled] = useState(false);

    const onAcquire = useCallback(() => {
        // Clear the image display
        setImage(undefined);
        (async () => {
            setDisabled(true);
            const response = await fetch(`http://${props.host}/cam/acquire/${camera}`);
            setImage(URL.createObjectURL(await response.blob()));
            setDisabled(false);
        })();
    }, [camera, props.host]);

    return (
        <>
            <Select disabled={disabled} value={camera} onChange={(e) => setCamera(e.target.value)}>
                <option value='hq'>HQ Camera</option>
                <option value='aux'>Auxiliary Camera</option>
            </Select>
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