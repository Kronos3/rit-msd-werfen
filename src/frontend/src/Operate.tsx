import {
    Image,
    HStack,
    Text,
    Button,
    VStack,
    IconButton,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalCloseButton,
    ModalBody,
    ModalFooter,
    useDisclosure,
    SimpleGrid,
    useToast
} from '@chakra-ui/react';
import validator from '@rjsf/validator-ajv8';

import { useCallback, useEffect, useState } from 'react';
import {
    MdSettings,
    MdOutlineQrCode,
    MdPhotoCamera,
    MdOutlineMode
} from 'react-icons/md';
import { Form } from '@rjsf/chakra-ui';

import { StageStatus } from './api';
import * as cookies from './cookie';
import { generateQuery } from './Form';
import SettingsForm from './SettingsForm';

function OperateCalibrated(props: { host: string, usb?: string, schema: any }) {
    const unload = useDisclosure();
    const cardId = useDisclosure();
    const singleCard = useDisclosure();
    const cardIdChange = useDisclosure();

    const toast = useToast();

    const [disabled, setDisabled] = useState<boolean>(false);

    const [images, setImages] = useState<Blob[]>([]);
    const [cardIdOutput, setCardIdOutput] = useState<string | undefined>();

    const [unloadPosition, setUnloadPosition] = useState<number>(cookies.getJson("unloadPosition") ?? -2000);
    useEffect(() => {
        cookies.set("unloadPosition", JSON.stringify(unloadPosition));
    }, [unloadPosition]);

    const [cardIdParams, setCardIdParams] = useState(cookies.getJson("cardIdParams"));
    useEffect(() => {
        cookies.set("cardIdParams", JSON.stringify(cardIdParams));
    }, [cardIdParams]);

    const [singleCardParams, setSingleCardParams] = useState(cookies.getJson("singleCardParams"));
    useEffect(() => {
        cookies.set("singleCardParams", JSON.stringify(singleCardParams));
    }, [singleCardParams]);

    const onLoadUnload = useCallback(() => {
        setDisabled(true);
        fetch(`http://${props.host}/stage/absolute?n=${unloadPosition}`,
            { method: "POST" }
        ).finally(() => {
            setDisabled(false);
        });
    }, [unloadPosition, props.host]);

    const onImageCard = useCallback(() => {
        setDisabled(true);

        (async () => {
            setImages([]);
            setCardIdOutput(undefined);

            const body = {
                "sensor": singleCardParams,
                "card_id": cardIdParams,
                "path": props.usb
            };

            const response = await fetch(`http://${props.host}/system/run`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                toast({
                    title: "Failed to acquire single card",
                    description: await response.text(),
                    status: "error"
                });
                return;
            }

            const fids: number[] = await response.json();

            // The final future id is the card ID string
            // It is just plaintext not an image
            const card_id_fid = fids[fids.length - 1];
            fids.splice(fids.length - 1, 1);

            const out = [];
            for (const fid of fids) {
                const fidRes = await fetch(`http://${props.host}/future/${fid}`)
                const imgBlob = await fidRes.blob();
                out.push(imgBlob);
                setImages([...out]);
            }

            const fidRes = await fetch(`http://${props.host}/future/${card_id_fid}`);
            setCardIdOutput(await fidRes.text());
            onLoadUnload();

        })().finally(() => {
            setDisabled(false);
        });
    }, [cardIdParams, singleCardParams, props.host]);

    return (
        <VStack align="stretch">
            <Modal isOpen={unload.isOpen} onClose={unload.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Unload position</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Form
                            formData={unloadPosition}
                            onChange={e => setUnloadPosition(e.formData)}
                            schema={{ type: "number" }}
                            validator={validator}><div></div></Form>
                    </ModalBody>
                    <ModalFooter />
                </ModalContent>
            </Modal>
            <Modal isOpen={cardId.isOpen} onClose={cardId.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Card ID Parameters</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <SettingsForm
                            value={cardIdParams}
                            setValue={setCardIdParams}
                            path="/system/card_id"
                            schema={props.schema}
                            propertyFilterOut={["return_img"]} />
                    </ModalBody>

                    <ModalFooter />
                </ModalContent>
            </Modal>
            <Modal isOpen={singleCard.isOpen} onClose={singleCard.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Sensor Imaging Parameters</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <SettingsForm
                            value={singleCardParams}
                            setValue={setSingleCardParams}
                            path="/system/single_card"
                            schema={props.schema}
                            propertyFilterOut={["buffer"]} />
                    </ModalBody>

                    <ModalFooter />
                </ModalContent>
            </Modal>
            <SimpleGrid columns={2} spacing={2}>
                <HStack>
                    <Text>Move to load / unload sensor card</Text>
                    <IconButton
                        isDisabled={disabled}
                        onClick={unload.onOpen}
                        aria-label='Settings'
                        fontSize='20px'
                        icon={<MdSettings />}
                    />
                </HStack>
                <HStack>
                    <Text>Image a loaded card</Text>
                    <IconButton
                        isDisabled={disabled}
                        onClick={cardId.onOpen}
                        aria-label='Card ID'
                        fontSize='20px'
                        icon={<MdOutlineQrCode />}
                    />
                    <IconButton
                        isDisabled={disabled}
                        onClick={singleCard.onOpen}
                        aria-label='Sensor Settings'
                        fontSize='20px'
                        icon={<MdPhotoCamera />}
                    />
                </HStack>
                <Button colorScheme='blue' isDisabled={disabled} onClick={onLoadUnload}>Load/Unload</Button>
                <Button colorScheme='blue' isDisabled={disabled || !props.usb} onClick={onImageCard}>Image Card</Button>
            </SimpleGrid>
            <SimpleGrid columns={3} spacing={2}>
                {images.map((img, i) => (
                    <Image key={i} src={URL.createObjectURL(img)} />
                ))}
            </SimpleGrid>
            <Modal isOpen={cardIdChange.isOpen} onClose={cardIdChange.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Unload position</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Form
                            formData={cardIdOutput}
                            schema={{ type: "string" }}
                            validator={validator}
                            onSubmit={async (event) => {
                                const query = generateQuery({
                                    fromId: cardIdOutput,
                                    toId: event.formData
                                });
                                const response = await fetch(`http://${props.host}/system/rename?${query}`, {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                });

                                if (response.ok) {
                                    setCardIdOutput(event.formData);
                                }

                                setDisabled(false);
                            }}
                        />
                    </ModalBody>
                    <ModalFooter />
                </ModalContent>
            </Modal>
            {
                (cardIdOutput !== undefined) ? (
                    <HStack>
                        <Text>{cardIdOutput}</Text>
                        <IconButton
                            isDisabled={disabled}
                            onClick={cardIdChange.onOpen}
                            aria-label='Change ID'
                            fontSize='20px'
                            icon={<MdOutlineMode />}
                        />
                    </HStack>
                ) : <></>
            }
        </VStack>
    );
}

function OperateUncalibrated(props: { host: string, schema: any }) {
    const [isDisabled, setDisabled] = useState<boolean>(false);
    const { isOpen, onOpen, onClose } = useDisclosure();
    const [settings, setSettings] = useState(cookies.getJson("alignmentParams"));

    useEffect(() => {
        if (settings) {
            cookies.set("alignmentParams", JSON.stringify(settings));
        }
    }, [settings]);

    const onAlign = useCallback(() => {
        setDisabled(true);
        (async () => {
            const query = generateQuery(settings);
            await fetch(`http://${props.host}/system/align?${query}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });

            setDisabled(false);
        })();
    }, [settings]);

    return (
        <VStack align="stretch">
            <Modal isOpen={isOpen} onClose={onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Alignment Parameters</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <SettingsForm value={settings} setValue={setSettings} path="/system/align" schema={props.schema} />
                    </ModalBody>

                    <ModalFooter />
                </ModalContent>
            </Modal>
            <HStack alignSelf="center">
                <Text>Stage must be aligned before continuing</Text>
                <IconButton
                    isDisabled={isDisabled}
                    onClick={onOpen}
                    aria-label='Settings'
                    fontSize='20px'
                    icon={<MdSettings />}
                />
            </HStack>
            <Button
                isDisabled={isDisabled}
                onClick={onAlign}
                colorScheme='blue'
                minW="sm"
                alignSelf="center"
            >
                Align
            </Button>
        </VStack>
    )
}

export default function Operate(props: { status: StageStatus, usb?: string, host: string, schema: any }) {
    return <>
        {
            props.status.calibrated ?
                <OperateCalibrated host={props.host} usb={props.usb} schema={props.schema} />
                : <OperateUncalibrated host={props.host} schema={props.schema} />
        }
    </>
}
