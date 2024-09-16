import * as datas from '../../fakeProductDB.json' with { type: 'json' };
const productDatas = datas.default;
let currentProductData;
getCurrentProductData();

let tagImgShow = true;
const options = currentProductData.options;

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

/**
 * 通用說明格式
 * 
 */
function tagDescription(strong,p){
  const res = `
    <div class="description between item-center">
      <div class="title">
        <strong>${strong}</strong>
        <p>${p}</p>
      </div>
    </div>
  `;
  return res
}

/**
 * 主要圖片建立
 */
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
      <p>接受jpg、png、gif格式檔案</p>
      <button type="file" id="img-select">加入圖片</button>
    </div>
  </div>
  `;

  imgUploader();
  imgDeleteListener();
}

// 處理上傳圖片
function imgUploader() {
  const uploader = document.getElementById('img-uploader');
  const select = document.getElementById('img-select');
  const add_img_box = document.querySelector('.add_img_box');
  select.addEventListener(
    'click',
    function (e) {
      if (uploader) {
        uploader.click();
      }
      e.preventDefault(); // prevent navigation to "#"
    },
    false
  );

  uploader.addEventListener('change', (even) => {
    // "even" for uploading detial

    const dom = document.querySelectorAll('#_tag_pic_content .content .img_box .items');

    if(dom.length + uploader.files.length > 12) alert('大於12張圖片，請重新選擇');
    else {
      for (const file of uploader.files) {
        appendNewImg(URL.createObjectURL(file));
      }
      imgDeleteListener();
    }
  });

  function appendNewImg(url){
    const dom = document.querySelector('#_tag_pic_content .content .img_box');

    const html = `
      <div class="items">
        <div><img src="${url}"/></div>
        <div class="btn">
          <button>ALT</button>
          <button class="delete">刪除</button>
        </div>
      </div>
    `;

    dom.insertAdjacentHTML('beforeend',html);
  }


  // // 拖移圖片區域
  // add_img_box.addEventListener(
  //   'dragenter',
  //   (e) => {
  //     e.stopPropagation();
  //     e.preventDefault();
  //   },
  //   false
  // );
  // add_img_box.addEventListener(
  //   'dragover',
  //   (e) => {
  //     e.stopPropagation();
  //     e.preventDefault();
  //   },
  //   false
  // );
  // add_img_box.addEventListener('drop', drop, false);

  // function drop(e) {
  //   e.stopPropagation();
  //   e.preventDefault();

  //   // "e" for uploading detial
  //   console.log(e);
  // }
}


/**
 * 商品資訊
 */
function createTagDetialContent() {
  const dom = document.getElementById('_tag_info_content');
  const domContent = dom.querySelector('.content');

  const html = `
    <div class="items">
      <label>產品名稱</label>
      <input value="${currentProductData.name}" data-title="title"/>
    </div>
    <div class="items">
      <label>描述</label>
      <input value="${currentProductData.description}" data-title="description"/>
    </div>
  `;
    

  dom.insertAdjacentHTML('afterbegin' , tagDescription('商品內頁訊息',''))
  domContent.insertAdjacentHTML('afterbegin', html);
}

// 監聽照片
function imgDeleteListener(){
  const imgBox = document.querySelectorAll('#_tag_pic_content .img_box .items');
  const imgsDeleteBtn = document.querySelectorAll('#_tag_pic_content .img_box button.delete');

  for (let i = 0; i < imgsDeleteBtn.length; i++) {
    const element = imgsDeleteBtn[i];
    element.addEventListener('click',(even)=>{
      imgBox[i].remove()
    })
  }
}


/**
 * 分類
 */
function createSortContent() {
  const dom = document.getElementById('_tag_sort_content');
  // currentProductData.sort
  let sorts = '';

  for(const index in currentProductData.sort) {
    sorts += `
    <div class="items flex">
      <input type="checkbox" ${index % 2 === 0? 'checked' : '' } />
      <label>${currentProductData.sort[index]}</label>
    </div>
    `;
  }

  const html = `
    ${tagDescription('分類','')}
    <div class="content">
      <div class="mb-20">
        <button id="sort_editor">編輯分類</button>
      </div>
      ${sorts}
    </div>
  `;
    
  dom.insertAdjacentHTML('afterbegin' , html);
  document.getElementById('sort_editor').addEventListener('click',sortEditContent);
}

// 編輯選項抬頭-內容
function sortEditContent(dom) {

  let sortHtml = '';
  const sortData = currentProductData.sort;
  for(const i in sortData) {
    sortHtml += `
      <div data-id="${sortData[i]}" class="text-left options close flex mb-10">
        <p>
          <i class="fa-solid fa-xmark"></i>
        </p>
        <label class="ml-10">${sortData[i]}</label>
      </div>
    `;
  }

  const html = `
    <div class="top_level format" id="confirm">
      <div class="top_level_box">
        <div class="mb-20 mt-20 px-15 text-center">
          ${sortHtml}
        </div>
        <div class="text-center ">
          <button class="submit">確定</button>
          <button class="cancel">取消</button>
        </div>
      </div>
    </div>
  `;

  document.querySelector('body').insertAdjacentHTML('afterbegin', html);
  const sortRemove = document.querySelectorAll('#confirm .options i')

  for(let i=0; i<sortRemove.length; i++) {
    sortRemove[i].addEventListener('click',()=>{
      const id = sortRemove[i].parentNode.parentNode.getAttribute('data-id');
      document.querySelector(`[data-id="${id}"]`).remove();
      currentProductData.sort.splice(currentProductData.sort.indexOf(id),1);
    })
  }

  const confirm = document.querySelector('#confirm');
  const submit = confirm.querySelector('.submit');
  const cancel = confirm.querySelector('.cancel');

  // 確認選擇
  const submitFun = () => {
    const dom = document.getElementById('_tag_sort_content');
    dom.innerHTML='';
    // @更換 SUBIT API
    // dom.querySelector('p').innerText = val.value;
    createSortContent();
    confirm.remove();
    cancel.addEventListener('click', submitFun);
  };
  submit.addEventListener('click', submitFun);

  // 取消選擇
  const cancelFun = () => {
    confirm.remove();
    cancel.removeEventListener('click', cancelFun);
  };
  cancel.addEventListener('click', cancelFun);
}




/**
 * 數量和售價
 */
function createSaleInfoContent() {
  const dom = document.getElementById('_tag_price_content');

  const html = `
    ${tagDescription('數量和售價','')}
    <div class="content">
      <div class="items">
        <label>原價</label>
        <input type="text" value="${Math.floor(currentProductData.price)}"/>
      </div>
      <div class="items">
        <label>特價</label>
        <input type="text" value="${Math.floor(currentProductData.specialOffer)}"/>
        <p class="info">無需設定特價時, 欄位留白</p>
      </div>
      <div class="items">
        <div class="flex">
          <input type="checkbox" ${currentProductData.samePrice? 'checked':''}/>
          <label>商品統一價格</label>
        </div>
        <p class="info">打勾時, 不分單品項的設定價格, 將統一依照價格販售</p>
      </div>
    </div>
  `;
    
  dom.insertAdjacentHTML('afterbegin' , html)
}

/**
 * 商品規格
 */
function createFormatContent() {
  const dom = document.getElementById('_tag_format_content');

  const optionTitle = currentProductData.optionTitle;


  let optionsHtml = '';
  let optionsTitleHtml = '<div class="items box w2"></div>';

  for(const option in optionTitle) {
    const el = optionTitle[option];
    const res = option === 'option1' || option === 'option2';
    const check = option === 'option1'? 'edit_option_1' : option === 'option2' ? 'edit_option_2' :'';
    optionsTitleHtml += `
      <div class="items flex item-center box ${res ? 'w30' : 'w15'}">
        <p>${el}</p>
        ${res ? `<i id="${check}" class="editor ml-5 fa-solid fa-pen-to-square"></i>` : ''}
      </div>
    `;
  }

  for(const index in options) {
    const el = options[index];
    optionsHtml += `
      <div class="items flex border-bottom my-10 pb-10" data-del="${rondomUid()}">
        <div class="box w2 close">
          <p>
            <i class="fa-solid fa-xmark"></i>
          </p>
        </div>
        <div class="box w30">
          <input type="text" value="${el.option1}"/>
        </div>
        <div class="box w30">
          <input type="text" value="${el.option2}"/>
        </div>
        <div class="box w15">
          <input type="text" value="${Math.floor(el.price)}"/>
        </div>
        <div class="box w15">
          <input type="text" value="${Math.floor(el.specialOffer)}"/>
        </div>
        <div class="box w15">
          <input type="text" value="${el.storeId}"/>
        </div>
        <div class="box w15">
          <input type="text" value="${el.stock}"/>
        </div>
      </div>
    `;
  }

  const optionTitleHtml = `
    <div class="title flex border-bottom mb-5">
      ${optionsTitleHtml}
    </div>
    <div class="items_box">
      ${optionsHtml}
    </div>
  `;

  const html = `
    ${tagDescription('商品規格','')}
    <div class="x-scroll">
      <div class="content option_content">
        <div class="mb-20">
          <button id="add_new_format_cloum">新增欄位</button>
        </div>
        ${optionTitleHtml}
      </div>
    </div>
  `;

  dom.insertAdjacentHTML('afterbegin' , html)
  document.querySelectorAll('#_tag_format_content [data-del]').get
  formatDeleteHandler();
  formatInsertHandler();
  editOptionTitleHandler();
}
// 編輯選項抬頭
function editOptionTitleHandler(){
  const dom_1 = document.getElementById('edit_option_1');
  const dom_1_content = dom_1.parentNode;
  const dom_2 = document.getElementById('edit_option_2');
  const dom_2_content = dom_2.parentNode;

  console.log(dom_1.parentNode.textContent);

  dom_1.addEventListener('click',()=>{
    editOptionContent(dom_1_content)
  })
  dom_2.addEventListener('click',()=>{
    editOptionContent(dom_2_content)
  })
}
// 編輯選項抬頭-內容
function editOptionContent(dom) {
  let html = `
    <div class="top_level format" id="confirm">
      <div class="top_level_box">
        <div class="mb-20 mt-20 text-center">
          <input id="input_enter" type="text" value="${dom.innerText.trim()}" />
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
    const val = document.getElementById('input_enter');
    // @更換 SUBIT API
    dom.querySelector('p').innerText = val.value;
    confirm.remove();
    cancel.addEventListener('click', submitFun);
  };
  submit.addEventListener('click', submitFun);

  // 取消選擇
  const cancelFun = () => {
    confirm.remove();
    cancel.removeEventListener('click', cancelFun);
  };
  cancel.addEventListener('click', cancelFun);
}
// 刪除列
function formatDeleteHandler(){
  const dels = document.querySelectorAll('#_tag_format_content [data-del]');  
  for(let i = 0; i < dels.length; i++) {
    const attr = dels[i].getAttribute('data-del');
    // const btn = dels[i].querySelector('.close');
    const btn = document.querySelector(`#_tag_format_content [data-del="${attr}"] .close`);
    console.log(btn);

    btn.addEventListener('click', ()=>{
      listen(btn,attr)
    })
    
  }


  function listen(btn, attr){
    confirmBTN((callback) => {
      if(callback) {
        document.querySelector(`#_tag_format_content [data-del="${attr}"]`).remove();
        btn.removeEventListener('click',()=>{
          listen(btn,attr)
        });
      }
    });
  }
}
// 隨機UID **作為陣列操作之目標
function rondomUid(){
  const alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789";
  let res = '';

  for(let i = 0; i < 5; i++) {
    res += alphabet[Math.floor(Math.random() * alphabet.length)];
  }

  return res
}
// 新增列
function formatInsertHandler(){
  const btn = document.getElementById('add_new_format_cloum') 
  
  
  btn.addEventListener('click',addCloum);
  

  function addCloum(){
    const uid = rondomUid();
    const dom = document.querySelector('#_tag_format_content .items_box')
    
    const html = `
      <div class="items flex border-bottom my-10 pb-10" data-del="${uid}">
        <div class="box w2 close">
          <p>
            <i class="fa-solid fa-xmark"></i>
          </p>
        </div>
        <div class="box w30">
          <input type="text" value=""/>
        </div>
        <div class="box w30">
          <input type="text" value=""/>
        </div>
        <div class="box w15">
          <input type="text" value=""/>
        </div>
        <div class="box w15">
          <input type="text" value=""/>
        </div>
        <div class="box w15">
          <input type="text" value=""/>
        </div>
        <div class="box w15">
          <input type="text" value=""/>
        </div>
      </div>
    `;

    dom.insertAdjacentHTML('beforeend',html);
    removeCloum(uid);
  }
  function removeCloum(uid){
    const dels = document.querySelector(`#_tag_format_content [data-del="${uid}"]`);  
    const btn = dels.querySelector('.close')

    btn.addEventListener('click',listen)
  
  
    function listen(){
      confirmBTN((callback) => {
        if(callback) {
          dels.remove();
          btn.removeEventListener('click',listen);
        }
      });
    }
  }

  
}

/**
 * 設定
 */
function createSettingContent() {
  const dom = document.getElementById('_tag_setting_content');
  const html = `
    ${tagDescription('數量和售價','')}
    <div class="content">
      <div class="items mb-20">
        <div class="box flex center">
          <input type="checkbox" ${currentProductData.showWeb ==='true'? "checked":''}/>
          <label class="ml-5">前台顯示</label>
        </div>
        <div class="info">
          <span>開啟:顯示商品於網站中</span>
          <span>關閉:不顯示商品於網站中</span>
        </div>
      </div>
      <div class="items">
        <div class="box  flex center">
          <input type="checkbox" ${currentProductData.onSale ==='true'? "checked":''}/>
          <label class="ml-5">販售中</label>
        </div>
        <div class="info">
          <span>開啟:商品可被加入購物車</span>
          <span>關閉:商品顯示"已售完"</span>
        </div>
      </div>
      <div class="items">
      </div>
    </div>
  `;
    
  dom.insertAdjacentHTML('afterbegin' , html)
    console.log(currentProductData);
}





/**
 * 
 * @param {Boolean} callback - if true return true otherwise empty
 */
function confirmBTN(callback) {
  let html = `
    <div class="top_level" id="confirm">
      <div class="top_level_box">
        <div class="mb-20 mt-10 text-center">
          確定要刪除嗎?
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
    callback(true);
    confirm.remove();
    cancel.addEventListener('click', submitFun);
  };
  submit.addEventListener('click', submitFun);

  // 取消選擇
  const cancelFun = () => {
    confirm.remove();
    cancel.removeEventListener('click', cancelFun);
  };
  cancel.addEventListener('click', cancelFun);
}


/**
 * content switch by tag click.
 */
function tagActiveListener() {
  const tags = document.querySelectorAll('#_product_detail_content .row .th');
  tags.forEach((el) => {
    el.addEventListener('click', (even) => {
      tagActive(tags, even.target.id);
      contentActive(even.target.id);
    });
  });
}

/**
 * tag active setting.
 */
function tagActive(tags, id) {
  // tags
  tags.forEach((el) => {
    if (el.id != id) {
      el.classList.remove('content--active');
    } else {
      el.classList.add('content--active');
    }
  });
}


function contentActive(id) {
  const contents = document.querySelectorAll('#_product_detail .item');

  // content
  contents.forEach((el) => {
    if (el.id != `${id}_content`) {
      el.style.display = 'none';
    } else {
      el.style.display = '';
    }
  });
}


/**
 * content first loading style. 
 */
function contentFirstLoad() {
  const contents = document.querySelectorAll('#_product_detail .item');

  // content
  contents.forEach((el) => {
    if (el.id != `_tag_pic_content`) {
      el.style.display = 'none';
    } else {
      el.style.display = '';
    }
  });
}



function LoopBanner() {
  let html = '';

  if (currentProductData) {
    currentProductData.banner.forEach((el) => {
      html += `
      <div class="items">
        <div><img src="${el}"/></div>
        <div class="btn">
          <button>ALT</button>
          <button class="delete">刪除</button>
        </div>
      </div>
      `;
    });
  }

  return html;
}

const productDetail = () => {
  createTagPicContent();
  tagActiveListener();
  contentFirstLoad();
  createTagDetialContent();
  createSortContent();
  createSaleInfoContent();
  createFormatContent();
  createSettingContent();
};

export { productDetail };
