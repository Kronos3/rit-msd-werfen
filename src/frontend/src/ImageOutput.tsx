import { useCallback, useEffect, useState } from "react";
import { Image, VStack } from "@chakra-ui/react";

import ApiForm from "./Form";


// eslint-disable-next-line @typescript-eslint/naming-convention
export default function ImageOutput(props: { path: string, host: string, schema: any, sequenced?: boolean }) {
    const [image, setImage] = useState<string | undefined>();

    const requestNewImg = useCallback((fid: number) => {
        fetch(`http://${props.host}/sfuture/${fid}`)
            .then((res) => {
                if (res.status === 204) {
                    console.log("Done");
                    // No more content
                } else if (res.ok && res.status === 200) {
                    res.blob().then((blob) => {
                        console.log("img");
                        setImage(URL.createObjectURL(blob));
                        requestNewImg(fid);
                    });
                }
            }).catch(() => {
                requestNewImg(fid);
            });
    }, []);

    const onReply = useCallback((response: Response) => {
        if (props.sequenced) {
            response.json().then((n) => {
                requestNewImg(n);
            });
        }
        else {
            response.blob().then((blob) => {
                setImage(URL.createObjectURL(blob));
            });
        }
    }, [props.sequenced, requestNewImg]);

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
