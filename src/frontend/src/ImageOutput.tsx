import { useCallback, useState } from "react";
import { Image, VStack } from "@chakra-ui/react";

import ApiForm from "./Form";


export default function ImageOutput(props: { path: string, host: string, schema: any }) {
    const [image, setImage] = useState<string | undefined>();

    const onReply = useCallback((response: Response) => {
        response.blob().then((blob) => {
            setImage(URL.createObjectURL(blob));
        });
    }, []);

    return (
        <VStack>
            <ApiForm
                path={props.path}
                host={props.host}
                schema={props.schema}
                onReply={onReply} />
            {image ? <Image src={image} /> : <></>}
        </VStack>
    )
}