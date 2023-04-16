import {
    Stack,
    IconButton,
    Text,
    VStack,
    SimpleGrid,
    Card,
    Image,
    Heading,
    MenuDivider,
    Button,
    useToast,
    Badge,
    Spinner,
    useDisclosure,
    AlertDialog,
    AlertDialogOverlay,
    AlertDialogContent,
    AlertDialogHeader,
    AlertDialogBody,
    AlertDialogFooter,
    Modal,
    ModalOverlay,
    ModalContent,
    ModalHeader,
    ModalCloseButton,
    ModalBody,
    ModalFooter,
    Menu,
    MenuItem,
    MenuButton,
    MenuList,
    CardHeader,
    Flex,
    Box,
    Center
} from '@chakra-ui/react';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { MdDriveFileRenameOutline, MdMoreHoriz, MdOutlineDelete, MdOutlineFileDownload, MdOutlineImage, MdRefresh } from 'react-icons/md';
import { SensorCard } from './api';
import { RenameCardForm, generateQuery } from './Form';

// eslint-disable-next-line @typescript-eslint/naming-convention
function SensorCardElement(props: {
    usb?: string, onRefresh: () => void, host: string,
} & SensorCard) {
    const date = useMemo(() => (
        new Date(Date.parse(props.acquisition_time))).toLocaleString(),
        [props.acquisition_time]
    );

    const previewImageSrcs = useMemo(() => {
        const out = [];
        for (let i = 0; i < props.num_images; i++) {
            out.push(`http://${props.host}/system/card/view?${generateQuery({
                path: props.usb,
                subdir: props.subdir_path,
                img: i,
                encoding: props.image_format
            })}`);
        }

        return out;
    }, [props.num_images, props.subdir_path, props.usb, props.image_format]);

    const [preview, setPreview] = useState<string>();

    const [isLoading, setIsLoading] = useState<boolean>(false);

    const previewDisclosure = useDisclosure();
    const renameDisclosure = useDisclosure();

    const deleteDisclosure = useDisclosure();
    const cancelDelete = useRef<any>();
    const toast = useToast();

    useEffect(() => {
        if (props.usb) {
            // Fetch a single preview node
            setIsLoading(true);
            fetch(`http://${props.host}/system/card/view?${generateQuery({
                path: props.usb,
                subdir: props.subdir_path,
                img: 0,
                encoding: props.image_format
            })}`).then(async (res) => {
                setPreview(URL.createObjectURL(await res.blob()));
            }).finally(() => {
                setIsLoading(false);
            });
        }
    }, [props.acquisition_time, props.subdir_path, props.image_format, props.usb, props.host]);

    const onDelete = useCallback(() => {
        fetch(`http://${props.host}/system/card/delete?${generateQuery({
            path: props.usb,
            subdir: props.subdir_path
        })}`).then(async (res) => {
            if (res.ok) {
                toast({
                    title: `Deleted ${props.card_id}`,
                    status: "success"
                });
            } else {
                toast({
                    title: `Failed to delete ${props.card_id}`,
                    description: await res.text(),
                    status: "error"
                });
            }

            props.onRefresh();
        }).catch(res => {
            toast({
                title: `Failed to delete ${props.card_id}`,
                description: res,
                status: "error"
            });
        });

        deleteDisclosure.onClose();
    }, [props.usb, props.onRefresh, props.host, props.subdir_path, props.card_id]);

    return (
        <Card>
            <AlertDialog
                isOpen={deleteDisclosure.isOpen}
                leastDestructiveRef={cancelDelete}
                onClose={deleteDisclosure.onClose}
            >
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize='lg' fontWeight='bold'>
                            Delete Images
                        </AlertDialogHeader>

                        <AlertDialogBody>
                            Are you sure? You can't undo this action afterwards.
                        </AlertDialogBody>

                        <AlertDialogFooter>
                            <Button ref={cancelDelete} onClick={deleteDisclosure.onClose}>
                                Cancel
                            </Button>
                            <Button colorScheme='red' onClick={onDelete} ml={3}>
                                Delete
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>

            <Modal size="4xl" isOpen={previewDisclosure.isOpen} onClose={previewDisclosure.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>{props.card_id}</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <SimpleGrid columns={3} spacing={2}>
                            {
                                previewDisclosure.isOpen && previewImageSrcs.map(v => <Image src={v} />)
                            }
                        </SimpleGrid>
                    </ModalBody>
                    <ModalFooter>
                    </ModalFooter>
                </ModalContent>
            </Modal>

            <Modal isOpen={renameDisclosure.isOpen} onClose={renameDisclosure.onClose}>
                <ModalOverlay />
                <ModalContent>
                    <ModalHeader>Change Card ID</ModalHeader>
                    <ModalCloseButton />
                    <ModalBody>
                        <RenameCardForm
                            onClose={renameDisclosure.onClose}
                            onFinally={props.onRefresh}
                            host={props.host}
                            subdir={props.subdir_path}
                            usb={props.usb}
                            cardId={props.card_id}
                        />
                    </ModalBody>
                    <ModalFooter />
                </ModalContent>
            </Modal>

            <CardHeader>
                <Flex>
                    <Flex flex='1' gap='4' alignItems='center' flexWrap='wrap'>
                        <Box>
                            <Heading size='sm'>{props.card_id}</Heading>
                            <Text fontSize="sm">{date}</Text>
                        </Box>
                    </Flex>
                    <Menu>
                        <MenuButton
                            as={IconButton}
                            aria-label='Options'
                            icon={<MdMoreHoriz />}
                            variant='outline'
                            fontSize="xl"
                            size="sm"
                        />
                        <MenuList>
                            <MenuItem icon={<MdOutlineImage />} onClick={previewDisclosure.onOpen}>
                                View
                            </MenuItem>
                            <MenuItem icon={<MdOutlineFileDownload />}>
                                Download ZIP
                            </MenuItem>
                            <MenuDivider />
                            <MenuItem icon={<MdDriveFileRenameOutline />} onClick={renameDisclosure.onOpen}>
                                Rename
                            </MenuItem>
                            <MenuItem icon={<MdOutlineDelete />} onClick={deleteDisclosure.onOpen}>
                                Delete
                            </MenuItem>
                        </MenuList>
                    </Menu>
                </Flex>
            </CardHeader>

            {
                (preview && !isLoading) ? <Image src={preview} /> : <Center py={4}><Spinner /></Center>
            }
        </Card>
    );
}

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function View(props: { usb?: string; refresh: number, host: string }) {
    const [cards, setCards] = useState<SensorCard[]>([]);
    const toast = useToast();

    const onRefresh = useCallback(async () => {
        const response = await fetch(`http://${props.host}/system/cards?path=${props.usb}`);

        if (response.ok) {
            // Place the newest images first
            setCards((await response.json()).reverse());
        } else {
            toast({
                title: "Failed to refresh sensor card listings",
                description: await response.text(),
                status: "error"
            });
        }
    }, [props.host, props.usb]);

    useEffect(() => {
        if (props.usb) {
            onRefresh();
        }
    }, [props.usb, props.refresh, props.host]);

    return (
        <VStack align="stretch">
            <Stack direction='row' spacing={4} align='center' justify='center'>
                <Text>Imaged Sensor Cards <Badge colorScheme='purple'>{cards.length}</Badge></Text>
                <IconButton
                    onClick={onRefresh}
                    isDisabled={props.usb === undefined}
                    aria-label='Refresh'
                    fontSize='20px'
                    icon={<MdRefresh />}
                />
            </Stack>
            <SimpleGrid columns={3} spacing={2}>
                {
                    cards.map((c) => (
                        <SensorCardElement onRefresh={onRefresh} key={c.subdir_path} usb={props.usb} host={props.host} {...c} />
                    ))
                }
            </SimpleGrid>
        </VStack>
    );
}
