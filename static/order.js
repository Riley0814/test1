// 引入假資料
/**
 * 替換API "對應訂單數量"
 * # 依照當前 showListNum 、 currentShowPage 來決定回傳多少資料
 * # ex.
 * 當前第1頁 currentShowPage = 1
 * 使用者顯示訂單數 showListNum = 24
 */
import * as data from './../../fakeOrderDB.json' with { type: 'json' };
let orderDatas = data.default;

/**
 * 顯示列數
 * * 12, 24, 48, 100
 */
const showOption = [12, 24, 48, 100];

/**
 * 列數預設值
 * * 12
 */
let showListNum = showOption[0];

/**
 * 分頁顯示頁數
 */
const paginationShowLength = 5;

/**
 * 分頁預設值
 * * 1
 */
let currentShowPage = 1;

/**
 * 分頁顯示頁數
 */
let select = 1;

/**
 * 替換API "訂單總數量"
 * * 直接回傳總共多少筆
 * * ex. 200
 */
const orderDataLength = orderDatas.length;

/**
 * 依條件過濾後的訂單列
 */
let showOrderList;
let orderList = [];

// pagination
/**
 * 創建頁碼
 */
function paginationCreate() {
  let html = '';

  const currentOrderList =
    orderList.length != 0 ? orderList.length : orderDataLength;
  const pages = Math.ceil(currentOrderList / showListNum);
  const paginationDOM = document.querySelector('#pagination ul');
  const numbers = Array.from({ length: pages }, (v, k) => k + 1);
  const leng = Math.ceil(pages / paginationShowLength);
  let paginationArray = [];


  for (let i = 0; i < leng; i++) {
    paginationArray.push([...numbers.splice(0, paginationShowLength)]);
  }

  // 如有，加入往前的分頁按鈕
  if (paginationArray.length <= select) html += `<button id="pre">pre</button>`;


  for (let i = 1; i <= paginationArray[select - 1].length; i++) {
    const num = paginationArray[select - 1][i - 1];
    html += `<li class="${
      currentShowPage === num ? 'current' : ''
    }" data-num="${num}">${num}</li>`;
  }

   // 如有，加入往後的分頁按鈕
  if (paginationArray.length > select)
    html += `<button id="next">next</button>`;



  paginationDOM.innerHTML = html;

  clickme();
}

function clickme() {
  const next = document.getElementById('next');
  const pre = document.getElementById('pre');
  if (next)
    next.addEventListener('click', () => {
      currentShowPage = paginationShowLength * select + 1;
      select += 1;
      paginationCreate();
      orderDOM();
      mainToTop();
    });
  if (pre)
    pre.addEventListener('click', () => {
      select -= 1;
      currentShowPage = paginationShowLength * select;
      paginationCreate();
      orderDOM();
      mainToTop();
    });
}

/**
 * 監聽點擊頁碼切換頁面
 */
function switchPageListen(orderList = null) {
  const lis = document.querySelectorAll('#pagination li');
  lis.forEach((el) => {
    el.addEventListener('click', () => {
      paginationSwitch(el.getAttribute('data-num'));
    });
  });

  function paginationSwitch(num) {
    // 當前頁碼更新為點擊頁碼
    currentShowPage = Number(num);
    // 刷新資料內容
    orderDOM();
    mainToTop();
  }
}

/**
 * 回到底部
 */
function mainToTop() {
  const _main_content = document.getElementById('_main_content');
  _main_content.scrollTo({ top: 0, behavior: 'smooth' });
}

// selectOption.
function selectOptionCreate() {
  let html = '';

  const select = document.querySelector('#order_controller #showListOption');

  for (let i = 0; i < showOption.length; i++) {
    const element = showOption[i];
    const opt = new Option(`${element}筆`, element);
    select.options.add(opt);
  }
}

function selectOptionClick() {
  const select = document.querySelector('#order_controller #showListOption');
  select.addEventListener('change', (el) => {
    showListNum = Number(el.target.value);
    currentShowPage = 1;
    orderDOM();
  });
}

/**
 * 建立訂單列
 */
function orderDOM() {
  // 依照 showListNum、currentShowPage  切出的訂單陣列
  const sliceData = orderDatas.slice(
    currentShowPage * showListNum - showListNum,
    currentShowPage * showListNum
  );
  // 如果Data沒給值，就使用sliceData
  showOrderList = orderList.length != 0 ? orderList : sliceData;

  const orderContainer = document.querySelector('#orderContent .items');
  let html = '';

  showOrderList.forEach((el) => {
    const status = checkStatus(el);
    const date = new Date(el.orderDate);
    el.date = `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;

    html += `
    <div class="row">
      <div class="th w20 link">
        <a href="orderDetail.html?id=${el.orderId}">${el.orderId}</a>
      </div>
      <div class="th w10 ">${el.date}</div>
      <div class="th w10 ">
        <span class="_status ${status.order.css}">
          ${status.order.ch}
        </span>
      </div>
      <div class="th w10 ">
        <span class="_status ${status.pay.css}">
          ${status.pay.ch}
        </span>
      </div>
      <div class="th w10 ">
        <span class="_status ${status.delivery.css}">
          ${status.delivery.ch}
          </span>
        </div>
      <div class="th w20">
        <div>
          <strong>${el.subscriber.username}</strong>
          <p class="email">${el.email}</p>
        </div>
      </div>
      <div class="th w10 "><p>$${el.totalPrice}</p></div>
    </div>
    `;
  });

  orderContainer.innerHTML = html;

  paginationCreate();
  switchPageListen();
}

function checkStatus(el) {
  let order = {},
    pay = {},
    delivery = {};

  switch (el.delivery.status.toLowerCase()) {
    case 'arrived':
      delivery['css'] = 'status_white';
      delivery['ch'] = '已到達';
      break;
    case 'shipped':
      delivery['css'] = 'status_white';
      delivery['ch'] = '已發貨';
      break;
    case 'handling':
      delivery['css'] = 'status_green';
      delivery['ch'] = '處理中';
      break;
    case 'pending':
      delivery['css'] = 'status_yellow';
      delivery['ch'] = '備貨中';
      break;
    case 'cancel':
      delivery['css'] = 'status_gray';
      delivery['ch'] = '已取消';
      break;
    case 'return':
      delivery['css'] = 'status_blue';
      delivery['ch'] = '已退貨';
      break;
    default:
      delivery['css'] = 'status_warning';
      delivery['ch'] = '狀態尚未配對';
      break;
  }

  switch (el.orderStatus.toLowerCase()) {
    case 'complete':
      order['css'] = 'status_white';
      order['ch'] = '已完成';
      break;
    case 'handling':
      order['css'] = 'status_green';
      order['ch'] = '處理中';
      break;
    case 'pending':
      order['css'] = 'status_yellow';
      order['ch'] = '待確定';
      break;
    case 'cancel':
      order['css'] = 'status_gray';
      order['ch'] = '已取消';
      break;
    default:
      order['css'] = 'status_warning';
      order['ch'] = '狀態尚未配對';
      break;
  }

  switch (el.pay.status.toLowerCase()) {
    case 'paid':
      pay['css'] = 'status_green';
      pay['ch'] = '已付款';
      break;
    case 'unpaid':
      pay['css'] = 'status_yellow';
      pay['ch'] = '未付款';
      break;
    case 'cancel':
      pay['css'] = 'status_gray';
      pay['ch'] = '已取消';
      break;
    case 'refund':
      pay['css'] = 'status_blue';
      pay['ch'] = '已退款';
      break;
    default:
      pay['css'] = 'status_warning';
      pay['ch'] = '狀態尚未配對';
      break;
  }

  return { order, pay, delivery };
}

/**
 * 替換API "搜尋對應條件"
 */
function search({ target, text }) {
  for (let [key, value] of Object.entries(orderDatas)) {
    switch (target) {
      case 'id':
        if (value.orderId.match(text)) orderList.push(value);
        break;
      case 'phone':
        if (value.phoneNum.match(text)) orderList.push(value);
        break;
      case 'email':
        if (value.email.match(text)) orderList.push(value);
        break;
      case 'name':
        if (value.name.match(text)) orderList.push(value);
        break;
    }
  }
  orderDOM();
}

/**
 * Search
 */
function searchBtnListen() {
  const searchBtn = document.querySelector('#search_btn');
  const textDOM = document.querySelector('#search_order');

  searchBtn.addEventListener('click', listen);
  textDOM.addEventListener('keyup', (event) => {
    if (event.keyCode === 13) listen();
  });

  function listen() {
    const text = String(textDOM.value).trim();
    const targetDOM = document.querySelector('#search_targt');
    const target = targetDOM.value;
    orderList = [];
    if (text != '' && target != '') {
      search({ target, text });
    }
    if (text === '') orderDOM();
  }
}

const order = () => {
  orderDOM();
  selectOptionClick();
  selectOptionCreate();
  searchBtnListen();
};

export { order };
