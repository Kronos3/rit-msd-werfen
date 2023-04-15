import { useState } from "react";
import { Image, VStack } from "@chakra-ui/react";

import ApiForm from "./Form";


export default function SingleCard(props: { host: string, schema: any }) {
    const [images, setImages] = useState<string[]>([]);

    return (
        <>
            <ApiForm
                host={props.host}
                path="/system/single_card"
                schema={props.schema}
                onReply={async (response) => {
                    const fids: number[] = await response.json()
                    setImages([]);
                    const out = [];
                    for (const fid of fids) {
                        const fidRes = await fetch(`http://${props.host}/future/${fid}`)
                        const imgBlob = await fidRes.blob();
                        out.push(imgBlob);
                        setImages(out.map(v => URL.createObjectURL(v)));
                    }
                }} />
            <VStack>
                {
                    images.map((v, idx) => <Image key={idx} src={v} />)
                }
            </VStack>
        </>
    )
}