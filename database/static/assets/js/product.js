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
console.log(dataLength);


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


  sliceData.forEach((el,index) => {
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
            <button data="${index}" class="${showWeb? "light":""}">${showWeb?"網店下架":"網店上架"}</button>
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
  list.forEach(element => {
    const index = element.getAttribute('data');
    element.addEventListener('click',()=>{
      data[index].showWeb = JSON.stringify(!JSON.parse(data[index].showWeb));
      createProductContent();
    })
  });
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

const product = ()=>{
  createProductContent();
  paginationCreate();
  switchPageListen();
}

export {product};