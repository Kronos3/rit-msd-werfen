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
    useToast,
    Stack
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

interface CardIdResponse {
    card_id: string;
    subdir: string;
}

function OperateCalibrated(props: { host: string, usb?: string, schema: any }) {
    const unload = useDisclosure();
    const cardId = useDisclosure();
    const singleCard = useDisclosure();
    const cardIdChange = useDisclosure();

    const toast = useToast();

    const [disabled, setDisabled] = useState<boolean>(false);

    const [images, setImages] = useState<string[]>([]);
    const [cardIdImg, setCardIdImg] = useState<string | undefined>();
    const [cardIdResponse, setCardIdResponse] = useState<CardIdResponse | undefined>();

    const [unloadParams, setUnloadParams] = useState(cookies.getJson("unloadParams") ?? { n: -2000, size: "QUARTER" });
    useEffect(() => {
        cookies.set("unloadParams", JSON.stringify(unloadParams));
    }, [unloadParams]);

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
        fetch(`http://${props.host}/stage/absolute?n=${generateQuery(unloadParams)}`,
            { method: "POST" }
        ).finally(() => {
            setDisabled(false);
        });
    }, [unloadParams, props.host]);

    const onImageCard = useCallback(() => {
        setDisabled(true);

        (async () => {
            setImages([]);
            setCardIdResponse(undefined);
            setCardIdImg(undefined);

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
            const card_id_img_fid = fids[fids.length - 2];
            const card_id_fid = fids[fids.length - 1];
            fids.splice(fids.length - 2, 2);

            const out = [];
            for (const fid of fids) {
                const fidRes = await fetch(`http://${props.host}/future/${fid}`)
                const imgBlob = await fidRes.blob();
                out.push(imgBlob);
                setImages(out.map(v => URL.createObjectURL(v)));
            }

            const fidResImg = await fetch(`http://${props.host}/future/${card_id_img_fid}`);
            setCardIdImg(URL.createObjectURL(await fidResImg.blob()));

            const fidResText = await fetch(`http://${props.host}/future/${card_id_fid}`);
            setCardIdResponse(await fidResText.json());
            onLoadUnload();
        })().finally(() => {
            setDisabled(false);
        });
    }, [cardIdParams, onLoadUnload, singleCardParams, props.usb, props.host]);

    return (
        <VStack align="stretch">
            <Modal isOpen={unload.isOpen} onClose={unload.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Unload position</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <SettingsForm
                            value={unloadParams}
                            setValue={setUnloadParams}
                            path="/stage/absolute"
                            schema={props.schema}
                            propertyFilterOut={["ignore_limits"]} />
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
            <SimpleGrid columns={4} spacing={2}>
                {images.map((img, i) => (
                    <Image key={i} src={img} />
                ))}
            </SimpleGrid>
            <Modal isOpen={cardIdChange.isOpen} onClose={cardIdChange.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Change Card ID</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <Form
                            formData={cardIdResponse?.card_id}
                            onChange={(e) => setCardIdResponse((cardIdResponse) ? { ...cardIdResponse, card_id: e.formData } : undefined)}
                            schema={{ type: "string" }}
                            validator={validator}
                            onSubmit={async (e) => {
                                cardIdChange.onClose();

                                const query = generateQuery({
                                    to_id: e.formData,
                                    subdir: cardIdResponse?.subdir,
                                    path: props.usb
                                });
                                const response = await fetch(`http://${props.host}/system/rename?${query}`, {
                                    method: "POST",
                                    headers: { "Content-Type": "application/json" },
                                });

                                if (response.ok) {
                                    toast({
                                        title: `Successfully renameed card ID to ${e.formData}`,
                                        description: await response.text(),
                                        status: "error"
                                    });
                                    setCardIdResponse(await response.json());
                                } else {
                                    toast({
                                        title: "Failed to rename card ID",
                                        description: await response.text(),
                                        status: "error"
                                    });
                                }

                                setDisabled(false);
                            }}
                        />
                    </ModalBody>
                    <ModalFooter />
                </ModalContent>
            </Modal>
            {
                (cardIdResponse !== undefined) ? (
                    <Stack paddingTop={8} direction='row' spacing={4} align='center' justify='center'>
                        {cardIdImg ? <Image src={cardIdImg} /> : <></>}
                        <Text>{cardIdResponse.card_id}</Text>
                        <IconButton
                            isDisabled={disabled}
                            onClick={cardIdChange.onOpen}
                            aria-label='Change ID'
                            fontSize='20px'
                            icon={<MdOutlineMode />}
                        />
                    </Stack>
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
