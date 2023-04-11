import { useState } from "react";
import { Image, VStack } from "@chakra-ui/react";

import ApiForm from "./Form";


export default function Align(props: { host: string, schema: any }) {
    const [image, setImage] = useState<Blob | undefined>();

    return (
        <>
            <ApiForm
                host={props.host}
                path="/system/align"
                schema={props.schema}
                onReply={async (response) => {
                    setImage(await response.blob());
                }} />
            <VStack>
                {
                    image ? <Image src={URL.createObjectURL(image)} /> : <></>
                }
            </VStack>
        </>
    )
}