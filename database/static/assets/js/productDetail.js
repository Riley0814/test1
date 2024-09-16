import * as datas from '../../fakeProductDB.json' with { type: 'json' };
const productDatas = datas.default;
let currentProductData;
getCurrentProductData();


/**
 * 獲取當前location query id
 */
function getUrlParameter(name) {
  name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
  const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
  const results = regex.exec(location.search);
  return results === null
    ? false
    : decodeURIComponent(results[1].replace(/\+/g, ' '));
}


/**
 * 
 * 替換API "依產品之Data"
 */
function getCurrentProductData() {
  const pathId = getUrlParameter('id');

  if (!pathId) window.location.href = '/pages/productDetail.html';
  else {
    for (let [key, value] of Object.entries(productDatas)) {
      if (value.id === pathId) currentProductData = value;
    }
  }
}


console.log(currentProductData);
function createTagPicContent() {
  const dom = document.getElementById('_tag_pic_content');
  dom.innerHTML = `
  <div class="description flex between item-center">
    <div class="title">
      <strong>商品主要圖片</strong>
      <p>建議 750 x 750 pixel</p>
    </div>
    <div>
      ${currentProductData.banner.length} / 12
    </div>
  </div>
  <div class="content">
    <div class="img_box">${LoopBanner()}</div>
    <div class="add_img_box">
      
      <input
        type="file"
        style="display:none"
        id="img-uploader"
        data-target="img-uploader"
        accept=".jpg,.png,.gif"
        multiple="multiple"
      />
      <h2>拖放圖片到這裡</h2>
      <p>接受jpg、png、gif格式檔案</p>
      <button id="img-select">加入圖片</button>
    </div>
  </div>
  `

  imgUploader();
}

function imgUploader(){
  const uploader = document.getElementById('img-uploader');
  const select = document.getElementById('img-select');
  const add_img_box =  document.querySelector('.add_img_box');
  select.addEventListener(
    "click",
    function (e) {
      if (uploader) {
        uploader.click();
      }
      e.preventDefault(); // prevent navigation to "#"
    },
    false,
  );

  uploader.addEventListener('change',(even)=>{
    // "even" for uploading detial
  })

  add_img_box.addEventListener("dragenter", (e)=>{
    e.stopPropagation();
    e.preventDefault();
  }, false);
  add_img_box.addEventListener("dragover", (e)=>{
    e.stopPropagation();
    e.preventDefault();
  }, false);
  add_img_box.addEventListener("drop", drop, false);


  function drop(e) {
    e.stopPropagation();
    e.preventDefault();
  
     // "e" for uploading detial
    console.log(e);

  
  }
}

function LoopBanner(){
  let html = '';

  if(currentProductData) {
    currentProductData.banner.forEach(el => {
      html += `
      <div class="items">
        <div><img src="${el}"/></div>
        <div class="btn">
          <button>ALT</button>
          <button class="delete">刪除</button>
        </div>
      </div>
      `
    });
  }

  return html;
}

const productDetail = () => {
  createTagPicContent();
};

export { productDetail };
