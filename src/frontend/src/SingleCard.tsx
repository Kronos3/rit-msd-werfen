import { useState } from "react";

import ApiForm from "./Form";
import { ApiProps } from "./common";

import { Image, VStack } from "@chakra-ui/react";

export default function SingleCard(props: ApiProps & { schema: any }) {
    const [images, setImages] = useState<Blob[]>([]);

    return (
        <>
            <ApiForm
                address={props.address}
                port={props.port}
                path="/system/single_card"
                schema={props.schema}
                onReply={async (response) => {
                    const fids: number[] = await response.json()
                    setImages([]);
                    const out = [];
                    for (const fid of fids) {
                        const fidRes = await fetch(`http://${props.address}:${props.port}/future/${fid}`)
                        const imgBlob = await fidRes.blob();
                        out.push(imgBlob);
                        setImages([...out]);
                    }
                }} />
            <VStack>
                {
                    images.map(v => <Image src={URL.createObjectURL(v)} />)
                }
            </VStack>
        </>
    )
}