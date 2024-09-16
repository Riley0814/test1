// 引入假資料，測試用
/**
 * 替換API "對應訂單數量"
 * # 依照當前 showListNum 、 currentShowPage 來決定回傳多少資料
 * # ex.
 * 當前第1頁 currentShowPage = 1
 * 使用者顯示訂單數 showListNum = 24
 */
import * as datas from '../../fakeProductDB.json' with { type: 'json' };

let data = datas.default;
const dataLength = data.length;


/**
 * 頁面預設值
 * * 1
 */
let currentShowPage = 1;
const showListNum = 10;


/**
 * 依條件過濾後的產品列
 */
let showProductList;
let productList = [];


/**
 * 建立產品資料
 */
function createProductContent() {

  const box = document.getElementById('_product_detail');
  box.innerHTML = ''
  let html = '';

  const sliceData = data.slice(
    currentShowPage * showListNum - showListNum,
    currentShowPage * showListNum
  );

  const sliceDatas = productList.slice(
    currentShowPage * showListNum - showListNum,
    currentShowPage * showListNum
  );

  // 如果Data沒給值，就使用sliceData
  showProductList = productList.length != 0 ? sliceDatas : sliceData;

  console.log(showProductList);


  showProductList.forEach((el,index) => {
    const showWeb = JSON.parse(el.showWeb.toLowerCase());
    const onSale = JSON.parse(el.onSale.toLowerCase());

    html += `              
      <div class="content flex row">
        <div class="th w10">
          <img src="${el.banner[0]}">
        </div>
        <!-- price -->
        <div class="th w10">
          <strong>NT$${el.price}</strong>
        </div>
        <!-- special price -->
        <div class="th w10 red-color">
          <strong>NT$${el.specialOffer}</strong>
        </div>
        <!-- stcok -->
        <div class="th w10">
          <p>${el.totalStock}</p>
        </div>
        <!-- name -->
        <div class="th w30">
          <p>${el.name}</p>
        </div>
        <!-- status -->
        <div class="th w10">
          <p class="${onSale?"sale":"stop"}">${onSale?"販售中":"停售"}</p>
        </div>
        <!-- option -->
        <div class="th w12em btn flex-warp">
          <!-- show on web -->
          <div class="show_web">
            <button data="${el.id}" class="${showWeb? "light":""}">${showWeb?"網店下架":"網店上架"}</button>
          </div>
          <!-- edit -->
          <div>
            <a href="./productDetail.html?id=${el.id}">編輯</a>
          </div>
        </div>
      </div>
    `;
  });

  box.insertAdjacentHTML('beforeend', html);
  switchProductshowWeb();
}


/**
 * 上、下架商品
 */
function switchProductshowWeb(){
  const list = document.querySelectorAll('.show_web button');
  console.log(list);
  list.forEach(element => {
    const index = element.getAttribute('data');
    const id = data.find((el)=> el.id === index);
    element.addEventListener('click',()=>{
      switchs(id)
    });
  });

  function switchs(index) {
    index.showWeb = JSON.stringify(!JSON.parse(index.showWeb));
    createProductContent();
  }
}

// pagination
/**
 * 創建頁碼
 */
function paginationCreate() {
  let html = '';

  const pages = Math.ceil(dataLength / showListNum);
  const paginationDOM = document.querySelector('#pagination ul');
  for (let i = 1; i <= pages; i++) {
    html += `<li class="${currentShowPage === i ? "current":""}" data-num="${i}">${i}</li>`;
  }
  paginationDOM.innerHTML = html;
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
    createProductContent();
    // 回到底部
    const _main_content = document.getElementById('_main_content');
    _main_content.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

/**
 * Search
 */
function searchBtnListen() {
  const searchBtn = document.querySelector('#search_btn');
  const textDOM = document.querySelector('#search_product');

  searchBtn.addEventListener('click', listen);
  textDOM.addEventListener('keyup', (event) => {
    if (event.keyCode === 13) listen();
  });


  function listen() {
    const text = String(textDOM.value).trim();
    const targetDOM = document.querySelector('#search_targt');
    const target = targetDOM.value;
    productList = [];
    
    if (text != '' && target != '') {
      search({ target, text });
    }
    if (target === 'showWeb') search({ target, text });
    else if (text === '' && target != 'sale') createProductContent();
  }
}

/**
 * 替換API "搜尋對應條件"
 */
function search({ target, text }) {
  for (let [key, value] of Object.entries(data)) {

    switch (target) {
      case 'id':
        if (value.name.match(text)) productList.push(value);
        break;
      case 'showWeb':
        if (value.showWeb === 'true') productList.push(value);
        break;
    }
  }

  createProductContent();
}

const product = ()=>{
  createProductContent();
  paginationCreate();
  switchPageListen();
  searchBtnListen();
}

export {product};