type DataRefreshHandler = () => void;

const handlers = new Set<DataRefreshHandler>();

/** 管理端刷新成功后递增。未挂载的页面下次进入据此判断缓存已过期。 */
let refreshEpoch = 0;

export function getDataRefreshEpoch(): number {
  return refreshEpoch;
}

export function emitDataRefresh() {
  refreshEpoch += 1;
  handlers.forEach((handler) => handler());
}

export function onDataRefresh(handler: DataRefreshHandler) {
  handlers.add(handler);
}

export function offDataRefresh(handler: DataRefreshHandler) {
  handlers.delete(handler);
}
