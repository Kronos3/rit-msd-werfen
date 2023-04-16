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
    useToast
} from '@chakra-ui/react';

import { useCallback, useEffect, useState } from 'react';
import { MdRefresh } from 'react-icons/md';
import { SensorCard } from './api';

// eslint-disable-next-line @typescript-eslint/naming-convention
function SensorCardElement(props: { sensor: SensorCard }) {
    useEffect(() => {

    }, [props.sensor]);

    return (
        <Card maxW='sm'>
            <CardBody>
                <Image
                    src='https://images.unsplash.com/photo-1555041469-a586c61ea9bc?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80'
                    alt='Green double couch with wooden legs'
                    borderRadius='lg'
                />
                <Heading size='md'>{props.sensor.card_id}</Heading>
            </CardBody>
            <Divider />
            <CardFooter>
                <ButtonGroup spacing='2'>
                    <Button variant='solid' colorScheme='blue'>
                        Download Zip
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
                <Text>Imaged Sensor Cards</Text>
                <IconButton
                    onClick={onRefresh}
                    isDisabled={props.usb === undefined}
                    aria-label='Refresh'
                    fontSize='20px'
                    icon={<MdRefresh />}
                />
            </Stack>
            <SimpleGrid columns={4} spacing={2}>
                {
                    cards.map(c => (
                        <SensorCardElement sensor={c} />
                    ))
                }
            </SimpleGrid>
        </VStack>
    );
}
