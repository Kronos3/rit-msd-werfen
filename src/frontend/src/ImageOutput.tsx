import { useState } from "react";
import { Image, VStack } from "@chakra-ui/react";

import ApiForm from "./Form";


export default function ImageOutput(props: { path: string, host: string, schema: any }) {
    const [image, setImage] = useState<string | undefined>();

    return (
        <>
            <ApiForm
                path={props.path}
                host={props.host}
                schema={props.schema}
                onReply={async (response) => {
                    setImage(URL.createObjectURL(await response.blob()));
                }} />
            <VStack>
                {
                    image ? <Image src={image} /> : <></>
                }
            </VStack>
        </>
    )
}