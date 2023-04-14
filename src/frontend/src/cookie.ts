export function set(name: string, val?: string) {
    const date = new Date();

    if (val === undefined) {
        return;
    }

    const value = val;

    // Set it expire in 7 days
    date.setTime(date.getTime() + (7 * 24 * 60 * 60 * 1000));

    // Set it
    document.cookie = name + "=" + value + "; expires=" + date.toUTCString() + "; path=/";
}

export function get(name: string) {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");

    if (parts && parts.length === 2) {
        return parts.pop()!.split(";").shift();
    }
}

export function getJson<T = unknown>(name: string) {
    const out = get(name);
    try {
        return out === undefined ? undefined : JSON.parse(out) as T;
    } catch(e) {
        console.error("Failed to parse", name, out, e);
        return undefined;
    }
}
