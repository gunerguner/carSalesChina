type DataRefreshHandler = () => void;

const handlers = new Set<DataRefreshHandler>();
const DATA_REFRESH_EVENT = 'DATA_REFRESH';

export function emitDataRefresh() {
  handlers.forEach((handler) => handler());
}

export function onDataRefresh(handler: DataRefreshHandler) {
  handlers.add(handler);
}

export function offDataRefresh(handler: DataRefreshHandler) {
  handlers.delete(handler);
}

export { DATA_REFRESH_EVENT };
