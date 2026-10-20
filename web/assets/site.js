'use strict';
const menuToggle = document.getElementById('menu-toggle');
const navigation = document.getElementById('site-navigation');
function setMenu(open) {
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? '关闭导航' : '打开导航');
  navigation.classList.toggle('is-open', open);
  document.body.classList.toggle('menu-is-open', open);
  document.querySelector('main').inert = open;
  document.querySelector('.site-footer').inert = open;
}
menuToggle.addEventListener('click', () => setMenu(menuToggle.getAttribute('aria-expanded') !== 'true'));
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
window.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menuToggle.focus();
  }
});
window.matchMedia('(min-width: 821px)').addEventListener('change', event => {
  if (event.matches) setMenu(false);
});
