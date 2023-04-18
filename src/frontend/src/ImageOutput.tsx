import { useCallback, useEffect, useState } from "react";
import { Image, VStack } from "@chakra-ui/react";

import ApiForm from "./Form";


// eslint-disable-next-line @typescript-eslint/naming-convention
export default function ImageOutput(props: { path: string, host: string, schema: any, sequenced?: boolean }) {
    const [image, setImage] = useState<string | undefined>();
    const [seqFid, setSeqFid] = useState<number | undefined>();

    const onReply = useCallback((response: Response) => {
        if (props.sequenced) {
            response.json().then((n) => setSeqFid(n));
        }
        else {
            response.blob().then((blob) => {
                setImage(URL.createObjectURL(blob));
            });
        }
    }, [props.sequenced]);

    const requestNewImg = useCallback(() => {
        console.log(seqFid);
        fetch(`http://${props.host}/sfuture/${seqFid}`)
                .then((res) => {
                    if (res.status === 204) {
                        console.log("Done");
                        // No more content
                    } else if (res.ok && res.status === 200) {
                        res.blob().then((blob) => {
                            console.log("img");
                            setImage(URL.createObjectURL(blob));
                            requestNewImg();
                        });
                    }
                });
    }, [seqFid]);

    useEffect(() => {
        if (seqFid !== undefined) {
            requestNewImg();
        }
    }, [seqFid]);

    return (
        <VStack align={"stretch"}>
            <ApiForm
                path={props.path}
                host={props.host}
                schema={props.schema}
                onReply={onReply} />
            {image ? <Image src={image} /> : <></>}
        </VStack>
    );
}
