import { useEffect, useState } from 'react';

import { Text } from '@chakra-ui/react';

import Form from '@rjsf/chakra-ui';
import validator from '@rjsf/validator-ajv8';

import { generateRjsfSchema } from './Form';

export default function SettingsForm(props: { path: string, value: any, setValue: any, schema: any, }) {
    const [schema, setSchema] = useState();

    useEffect(() => {
        setSchema(generateRjsfSchema(props.schema?.paths[props.path]?.post));
    }, [props.path, props.schema]);

    if (!props.schema) {
        return <Text>Failed to fetch API schema from Middleware</Text>
    }
    else if (!props.schema?.paths[props.path]) {
        return <Text>Middleware does not serve API for '{props.path}'</Text>
    }
    else if (!schema) {
        return <Text>Non-post requests are not supported: {props.path}</Text>
    }

    return (
        <Form
            formData={props.value}
            onChange={e => props.setValue(e.formData)}
            schema={schema}
            validator={validator}>
            <div></div>
        </Form>
    );
}