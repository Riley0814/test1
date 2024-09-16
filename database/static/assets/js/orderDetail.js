// 引入假資料，測試用
import * as data from './../../fakeOrderDB.json' with { type: 'json' };
import * as statusHandler from './statusValueHandler.js';


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
  const matchStatus = eachLsitStatus('order',status);
  const statusCSS = matchStatus.css;
  const statusCh = matchStatus.ch;


  html = `
    ${selectContent('order')}
    <div class="content">
      <div class="box">
        <p>訂單號碼</p>
        <span>${currentOrderData.orderId}</span>
      </div>
      <div class="box">
        <p>訂單日期</p>
        <span>${currentOrderData.orderDate}</span>
      </div>
      <div class="box">
        <p>訂單狀態</p>
        <span class="_status ${statusCSS}">${statusCh}</span>
      </div>
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
}

/**
 * 建立付款資料
 */
function createPayStatusContent() {
  const box = document.getElementById('_paid_status');
  let html = '';

  // 轉換日期格式
  const date = new Date(currentOrderData.pay.date);
  currentOrderData.pay.date = reDate(date);

  const status = currentOrderData.pay.status.toLowerCase();
  const matchStatus = eachLsitStatus('pay',status);
  const statusCSS = matchStatus.css;
  const statusCh = matchStatus.ch;

  html = `
    ${selectContent('pay')}
    <div class="content">
      <div class="box">
        <p>付款狀態</p>
        <span class="_status ${statusCSS}" >${statusCh}</span>
      </div>
      <div class="box">
        <p>付款日期</p>
        <span>${currentOrderData.pay.date}</span>
      </div>
      <div class="box">
        <p>付款帳號</p>
        <span>${currentOrderData.pay.account}</span>
      </div>
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
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
          <div class="text-center flex price">
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
      <div class="text-center flex price">
        <p>NT$${currentOrderData.delivery.fee}</p>
      </div>
    </div>
  
  `;
  const totalPrice = `
  <div class="flex between mx-10">
    <div>
      <p>商品小計</p>
    </div>
    <div class="text-center flex price">
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
        <div class="text-center price">
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

/**
 * 建立配送資料
 */
function createDeliveryStatusContent() {
  const box = document.getElementById('_delivery_status');
  let html = '';

  // 轉換日期格式
  const date = new Date(currentOrderData.delivery.date);
  currentOrderData.delivery.date = reDate(date);

  const status = currentOrderData.delivery.status.toLowerCase();
  const matchStatus = eachLsitStatus('delivery',status);
  const statusCSS = matchStatus.css;
  const statusCh = matchStatus.ch;

  html = `
    ${selectContent('delivery')}
    <div class="content">
      <div class="box">
        <p>配送狀態</p>
        <span class="_status ${statusCSS}" >${statusCh}</span>
      </div>
      <div class="box">
        <p>送達日期</p>
        <span>${currentOrderData.delivery.date}</span>
      </div>
      <div class="box">
        <p>收件人</p>
        <span>${currentOrderData.recipient.username}</span>
      </div>
        <div class="box">
        <p>收件人電話</p>
        <span>${currentOrderData.recipient.phoneNumber}</span>
      </div>
      <div class="box">
        <p>收件人地址</p>
        <span>${currentOrderData.recipient.address}</span>
      </div>  
      <div class="box">
        <p>配送單號</p>
        <span>${currentOrderData.delivery.trackCode}</span>
      </div>  
      <div class="box link">
        <p>配送追蹤 / URL</p>
        <a href="${currentOrderData.delivery.url}">${currentOrderData.delivery.url}</a>
      </div>  
    </div>
  `;

  box.insertAdjacentHTML('beforeend', html);
}






// 
// 
// component
// 
// 


/**
 * Select option
 * 
 * @returns {html}
 */
function selectContent(el){

  const selectList = {
    'delivery':{
      'title' : '配送資料',
      'optionDefault':'- 更改訂單配送狀態 -',
      'option' : ['備貨中','處理中','已發貨','已到達','已退貨','已取消']
    },
    'order':{
      'title' : '訂單資料',
      'optionDefault':'- 更改訂單狀態 -',
      'option' : ['待確定','處理中','已完成','已取消']
    },
    'pay':{
      'title' : '付款資料',
      'optionDefault':'- 更改付款狀態 -',
      'option' : ['未付款','已付款','已取消','已退款']
    },
  }

  const data = selectList[el];
  let options = '';
  data.option.forEach((el)=>{
    options += `<option>${el}</option>`
  })
  return `
  <div class="title flex space between">
    <div class="text-center flex">
      <h2>
        ${data.title}
      </h2>
    </div>
    <div class="box_indent">
      <select class="select">
        <option value="" selected disabled>${data.optionDefault}</option>
        ${options}
      </select>
    </div>
  </div>
  `;
  

}

/**
 * match each status depending on the target
 * 
 * @returns {{css: string , ch : string}}
 */
function eachLsitStatus(target,status){
  const statusPath = statusHandler[target][status];
  const statusValue = statusPath? statusPath : statusHandler.warning
  const css = statusValue.css;
  const ch = statusValue.ch;

  return {css,ch}
}





const orderData = () => {
  createStatusContent();
  createPayStatusContent();
  createDeliveryStatusContent();
  createOrderDetailsContent();
};

export { orderData };
