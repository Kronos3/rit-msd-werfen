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
    Button
} from '@chakra-ui/react';

import { useCallback, useEffect, useState } from 'react';
import { MdRefresh } from 'react-icons/md';
import { SensorCard } from './api';

function SensorCardElement(props: { sensor: SensorCard }) {
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
                        Buy now
                    </Button>
                    <Button variant='ghost' colorScheme='blue'>
                        Add to cart
                    </Button>
                </ButtonGroup>
            </CardFooter>
        </Card>
    )
}

export default function ViewMode(props: { usb?: string; host: string }) {
    const [cards, setCards] = useState<SensorCard[]>([]);

    const onRefresh = useCallback(() => {
        if (props.usb) {
            fetch(`/system/cards?path=${props.usb}`).then(async (v) => {
                setCards(await v.json());
            });
        }
    }, [props.host, props.usb]);

    useEffect(() => onRefresh(), [props.host]);

    return (
        <VStack align="stretch">
            <Stack direction='row' spacing={4} align='center' justify='center'>
                <Text>Imaged Sensor Cards</Text>
                <IconButton
                    onClick={onRefresh}
                    aria-label='Refresh'
                    fontSize='20px'
                    icon={<MdRefresh />}
                />
            </Stack>
            <SimpleGrid columns={4} spacing={2}>

            </SimpleGrid>
        </VStack>
    )
}