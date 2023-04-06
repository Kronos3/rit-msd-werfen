import { useState } from "react";

import ApiForm from "./Form";
import { ApiProps } from "./common";

import { Image, VStack } from "@chakra-ui/react";

export default function SingleCard(props: ApiProps & { schema: any }) {
    const [images, setImages] = useState<Uint8Array[]>([]);

    return (
        <>
            <ApiForm
                address={props.address}
                port={props.port}
                path="/system/single_card"
                schema={props.schema}
                onReply={async (response) => {

                    const imgOut: Uint8Array[] = [];
                    setImages([]);

                    if (response.body) {
                        const reader = response.body.getReader();

                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) {
                                break;
                            } else if (!value) {
                                continue
                            }

                            imgOut.push(value);
                            setImages([...imgOut]);
                        }
                    }
                }} />
            <VStack>
                {
                    images.map(v => <Image src={URL.createObjectURL(new Blob([v]))} />)
                }
            </VStack>
        </>
    )
}