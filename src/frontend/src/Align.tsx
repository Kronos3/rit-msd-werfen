import { useState } from "react";

import ApiForm from "./Form";

import { Image, VStack } from "@chakra-ui/react";

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