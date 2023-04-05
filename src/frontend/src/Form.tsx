import React from 'react';

import { Text } from '@chakra-ui/react'
import { ApiProps } from './common';

import schemaGenerator from 'openapi-schema-to-json-schema'

import Form from '@rjsf/chakra-ui';
import validator from '@rjsf/validator-ajv8';

function generateRjsfSchema(schema: any) {
    const properties: any = {};
    for (const param of schema.parameters) {
        properties[param.name] = schemaGenerator(param.schema);
    }

    return {
        type: "object",
        properties: properties
    } as any
}

export default function ApiForm(props: ApiProps & { path: string, schema: any, onReply?: (response: Response) => void }) {
    const schema = props.schema?.paths[props.path]?.post;
    if (!schema) {
        return <Text>Non-post requests are not supported</Text>
    }

    return <Form schema={generateRjsfSchema(schema)} validator={validator} onSubmit={async (formProp) => {
        // Merge parameters into 
        const response = await fetch(`http://${props.address}:${props.port}${props.path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formProp.formData)
        });

        props.onReply?.(response);
    }} />
}
