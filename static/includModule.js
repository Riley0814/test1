function includeHTML() {
  let z, i, elmnt, file, xhttp;
  /* Loop through a collection of all HTML elements: */
  z = document.getElementsByTagName('*');
  for (i = 0; i < z.length; i++) {
    elmnt = z[i];
    /*search for elements with a certain atrribute:*/
    file = elmnt.getAttribute('w3-include-html');
    if (file) {
      /* Make an HTTP request using the attribute value as the file name: */
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function () {
        if (this.readyState == 4) {
          if (this.status == 200) {
            elmnt.innerHTML = this.responseText;
          }
          if (this.status == 404) {
            elmnt.innerHTML = 'Page not found.';
          }
          /* Remove the attribute, and call this function once more: */
          elmnt.removeAttribute('w3-include-html');
          includeHTML();
        }
      };
      xhttp.open('GET', file, true);
      xhttp.send();
      /* Exit the function: */
      return;
    }
  }
}

function sideMenu() {
  fetch('./../components/sideMenu.html')
    .then((data) => data.text())
    .then((data) => {
      document.getElementById('_main_menu').innerHTML = data;
      const ja = document.createElement('script');
      ja.src = './../../components/sideMenu.js';
      document.querySelector('body').insertAdjacentElement('beforeend', ja);
    });
}

function topMenu() {
  fetch('./../components/topMenu.html')
    .then((data) => data.text())
    .then((data) => {
      document.getElementById('_top_menu').innerHTML = data;
      // const ja = document.createElement('script');
      // ja.src = './../../components/sideMenu.js';
      // document.querySelector('body').insertAdjacentElement('beforeend', ja);
    });
}

function navigation() {
  fetch('./../components/navigation.html')
    .then((data) => data.text())
    .then((data) => {
      document.getElementById('_navigation').innerHTML = data;
      const ja = document.createElement('script');
      ja.src = './../../components/navigation.js';
      document.querySelector('body').insertAdjacentElement('beforeend', ja);
    });
}

function orderDetail() {
  fetch('./../components/orderDetail.html')
    .then((data) => data.text())
    .then((data) => {
      document.getElementById('component').innerHTML = data;
      // const ja = document.createElement('script');
      // ja.src = './../../components/orderDetail.js';
      // document.querySelector('body').insertAdjacentElement('beforeend', ja);
    });
}

export { includeHTML, sideMenu, navigation, orderDetail, topMenu };
