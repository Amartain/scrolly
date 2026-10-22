import { json, send, type View } from './api';

/** Tribulation Weathered was read and closed: it does not come again until another conquest. */
export const victorySeen = () => send<View>('/api/trials/victory-seen', json('POST'));
