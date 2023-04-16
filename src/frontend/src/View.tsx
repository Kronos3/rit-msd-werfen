import {
    Stack,
    IconButton,
    Text,
    VStack,
    SimpleGrid,
    Card,
    CardBody,
    Image,
    Heading,
    Divider,
    CardFooter,
    ButtonGroup,
    Button,
    useToast,
    Badge,
    Spinner
} from '@chakra-ui/react';

import { useCallback, useEffect, useState } from 'react';
import { MdRefresh } from 'react-icons/md';
import { SensorCard } from './api';
import { generateQuery } from './Form';

// eslint-disable-next-line @typescript-eslint/naming-convention
function SensorCardElement(props: { usb?: string, host: string, sensor: SensorCard }) {
    const [date, setDate] = useState<string>();
    const [preview, setPreview] = useState<string>();

    useEffect(() => {
        const d = new Date(Date.parse(props.sensor.acquisition_time));
        setDate(d.toLocaleString());

        if (props.usb) {
            // Fetch a single preview node
            fetch(`http://${props.host}/system/card/view?${generateQuery({
                path: props.usb,
                subdir: props.sensor.subdir_path,
                img: 0,
                encoding: props.sensor.image_format
            })}`).then(async (res) => {
                setPreview(URL.createObjectURL(await res.blob()));
            });
        }
    }, [props.sensor, props.usb, props.host]);

    return (
        <Card maxW='sm'>
            <CardBody>
                {
                    preview ? <Image
                        src={preview}
                        borderRadius='lg'
                    /> : <Spinner />
                }
                <Heading size='md'>{props.sensor.card_id}</Heading>
                <Text color='blue.600' fontSize='sm'>
                    {date}
                </Text>
            </CardBody>
            <Divider />
            <CardFooter>
                <ButtonGroup spacing='2'>
                    <Button variant='solid' colorScheme='blue'>
                        View
                    </Button>
                    <Button variant='ghost' colorScheme='blue'>
                        Delete
                    </Button>
                </ButtonGroup>
            </CardFooter>
        </Card>
    );
}

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function View(props: { usb?: string; host: string }) {
    const [cards, setCards] = useState<SensorCard[]>([]);
    const toast = useToast();

    const onRefresh = useCallback(async () => {
        const response = await fetch(`http://${props.host}/system/cards?path=${props.usb}`);

        if (response.ok) {
            setCards(await response.json());
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
    }, [props.usb, props.host]);

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
                    cards.map((c, i) => (
                        <SensorCardElement key={i} usb={props.usb} host={props.host} sensor={c} />
                    ))
                }
            </SimpleGrid>
        </VStack>
    );
}
