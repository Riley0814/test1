export const delivery = {
  arrived: {
    css: 'status_white',
    ch: '已到達',
  },
  shipped: {
    css: 'status_white',
    ch: '已發貨',
  },
  handling: {
    css: 'status_green',
    ch: '處理中',
  },
  pending: {
    css: 'status_yellow',
    ch: '備貨中',
  },
  cancel: {
    css: 'status_gray',
    ch: '已取消',
  },
  return: {
    css: 'status_blue',
    ch: '已退貨',
  },
};

export const pay = {
  paid: {
    css: 'status_green',
    ch: '已付款',
  },
  unpaid: {
    css: 'status_yellow',
    ch: '未付款',
  },
  cancel: {
    css: 'status_gray',
    ch: '已取消',
  },
  refund: {
    css: 'status_blue',
    ch: '已退款',
  },
};

export const order = {
  complete: {
    css: 'status_white',
    ch: '已完成',
  },
  handling: {
    css: 'status_green',
    ch: '處理中',
  },
  pending: {
    css: 'status_yellow',
    ch: '待確定',
  },
  cancel: {
    css: 'status_gray',
    ch: '已取消',
  },
};

export const warning = {
  css: 'status_warning',
  ch: '狀態尚未配對',
};
