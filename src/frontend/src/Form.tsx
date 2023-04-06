import { useCallback, useEffect, useState } from 'react';

import { Text } from '@chakra-ui/react'

import schemaGenerator from 'openapi-schema-to-json-schema'

import Form from '@rjsf/chakra-ui';
import validator from '@rjsf/validator-ajv8';

function generateRjsfSchema(schema?: any) {
    if (!schema) {
        return;
    }

    const properties: any = {};
    if (schema.parameters) {
        for (const param of schema.parameters) {
            properties[param.name] = schemaGenerator(param.schema);
        }
    }

    return {
        type: "object",
        properties: properties,
        required: Object.keys(properties)
    } as any
}

function generateQuery(params: any): string {
    return Object.keys(params).map(key => key + '=' + params[key]).join('&');
}

export default function ApiForm(props: { host: string, path: string, schema: any, onReply?: (response: Response) => void }) {
    const [schema, setSchema] = useState();
    const [disabled, setDisabled] = useState(false);
    const [value, setValue] = useState();

    useEffect(() => {
        setSchema(generateRjsfSchema(props.schema?.paths[props.path]?.post));
    }, [props.path, props.schema]);

    const submit = useCallback((data: { formData?: any }) => {
        (async (formProp) => {
            // Merge parameters into query
            setDisabled(true);

            const query = generateQuery(formProp.formData);
            const response = await fetch(`http://${props.host}${props.path}?${query}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
            });
    
            setDisabled(false);

            props.onReply?.(response);
        })(data)
    }, [props]);

    if (!schema) {
        return <Text>Non-post requests are not supported</Text>
    }

    return <Form
        formData={value}
        onChange={e => setValue(e.formData)}
        disabled={disabled}
        schema={schema}
        validator={validator}
        onSubmit={submit} />
}
