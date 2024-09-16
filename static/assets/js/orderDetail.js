// 引入假資料，測試用
import * as data from './../../fakeOrderDB.json' with { type: 'json' };
import * as statusHandler from './statusValueHandler.js';

console.log(data.default);
let currentOrderData;
getCurrentOrderData();

function reDate(date) {
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
}

/**
 * 獲取當前location query id
 */
function getUrlParameter(name) {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  var results = regex.exec(location.search);

  return results === null
    ? false
    : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

/**
 * 替換API "依訂單號之Data"
 */
function getCurrentOrderData() {
  const pathId = getUrlParameter('id');

  if (!pathId) window.location.href = '/pages/orders.html';
  else {
    for (let [key, value] of Object.entries(data.default)) {
      if (value.orderId === pathId) currentOrderData = value;
    }
  }
}

/**
 * 建立訂單資料
 */
function createStatusContent() {
  const box = document.getElementById('_order_status');
  let html = '';

  // 轉換日期格式
  const date = new Date(currentOrderData.orderDate);
  currentOrderData.orderDate = reDate(date);

  const status = currentOrderData.orderStatus.toLowerCase();
  const matchStatus = eachLsitStatus('order', status);
  const statusCSS = matchStatus.css;
  const statusCh = matchStatus.ch;

  html = `
    ${selectContent('order')}
    <div class="content">
      <div class="box">
        <p>訂單狀態</p>
        <span id="_order_status_text" class="_status ${statusCSS}">${statusCh}</span>
      </div>
      <div class="box">
        <p>訂單號碼</p>
        <span>${currentOrderData.orderId}</span>
      </div>
      <div class="box">
        <p>訂單日期</p>
        <span>${currentOrderData.orderDate}</span>
      </div>
      <div class="box">
        <p>訂購人姓名</p>
        <span>${currentOrderData.subscriber.username}</span>
      </div>
      <div class="box">
        <p>訂購人電話</p>
        <span>${currentOrderData.subscriber.phoneNumber}</span>
      </div>
      <div class="box">
        <p>訂購人郵件</p>
        <span>${currentOrderData.email}</span>
      </div>
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
  selectBind('order', (callback) => {
    updatedStatus('order', callback, '_order_status_text');
  });
}

/**
 * 建立付款資料
 */
function createPayStatusContent() {
  const box = document.getElementById('_pay_status');
  let html = '';

  // 轉換日期格式
  const date = new Date(currentOrderData.pay.date);
  currentOrderData.pay.date = reDate(date);

  const values = statusValHandler('pay');
  const statusCSS = values.statusCSS;
  const statusCh = values.statusCh;

  html = `
    ${selectContent('pay',true)}
    <div class="content">
      <div class="box">
        <p>付款狀態</p>
        <span id="_pay_status_text" class="_status ${statusCSS}" >${statusCh}</span>
      </div>
      <div class="box items">
        <p>付款日期</p>
        <span>${currentOrderData.pay.date}</span>
      </div>
      <div class="box items">
        <p>付款帳號</p>
        <span>${currentOrderData.pay.account}</span>
      </div>
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
  selectBind('pay', (callback) => {
    updatedStatus('pay', callback, '_pay_status_text');
  });
  editorHandler('pay');
}

/**
 * 建立詳情資料
 */
function createOrderDetailsContent() {
  const box = document.getElementById('_order_product');
  let html = '';
  let htmlInner = '';

  const orders = currentOrderData.orders;

  orders.forEach((el) => {
    const options = loopOption(el.option);
    const pricet = Number(el.num) * Number(el.price);

    htmlInner += `
    <div class="box">
      <div class="prodect flex">
        <div class="flex_left">
          <img src="${el.img}"/>
        </div>
        <div class="flex_right">
          <div class="tag">
            <p>${el.storeId}</p>
          </div>
          <div class="title">
            <p>${el.name}</p>
          </div>
          <div class="option light">
            <p>${options}</p>
          </div>
          <div class="light">
            <p>${el.num} x ${el.price} = NT$${pricet}</p>
          </div>
        </div>
      </div>
    </div>
    `;
  });

  const descount = `
  <div class="mx-10">
      <div>
        <p>折扣</p>
      </div>
      <div class="pl-10">
        <div class="flex between mt-5">
          <div>
            <p>優惠名稱</p>
          </div>
          <div class="center  flex price">
            <p>- NT$${currentOrderData.totalPrice}</p>
          </div>
        </div>
      </div>
      </div>
  `;
  const delivery = `

    <div class="flex between mx-10">
      <div>
        <p>運費</p>
      </div>
      <div class="center  flex price">
        <p>NT$${currentOrderData.delivery.fee}</p>
      </div>
    </div>
  
  `;
  const totalPrice = `
  <div class="flex between mx-10">
    <div>
      <p>商品小計</p>
    </div>
    <div class="center  flex price">
      <p>NT$${currentOrderData.totalPrice}</p>
    </div>
  </div>
  `;

  html = `
    <div class="title space">
      <h2>
        商品詳情
      </h2>
    </div>
    <div class="content img_content space">
      ${htmlInner}
    </div>
    <div class="content box_indent">
      <div class="box flex title between">
        <div>
          <p>訂單合計</p>
        </div>
        <div class="center  price">
          <p>NT$${currentOrderData.totalPrice}</p>
        </div>
      </div>
      <div class="pl-5">
        ${totalPrice}
        ${descount}
        ${delivery}
      </div>
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
}

function loopOption(value) {
  const option = Object.keys(value);
  let html = '';
  for (let i = 0; i < option.length; i++) {
    const title = option[i];
    const element = value[title];
    html += `
      <p>${title}:<span>${element}</span></p>
    `;
  }
  return html;
}

function statusValHandler(el) {
  const status = currentOrderData[el].status.toLowerCase();
  const matchStatus = eachLsitStatus(el, status);
  const statusCSS = matchStatus.css;
  const statusCh = matchStatus.ch;

  return { status, matchStatus, statusCSS, statusCh };
}

/**
 * 建立配送資料
 */
function createDeliveryStatusContent() {
  const box = document.getElementById('_delivery_status');
  let html = '';

  // 轉換日期格式
  const date = new Date(currentOrderData.delivery.date);
  currentOrderData.delivery.date = reDate(date);

  const values = statusValHandler('delivery');
  const statusCSS = values.statusCSS;
  const statusCh = values.statusCh;

  html = `
    ${selectContent('delivery', true)}
    <div class="content">
      <div class="box">
        <p>配送狀態</p>
        <span id="_delivery_status_text" class="_status ${statusCSS}" >${statusCh}</span>
      </div>
      <div class="box items">
        <p>送達日期</p>
        <span>${currentOrderData.delivery.date}</span>
      </div>
      <div class="box items">
        <p>收件人</p>
        <span>${currentOrderData.recipient.username}</span>
      </div>
        <div class="box items">
        <p>收件人電話</p>
        <span>${currentOrderData.recipient.phoneNumber}</span>
      </div>
      <div class="box items">
        <p>收件人地址</p>
        <span>${currentOrderData.recipient.address}</span>
      </div>  
      <div class="box items">
        <p>配送單號</p>
        <span>${currentOrderData.delivery.trackCode}</span>
      </div>  
      <div class="box items link">
        <p>配送追蹤 / URL</p>
        <span>
          <a href="${currentOrderData.delivery.url}">
          ${currentOrderData.delivery.url}</a>
        </span>
      </div>  
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
  selectBind('delivery', (callback) => {
    updatedStatus('delivery', callback, '_delivery_status_text');
  });
  editorHandler('delivery');
}

//
//
// component
//
//

/**
 * Array透過過值找key
 */
function getKeyByValue(object, value) {
  return Object.keys(object).find((key) => object[key].ch === value);
}

/**
 * 更新欄位的狀態
 */
function updatedStatus(target, status, id) {
  const statusUpdate = getKeyByValue(statusHandler[target], status);
  const matchStatus = eachLsitStatus(target, statusUpdate);
  const statusCSS = matchStatus.css;
  const statusCh = matchStatus.ch;

  const dom = document.getElementById(id);
  dom.textContent = statusCh;
  dom.classList = `_status ${statusCSS}`;
}

/**
 * Select option
 *
 * @returns {html}
 */
function selectContent(el, editorOpen = false) {
  const selectList = {
    delivery: {
      title: '配送資料',
      optionDefault: '- 更改訂單配送狀態 -',
      option: ['備貨中', '處理中', '已發貨', '已到達', '已退貨', '已取消'],
    },
    order: {
      title: '訂單資料',
      optionDefault: '- 更改訂單狀態 -',
      option: ['待確定', '處理中', '已完成', '已取消'],
    },
    pay: {
      title: '付款資料',
      optionDefault: '- 更改付款狀態 -',
      option: ['未付款', '已付款', '已取消', '已退款'],
    },
  };

  const data = selectList[el];
  const editorOption = `
    <p id="_${el}_edit" class="edit">
      <i class="fa-solid fa-pen-to-square"></i>
    </p>
  `
  let options = '';
  data.option.forEach((el) => {
    options += `<option>${el}</option>`;
  });

  return `
  <div class="title flex space between">
    <div class="center flex">
      <h2>
        ${data.title}
      </h2>
      ${editorOpen? editorOption : ''}
    </div>
    <div class="box_indent">
      <select class="select" id="_${el}">
        <option value="${data.optionDefault}" selected disabled>${data.optionDefault}</option>
        ${options}
      </select>
    </div>
  </div>
  `;
}

function selectBind(target, callback) {
  const dom = document.getElementById(`_${target}`);
  dom.addEventListener('change', (el) => {
    const defaultVal = el.target.options[0].value;
    confirmBTN(defaultVal);
  });

  function confirmBTN(el) {
    let html = `
      <div class="top_level" id="confirm">
        <div class="top_level_box">
          <div class="mb-20 mt-10 text-center">
            確定要修改狀態嗎?
          </div>
          <div class="text-center ">
            <button class="submit">確定</button>
            <button class="cancel">取消</button>
          </div>
        </div>
      </div>
    `;

    document.querySelector('body').insertAdjacentHTML('afterbegin', html);

    const confirm = document.querySelector('#confirm');
    const submit = confirm.querySelector('.submit');
    const cancel = confirm.querySelector('.cancel');

    // 確認選擇
    const submitFun = () => {
      // @更換 SUBIT API
      callback(dom.value);
      confirm.remove();
      cancel.addEventListener('click', submitFun);
    };
    submit.addEventListener('click', submitFun);

    // 取消選擇
    const cancelFun = () => {
      dom.value = el;
      confirm.remove();
      cancel.removeEventListener('click', cancelFun);
    };
    cancel.addEventListener('click', cancelFun);
  }
}

/**
 * 編輯欄位
 * 
 * @param {String} target - type of status
 */
function editorHandler(target) {
  const dom = document.getElementById(`_${target}_edit`);
  const title = document.querySelector(`#_${target}_status .title h2`).textContent;

  if(!dom) return;

  dom.addEventListener('click', () => {
    editor(target, title);
  });
}

function editor(target, title) {
  const originVal = document.querySelectorAll(`#_${target}_status .content .box.items`);
  
  console.log(originVal);
  let innerHtml = '';

  // 取得原始輸出資料，轉為INPUT
  for (let i = 0; i < originVal.length; i++) {
    const element = originVal[i];
    const elClass = element.querySelector('span').classList;
    const elId = element.querySelector('span').id;
    const content = element.querySelector('span a') || element.querySelector('span')
    innerHtml += `
      <div class="box">
        ${element.querySelector('p').outerHTML}
        <input class="${elClass}" id="${elId}" value="${content.innerHTML.trim()}"/>
      </div>
    `;
  }

  const html = `
    <div class="border top_level" id="_content_editor">
      <div class="top_level_box">
        <div class="title">
          <p>${title}</p>
        </div>
        <div class="editor">
          ${innerHtml}
        </div>
        <div class="text-center">
          <button class="submit">確定</button>
          <button class="cancel">取消</button>
        </div>
      </div>
    </div>
  `;

  document.querySelector('body').insertAdjacentHTML('afterbegin', html);

  const editorBox = document.querySelector('#_content_editor');
  const submit = editorBox.querySelector('.submit');
  const cancel = editorBox.querySelector('.cancel');

  // 確認選擇
  const submitFun = () => {
    // @更換 SUBIT API

    editorBox.remove();
    cancel.addEventListener('click', submitFun);
  };
  submit.addEventListener('click', submitFun);

  // 取消選擇
  const cancelFun = () => {
    editorBox.remove();
    cancel.removeEventListener('click', cancelFun);
  };
  cancel.addEventListener('click', cancelFun);
}

/**
 * match each status depending on the target
 *
 * @returns {{css: string , ch : string}}
 */
function eachLsitStatus(target, status) {
  const statusPath = statusHandler[target][status];
  const statusValue = statusPath ? statusPath : statusHandler.warning;
  const css = statusValue.css;
  const ch = statusValue.ch;

  return { css, ch };
}

const orderData = () => {
  createStatusContent();
  createPayStatusContent();
  createDeliveryStatusContent();
  createOrderDetailsContent();
};

export { orderData };
