import { useMemo } from 'react';

import { Text } from '@chakra-ui/react';

import Form from '@rjsf/chakra-ui';
import validator from '@rjsf/validator-ajv8';

import { generateRjsfSchema } from './Form';

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function SettingsForm(props: { path: string, value: any, setValue: any, schema: any, propertyFilterOut?: string[] }) {
    const schema = useMemo(() => {
        return generateRjsfSchema(props.schema?.paths[props.path]?.post, props.propertyFilterOut);
    }, [props.path, props.schema, props.propertyFilterOut]);

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
        <Form
            formData={props.value}
            onChange={e => props.setValue(e.formData)}
            schema={schema}
            validator={validator}>
            <div></div>
        </Form>
    );
}