import { useCallback, useEffect, useMemo, useState } from 'react';
import { VStack, Text, useToast } from '@chakra-ui/react';
import schemaGenerator from 'openapi-schema-to-json-schema';

import Form from '@rjsf/chakra-ui';
import validator from '@rjsf/validator-ajv8';
import { CardIdResponse } from './api';

export function generateRjsfSchema(schema?: any, propertyFilterOut?: string[]) {
    if (!schema) {
        return;
    }

    const properties: any = {};
    if (schema.parameters) {
        for (const param of schema.parameters) {
            if (propertyFilterOut && propertyFilterOut.indexOf(param.name) !== -1) {
                continue;
            }

            properties[param.name] = schemaGenerator(param.schema);
        }
    }

    return {
        type: "object",
        properties: properties,
        required: Object.keys(properties)
    } as any;
}

export function generateQuery(params: any): string {
    return Object.keys(params).map(key => key + '=' + params[key]).join('&');
}

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function ApiForm(props: { host: string, path: string, schema: any, onReply?: (response: Response) => void }) {
    const [disabled, setDisabled] = useState(false);
    const [value, setValue] = useState();

    const [error, setError] = useState("");
    const [output, setOutput] = useState("");

    const schema = useMemo(
        () => generateRjsfSchema(props.schema?.paths[props.path]?.post),
        [props.schema, props.path]
    );

    const submit = useCallback((data: { formData?: any }) => {
        (async (formProp) => {
            // Merge parameters into query
            setDisabled(true);
            setError("");

            const query = generateQuery(formProp.formData);
            const response = await fetch(`http://${props.host}${props.path}?${query}`, {
                method: "POST",
                // eslint-disable-next-line @typescript-eslint/naming-convention
                headers: { "Content-Type": "application/json" },
            });

            setDisabled(false);

            if (!response.ok) {
                setError(await response.text());
                return;
            }

            if (props.onReply) {
                props.onReply(response);
            } else {
                setOutput(await response.text());
            }
        })(data);
    }, [props]);

    if (!props.schema) {
        return <Text>Failed to fetch API schema from Middleware</Text>;
    }
    else if (!props.schema?.paths[props.path]) {
        return <Text>Middleware does not serve API for '{props.path}'</Text>;
    }
    else if (!schema) {
        return <Text>Non-post requests are not supported: {props.path}</Text>;
    }

    return (
        <VStack align='stretch'>
            <Form
                formData={value}
                onChange={e => setValue(e.formData)}
                disabled={disabled}
                schema={schema}
                validator={validator}
                onSubmit={submit} />
            <Text>{error}</Text>
            <Text>{output}</Text>
        </VStack>
    );
}

// eslint-disable-next-line @typescript-eslint/naming-convention
export function RenameCardForm(props: {
    onClose: () => void,
    onReply?: (reply: CardIdResponse) => void,
    onFinally: () => void,
    host: string,
    usb?: string,
    subdir: string,
    cardId: string,
}) {
    const toast = useToast();
    const [formValue, setFormValue] = useState(props.cardId);

    useEffect(() => {
        setFormValue(props.cardId);
    }, [props.cardId]);

    return (
        <Form
            formData={formValue}
            onChange={e => setFormValue(e.formData)}
            schema={{ type: "string" }}
            validator={validator}
            onSubmit={(e) => {
                props.onClose();

                const query = generateQuery({
                    // eslint-disable-next-line @typescript-eslint/naming-convention
                    to_id: e.formData,
                    subdir: props.subdir,
                    path: props.usb
                });

                fetch(`http://${props.host}/system/rename?${query}`, {
                    method: "POST",
                    // eslint-disable-next-line @typescript-eslint/naming-convention
                    headers: { "Content-Type": "application/json" },
                }).then(async (response) => {
                    if (response.ok) {
                        props.onReply?.(await response.json());
                        toast({
                            title: `Renamed card ID to ${e.formData}`,
                            status: "success"
                        });
                    } else {
                        toast({
                            title: "Failed to rename card ID",
                            description: await response.text(),
                            status: "error"
                        });
                    }
                }).catch((e) => {
                    toast({
                        title: "Failed to rename card ID",
                        description: e,
                        status: "error"
                    });
                }).finally(props.onFinally);
            }}
        />
    );
}
