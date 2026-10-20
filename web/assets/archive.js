'use strict';
const archiveData=JSON.parse(document.getElementById('digest-data').textContent);
const cards=[...document.querySelectorAll('#digest-list .digest-card')];
let filter='all';
const search=document.getElementById('search');
function update(){
  const q=search.value.trim().toLocaleLowerCase();let count=0;
  archiveData.forEach((d,i)=>{const show=(filter==='all'||d.type===filter)&&[d.title,d.subtitle,d.summary,...d.tags,d.topic_text,d.date].join(' ').toLocaleLowerCase().includes(q);cards[i].hidden=!show;if(show)count++;});
  document.getElementById('results').textContent=`共 ${count} 期日报`;
  document.getElementById('empty').hidden=count!==0;
  document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b.dataset.filter===filter);b.setAttribute('aria-pressed',String(b.dataset.filter===filter));});
}
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{filter=b.dataset.filter;update();}));
search.addEventListener('input',update);
document.getElementById('reset-filters').addEventListener('click',()=>{filter='all';search.value='';update();});
