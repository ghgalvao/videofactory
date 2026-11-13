/* Markdown reader for the panel: marked (GFM) + a small sanitizer. window.MD.render(text) returns safe HTML.
   Same engine as the hub (marked). Content is local, but notes can carry HTML: scripts, frames and inline handlers are dropped. */
(function(){
  var BAD=/^(script|style|iframe|object|embed|link|meta|base|form)$/i;
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function clean(node){
    [].slice.call(node.children).forEach(function(el){
      if(BAD.test(el.tagName)){el.remove();return}
      [].slice.call(el.attributes).forEach(function(a){
        var n=a.name.toLowerCase(),v=a.value.trim().toLowerCase();
        if(n.indexOf('on')===0||((n==='href'||n==='src'||n==='xlink:href')&&/^(javascript|data:text\/html|vbscript):/.test(v)))el.removeAttribute(a.name);
      });
      if(el.tagName==='A'&&/^https?:/i.test(el.getAttribute('href')||'')){el.setAttribute('target','_blank');el.setAttribute('rel','noopener noreferrer')}
      if(el.tagName==='TABLE'){var w=document.createElement('div');w.className='md-table';el.parentNode.insertBefore(w,el);w.appendChild(el)}
      clean(el);
    });
  }
  window.MD={
    render:function(text){
      var src=String(text==null?'':text);
      if(!src.trim())return '<p class="md-empty">Ainda sem conteúdo.</p>';
      if(!window.marked)return '<pre>'+esc(src)+'</pre>';
      var html;
      try{html=window.marked.parse(src,{gfm:true,breaks:false})}catch(e){return '<pre>'+esc(src)+'</pre>'}
      var t=document.createElement('template');t.innerHTML=html;clean(t.content);
      var box=document.createElement('div');box.appendChild(t.content);
      return box.innerHTML;
    }
  };
})();
