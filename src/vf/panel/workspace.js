/* Gallery workspace tabs: Brief, Assets, References and Research.
   Identifiers in English; user-facing text in Portuguese. */
(function(){
  var CATEGORY_LABEL={brand:'Marca',characters:'Personagens',images:'Imagens',audio:'Áudio',docs:'Documentos'};
  var REF_LABEL={link:'link',file:'arquivo',text:'texto'};
  var IMG=/\.(png|jpe?g|webp|gif|svg)$/i,VID=/\.(mp4|webm|mov|m4v)$/i;
  var ctx=null,data=null;

  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function url(path){return '/file?g='+encodeURIComponent(ctx.gallery)+'&b=0&p='+encodeURIComponent(path)}
  function size(n){return n>1048576?(n/1048576).toFixed(1)+' MB':Math.max(1,Math.round(n/1024))+' KB'}
  /* images and links written as relative paths inside a note resolve against the note's folder in the gallery */
  function resolveRel(html,dir){return html.replace(/(src|href)="(?!https?:|\/|#|data:|mailto:)([^"]+)"/g,function(m,a,v){return a+'="'+url(dir+v)+'"'})}
  function copyBlock(text,label){return '<div class="code-block"><div class="code-bar"><span>'+esc(label)+'</span><button class="btn small" type="button" data-copy>Copiar</button></div><pre>'+esc(text)+'</pre></div>'}
  function load(){return ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/workspace').then(function(j){data=j;return j})}
  function send(method,path,body){return ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+path,{method:method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})})}

  function uploadFiles(files,area,category,meta,onDone,statusEl){
    var list=[].slice.call(files),done=0,errors=[];
    if(!list.length)return;
    (function next(){
      if(!list.length){statusEl.textContent=errors.length?errors.join(' · '):done+' arquivo(s) enviado(s)';onDone();return}
      var f=list.shift(),xhr=new XMLHttpRequest(),q='area='+area+'&category='+encodeURIComponent(category||'');
      if(meta)Object.keys(meta).forEach(function(k){q+='&'+k+'='+encodeURIComponent(meta[k])});
      xhr.open('POST','/api/gallery/'+encodeURIComponent(ctx.gallery)+'/upload?'+q);
      xhr.setRequestHeader('X-Filename',encodeURIComponent(f.name||'colado.png'));
      xhr.upload.onprogress=function(e){if(e.lengthComputable)statusEl.textContent='enviando '+f.name+'… '+Math.round(100*e.loaded/e.total)+'%'};
      xhr.onload=function(){if(xhr.status===200)done++;else{try{errors.push(f.name+': '+JSON.parse(xhr.responseText).error)}catch(e){errors.push(f.name+': erro '+xhr.status)}}next()};
      xhr.onerror=function(){errors.push(f.name+': falha de conexão');next()};
      xhr.send(f);
    })();
  }
  function dropzone(el,onFiles){
    el.addEventListener('dragover',function(e){e.preventDefault();el.classList.add('over')});
    el.addEventListener('dragleave',function(){el.classList.remove('over')});
    el.addEventListener('drop',function(e){e.preventDefault();el.classList.remove('over');onFiles(e.dataTransfer.files)});
    var input=el.querySelector('input[type=file]');
    el.addEventListener('click',function(e){if(e.target.closest('select,button,input,label'))return;input.click()});
    input.addEventListener('change',function(){onFiles(input.files);input.value=''});
  }
  function onPaste(handler){
    document.onpaste=function(e){
      if(!ctx||e.target.closest('textarea,input'))return;
      var files=[].slice.call(e.clipboardData.files||[]);
      if(files.length){e.preventDefault();handler(files)}
    };
  }

  /* ---------- completeness (the gamified meter) ---------- */
  function completeness(){
    var b=data.brand||{},brief=data.brief||'';
    var checks=[
      ['Brief escrito',brief.replace(/\s+/g,'').length>120],
      ['Público definido',/##\s*Público\s*\n+[^#\s(]/i.test(brief)],
      ['Tom de voz definido',/##\s*Tom de voz\s*\n+[^#\s(]/i.test(brief)],
      ['Nome da marca',!!b.name],
      ['Paleta com 2+ cores',(b.colors||[]).length>=2],
      ['Fontes definidas',!!(b.fonts&&b.fonts.display)],
      ['Logo enviado',!!b.logo],
      ['1ª referência salva',data.references.length>0],
      ['1º estudo de pesquisa',data.research.length>0]
    ];
    var ok=checks.filter(function(c){return c[1]}).length;
    return {pct:Math.round(100*ok/checks.length),checks:checks};
  }
  function meter(){
    var c=completeness();
    return '<div class="meter"><div class="meter-top"><b>Brief '+c.pct+'% completo</b><span class="hint">quanto mais completo, mais os vídeos saem no tom certo</span></div><div class="progress"><div class="track"><i style="width:'+c.pct+'%"></i></div></div>'+
      '<div class="badges">'+c.checks.map(function(k){return '<span class="badge'+(k[1]?' on':'')+'">'+(k[1]?'✓ ':'')+k[0]+'</span>'}).join('')+'</div></div>';
  }

  /* ---------- Brief ---------- */
  function renderBrief(el){
    var b=data.brand||{},colors=(b.colors&&b.colors.length?b.colors:[{name:'principal',hex:'#2d6be0'}]);
    var logos=data.assets.filter(function(a){return a.category==='brand'&&IMG.test(a.name)});
    el.innerHTML=meter()+
      '<div class="ws-cols"><section class="ws-card"><div class="setup-top"><h3>Brief (PRD da galeria)</h3><span class="hint" id="brief-state"></span></div>'+
        '<p class="hint">Objetivo, público, tom, plataformas e primeiros temas. O agente lê este texto antes de criar qualquer job aqui. Arquivo: <code>'+esc(data.home)+'/brief.md</code></p>'+
        '<textarea id="brief-text" class="brief-text" placeholder="Escreva o brief ou comece pelo modelo">'+esc(data.brief)+'</textarea>'+
        '<div class="row">'+(data.brief?'':'<button class="btn" type="button" id="brief-template">Começar pelo modelo</button>')+'<button class="btn primary" type="button" id="brief-save">Salvar brief</button></div></section>'+
      '<section class="ws-card"><div class="setup-top"><h3>Identidade</h3><span class="hint" id="brand-state"></span></div>'+
        '<p class="hint">Usada nos vídeos, nos criativos e no manual de marca. Arquivo: <code>'+esc(data.home)+'/brand.json</code></p>'+
        '<div class="form-grid"><label>Nome<input id="brand-name" value="'+esc(b.name||'')+'"></label><label>Frase da marca<input id="brand-tagline" value="'+esc(b.tagline||'')+'"></label></div>'+
        '<div class="field-title">Cores</div><div id="brand-colors" class="colors">'+colors.map(colorRow).join('')+'</div><button class="btn small" type="button" id="color-add">+ cor</button>'+
        '<div class="form-grid"><label>Fonte de título<input id="brand-display" placeholder="ex.: Archivo Black" value="'+esc((b.fonts||{}).display||'')+'"></label><label>Fonte de texto<input id="brand-body" placeholder="ex.: Inter" value="'+esc((b.fonts||{}).body||'')+'"></label></div>'+
        '<label>Logo<select id="brand-logo"><option value="">'+(logos.length?'escolha um arquivo de Marca':'envie o logo na aba Assets, categoria Marca')+'</option>'+logos.map(function(a){return '<option value="'+esc(a.path)+'"'+(a.path===b.logo?' selected':'')+'>'+esc(a.name)+'</option>'}).join('')+'</select></label>'+
        '<label>Ícone (opcional)<select id="brand-icon"><option value="">sem ícone</option>'+logos.map(function(a){return '<option value="'+esc(a.path)+'"'+(a.path===b.icon?' selected':'')+'>'+esc(a.name)+'</option>'}).join('')+'</select></label>'+
        '<label>Chamada final<input id="brand-cta" placeholder="ex.: Segue pra mais" value="'+esc(b.cta||'')+'"></label>'+
        '<div class="form-grid"><label>Palavras que usa<input id="brand-voice" placeholder="separe por vírgula" value="'+esc((b.voice||[]).join(', '))+'"></label><label>Palavras que evita<input id="brand-avoid" placeholder="separe por vírgula" value="'+esc((b.avoid||[]).join(', '))+'"></label></div>'+
        '<div class="row"><button class="btn primary" type="button" id="brand-save">Salvar identidade</button></div></section></div>';
    var t=document.getElementById('brief-template');
    if(t)t.onclick=function(){document.getElementById('brief-text').value=data.brief_template;t.remove()};
    document.getElementById('brief-save').onclick=function(){
      var st=document.getElementById('brief-state');st.textContent='salvando…';
      send('PUT','/brief',{text:document.getElementById('brief-text').value}).then(function(){st.textContent='salvo';return load()}).then(function(){refreshMeter(el)}).catch(function(e){st.textContent=e.message});
    };
    document.getElementById('color-add').onclick=function(){document.getElementById('brand-colors').insertAdjacentHTML('beforeend',colorRow({name:'',hex:'#888888'}))};
    document.getElementById('brand-colors').onclick=function(e){var r=e.target.closest('[data-remove-color]');if(r)r.closest('.color-row').remove()};
    document.getElementById('brand-save').onclick=function(){
      var st=document.getElementById('brand-state');st.textContent='salvando…';
      var split=function(id){return document.getElementById(id).value.split(',').map(function(s){return s.trim()}).filter(Boolean)};
      send('PUT','/brand',{name:val('brand-name'),tagline:val('brand-tagline'),cta:val('brand-cta'),logo:val('brand-logo'),icon:val('brand-icon'),
        fonts:{display:val('brand-display'),body:val('brand-body')},voice:split('brand-voice'),avoid:split('brand-avoid'),
        colors:[].map.call(document.querySelectorAll('.color-row'),function(r){return {name:r.querySelector('[data-cname]').value.trim(),hex:r.querySelector('[data-chex]').value}})
      }).then(function(){st.textContent='salvo';return load()}).then(function(){refreshMeter(el)}).catch(function(e){st.textContent=e.message});
    };
  }
  function colorRow(c){return '<div class="color-row"><input type="color" data-chex value="'+esc(c.hex)+'" aria-label="Cor"><input data-cname placeholder="nome (ex.: principal)" value="'+esc(c.name)+'"><button class="btn small" type="button" data-remove-color aria-label="Remover cor">×</button></div>'}
  function val(id){return document.getElementById(id).value.trim()}
  function refreshMeter(el){var m=el.querySelector('.meter');if(m)m.outerHTML=meter()}

  /* ---------- Assets ---------- */
  function renderAssets(el){
    el.innerHTML='<div class="dropzone" id="asset-drop"><input type="file" multiple hidden><b>Arraste arquivos aqui, clique para escolher ou cole com Ctrl+V</b>'+
      '<span class="hint">Imagens, vídeos, áudio, fontes e PDF, até 500 MB por arquivo. Destino: <code>'+esc(data.home)+'/assets/&lt;categoria&gt;/</code></span>'+
      '<label class="inline">Categoria <select id="asset-cat"><option value="">automática pelo tipo</option>'+data.categories.map(function(c){return '<option value="'+c+'">'+CATEGORY_LABEL[c]+'</option>'}).join('')+'</select></label>'+
      '<span class="hint" id="asset-status" aria-live="polite"></span></div>'+
      data.categories.map(function(cat){
        var items=data.assets.filter(function(a){return a.category===cat});
        if(!items.length)return '';
        return '<h3 class="ws-h3">'+CATEGORY_LABEL[cat]+' <span class="hint">'+items.length+'</span></h3><div class="asset-grid">'+items.map(assetCard).join('')+'</div>';
      }).join('')+(data.assets.length?'':'<div class="empty">Nenhum asset ainda. Comece pelo logo (categoria Marca) e pela folha do personagem (Personagens).</div>');
    var reload=function(){load().then(function(){renderAssets(el)})};
    var go=function(files){uploadFiles(files,'assets',document.getElementById('asset-cat').value,null,reload,document.getElementById('asset-status'))};
    dropzone(document.getElementById('asset-drop'),go);onPaste(go);
    bindRemove(el,reload);
  }
  function assetCard(a){
    var full=data.home+'/'+a.path,thumb=IMG.test(a.name)?'<img loading="lazy" alt="" src="'+url(a.path)+'">':VID.test(a.name)?'<video muted preload="metadata" src="'+url(a.path)+'#t=1"></video>':'<span>'+esc(a.name.split('.').pop().toUpperCase())+'</span>';
    return '<div class="asset"><a class="asset-thumb" href="'+url(a.path)+'" target="_blank" rel="noopener">'+thumb+'</a><div class="asset-info"><b title="'+esc(a.name)+'">'+esc(a.name)+'</b><span class="hint">'+size(a.size)+'</span>'+
      '<div class="row"><button class="btn small" type="button" data-copy-text="'+esc(full)+'">Copiar caminho</button><button class="btn small danger" type="button" data-trash="'+esc(a.path)+'">Remover</button></div></div></div>';
  }
  function bindRemove(el,reload){
    el.onclick=function(e){
      var c=e.target.closest('[data-copy-text]');
      if(c){var t=c.getAttribute('data-copy-text');try{navigator.clipboard.writeText(t).then(function(){c.textContent='Copiado'})}catch(err){c.textContent=t}return}
      var r=e.target.closest('[data-trash],[data-remove-ref]');
      if(!r)return;
      if(r.getAttribute('data-armed')!=='1'){r.setAttribute('data-armed','1');r.textContent='Confirmar';return}
      var p=r.hasAttribute('data-trash')?send('POST','/trash',{path:r.getAttribute('data-trash')}):send('POST','/references/'+encodeURIComponent(r.getAttribute('data-remove-ref'))+'/remove');
      p.then(reload).catch(function(err){r.textContent=err.message});
    };
  }

  /* ---------- References ---------- */
  function renderReferences(el){
    var kind='link',filter='all';
    el.innerHTML='<section class="ws-card"><h3>Nova referência</h3><div class="filters" id="ref-kind">'+['link','text','file'].map(function(k,i){return '<button class="chip" type="button" data-kind="'+k+'" aria-pressed="'+(i===0)+'">'+({link:'Link',text:'Texto',file:'Arquivo'})[k]+'</button>'}).join('')+'</div>'+
      '<div class="form-grid"><label>Título<input id="ref-title" placeholder="ex.: Reel do mentor e aprendiz"></label><label>Tags<input id="ref-tags" placeholder="gancho, edição, visual"></label></div>'+
      '<div id="ref-source"></div>'+
      '<label>Por que salvou<textarea id="ref-why" rows="2" placeholder="o que você quer copiar no formato: o gancho, o ritmo, a legenda…"></textarea></label>'+
      '<div class="row"><button class="btn primary" type="button" id="ref-add">Salvar referência</button><span class="hint" id="ref-status" aria-live="polite"></span></div></section>'+
      '<div class="filters" id="ref-filter"></div><div class="ref-list" id="ref-list"></div>';
    function source(){
      var box=document.getElementById('ref-source');
      if(kind==='link')box.innerHTML='<label>Link<input id="ref-url" type="url" placeholder="https://"></label>';
      else if(kind==='text')box.innerHTML='<label>Texto<textarea id="ref-text" rows="4" placeholder="anotação, trecho, ideia…"></textarea></label>';
      else{box.innerHTML='<div class="dropzone small" id="ref-drop"><input type="file" hidden><b>Arraste o arquivo, clique ou cole com Ctrl+V</b><span class="hint" id="ref-file-name">print, vídeo, PDF ou imagem</span></div>';
        var picked=null;dropzone(document.getElementById('ref-drop'),function(files){picked=files[0];document.getElementById('ref-file-name').textContent=picked?picked.name:''});
        onPaste(function(files){picked=files[0];document.getElementById('ref-file-name').textContent=picked.name||'imagem colada'});
        box.getPicked=function(){return picked};}
    }
    function list(){
      var refs=data.references.filter(function(r){return filter==='all'||r.type===filter});
      var counts={all:data.references.length};data.references.forEach(function(r){counts[r.type]=(counts[r.type]||0)+1});
      document.getElementById('ref-filter').innerHTML=[['all','Todas'],['link','Links'],['text','Textos'],['file','Arquivos']].filter(function(o){return o[0]==='all'||counts[o[0]]}).map(function(o){return '<button class="chip" type="button" data-filter-ref="'+o[0]+'" aria-pressed="'+(filter===o[0])+'">'+o[1]+'<b>'+(counts[o[0]]||0)+'</b></button>'}).join('');
      document.getElementById('ref-list').innerHTML=refs.map(function(r){
        var src=r.type==='link'?'<a href="'+esc(r.source)+'" target="_blank" rel="noopener">'+esc(r.source.replace(/^https?:\/\/(www\.)?/,'').slice(0,60))+'</a>':
          r.type==='file'?(IMG.test(r.source)?'<a href="'+url(r.source)+'" target="_blank" rel="noopener"><img class="ref-img" loading="lazy" alt="" src="'+url(r.source)+'"></a>':'<a href="'+url(r.source)+'" target="_blank" rel="noopener">'+esc(r.source.split('/').pop())+'</a>'):
          '<pre class="ref-note" data-note="'+esc(r.source)+'">…</pre>';
        var cmd='/vf-reference '+(r.type==='link'?r.source:data.home+'/'+r.source)+(data.slug?' '+data.slug:'');
        return '<article class="ref"><div class="setup-top"><b>'+esc(r.title)+'</b><span class="status">'+REF_LABEL[r.type]+'</span></div>'+src+
          (r.why?'<p><span class="hint">Por que:</span> '+esc(r.why)+'</p>':'')+(r.tags.length?'<div class="badges">'+r.tags.map(function(t){return '<span class="badge">'+esc(t)+'</span>'}).join('')+'</div>':'')+
          (r.analysis?'<div class="row"><button class="btn small" type="button" data-read-analysis="'+esc(r.analysis)+'">Ler análise</button></div>':'')+
          '<details><summary>Analisar com o Claude</summary>'+copyBlock(cmd,'Cole no Claude Code')+'</details>'+
          '<div class="row"><span class="hint">'+esc(r.date)+'</span><button class="btn small danger" type="button" data-remove-ref="'+esc(r.id)+'">Remover</button></div></article>';
      }).join('')||'<div class="empty">Nenhuma referência ainda. Salve um vídeo, post, print ou anotação que mostre o formato que você quer.</div>';
      [].forEach.call(document.querySelectorAll('[data-note]'),function(p){fetch(url(p.getAttribute('data-note'))).then(function(r){return r.text()}).then(function(t){p.textContent=t.slice(0,400)})});
    }
    source();list();
    document.getElementById('ref-kind').onclick=function(e){var b=e.target.closest('[data-kind]');if(!b)return;kind=b.getAttribute('data-kind');[].forEach.call(this.children,function(x){x.setAttribute('aria-pressed',x===b)});source()};
    document.getElementById('ref-filter').onclick=function(e){var b=e.target.closest('[data-filter-ref]');if(!b)return;filter=b.getAttribute('data-filter-ref');list()};
    document.getElementById('ref-add').onclick=function(){
      var st=document.getElementById('ref-status'),meta={title:val('ref-title'),why:val('ref-why'),tags:val('ref-tags')};
      var reload=function(){return load().then(function(){renderReferences(el)})};
      if(kind==='file'){var f=document.getElementById('ref-source').getPicked();if(!f){st.textContent='escolha um arquivo';return}
        uploadFiles([f],'references','',meta,reload,st);return}
      var body={type:kind,title:meta.title,why:meta.why,tags:meta.tags,source:kind==='link'?val('ref-url'):document.getElementById('ref-text').value};
      st.textContent='salvando…';send('POST','/references',body).then(reload).catch(function(e){st.textContent=e.message});
    };
    bindRemove(el.querySelector('#ref-list'),function(){load().then(function(){renderReferences(el)})});
    el.querySelector('#ref-list').addEventListener('click',function(e){var b=e.target.closest('[data-read-analysis]');if(!b)return;var p=b.getAttribute('data-read-analysis');
      fetch(url(p)).then(function(r){return r.text()}).then(function(t){ctx.openDoc(b.closest('.ref').querySelector('b').textContent,resolveRel(window.Learn&&window.Learn.md?window.Learn.md(t):'<pre>'+esc(t)+'</pre>',p.replace(/[^/]*$/,'')))})});
  }

  /* ---------- Research ---------- */
  function renderResearch(el){
    el.innerHTML='<section class="ws-card"><h3>Novo estudo</h3><p class="hint">O Claude pesquisa o tema, confere cada dado em duas fontes e grava em <code>'+esc(data.home)+'/research/</code>. Os roteiros da galeria passam a usar o estudo.</p>'+
      '<label>Tema<input id="research-topic" placeholder="ex.: como funcionam as marés"></label><div id="research-cmd"></div></section>'+
      '<div class="ref-list">'+(data.research.map(function(r){
        return '<article class="ref"><div class="setup-top"><b>'+esc(r.title)+'</b><span class="hint">'+new Date(r.mtime*1000).toLocaleDateString('pt-BR')+'</span></div><p class="hint"><code>'+esc(r.path)+'</code></p>'+
          '<div class="row"><button class="btn small" type="button" data-read="'+esc(r.path)+'">Ler estudo</button><button class="btn small danger" type="button" data-trash="'+esc(r.path)+'">Remover</button></div></article>';
      }).join('')||'<div class="empty">Nenhum estudo ainda.</div>')+'</div>';
    var topic=document.getElementById('research-topic'),cmd=function(){document.getElementById('research-cmd').innerHTML=copyBlock('/vf-research '+(topic.value.trim()||'<tema>')+(data.slug?' '+data.slug:''),'Cole no Claude Code')};
    topic.oninput=cmd;cmd();
    bindRemove(el.querySelector('.ref-list'),function(){load().then(function(){renderResearch(el)})});
    el.querySelector('.ref-list').addEventListener('click',function(e){
      var b=e.target.closest('[data-read]');if(!b)return;
      fetch(url(b.getAttribute('data-read'))).then(function(r){return r.text()}).then(function(t){ctx.openDoc(b.closest('.ref').querySelector('b').textContent,resolveRel(window.Learn&&window.Learn.md?window.Learn.md(t):'<pre>'+esc(t)+'</pre>',b.getAttribute('data-read').replace(/[^/]*$/,'')))});
    });
  }

  /* ---------- Brand manual ---------- */
  function renderManual(el){
    var pdf=data.exports.find(function(f){return f.name==='manual-de-marca.pdf'});
    el.innerHTML='<div class="manual-bar"><div><b>Manual de marca</b><span class="hint"> gerado do brief, da identidade, dos assets de Marca e das folhas dos vídeos desta galeria. Mudou algo? Ele se atualiza sozinho.</span></div>'+
      '<div class="row"><button class="btn primary" type="button" id="manual-pdf">Exportar PDF</button>'+
      (pdf?'<a class="btn" href="'+url(pdf.path)+'" target="_blank" rel="noopener">Abrir PDF</a>':'')+
      '<span class="hint" id="manual-state" aria-live="polite">'+(pdf?'último PDF: '+new Date(pdf.mtime*1000).toLocaleString('pt-BR'):'')+'</span></div></div>'+
      '<iframe class="manual-frame" title="Manual de marca" src="/manual?g='+encodeURIComponent(ctx.gallery)+'"></iframe>';
    document.getElementById('manual-pdf').onclick=function(){
      var st=document.getElementById('manual-state'),b=this;b.disabled=true;st.textContent='gerando PDF…';
      ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/manual-pdf',{method:'POST'}).then(function(r){
        return load().then(function(){renderManual(el);document.getElementById('manual-state').textContent='PDF salvo em '+data.home+'/'+r.path+' ('+size(r.size)+')'});
      }).catch(function(e){st.textContent=e.message;b.disabled=false});
    };
  }


  /* ---------- Client tabs (same as the agency hub) ---------- */
  var cview=null;
  function cload(){return ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/client').then(function(j){cview=j;return j})}
  function mdBox(t){return '<div class="md">'+(window.MD?window.MD.render(t):'<pre>'+esc(t)+'</pre>')+'</div>'}
  function putFile(path,text){return ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/file',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({path:path,text:text})})}
  function readFile(path){return fetch(url(path)+'&t='+Date.now()).then(function(r){return r.ok?r.text():''})}
  function copyText(btn){var pre=btn.closest('.code-block').querySelector('pre');try{navigator.clipboard.writeText(pre.innerText).then(function(){btn.textContent='Copiado'})}catch(e){btn.textContent='Selecione e Ctrl+C'}}

  /* markdown card: rendered text with an Editar button (saves the file in the client folder) */
  function mdCard(title,path,text,opt){
    opt=opt||{};
    var head='<div class="setup-top"><h3>'+esc(title)+'</h3><div class="row"><span class="hint" data-st></span><button class="btn small" type="button" data-edit>Editar</button></div></div>';
    var body=(opt.note?'<p class="hint">'+opt.note+'</p>':'')+'<div data-view>'+mdBox(text)+'</div>';
    return opt.fold?'<details class="ws-card mdcard fold" data-path="'+esc(path)+'"'+(opt.open?' open':'')+'><summary>'+esc(title)+'</summary><div class="fold-body"><div class="row end"><span class="hint" data-st></span><button class="btn small" type="button" data-edit>Editar</button></div>'+body+'</div></details>'
      :'<section class="ws-card mdcard" data-path="'+esc(path)+'">'+head+body+'</section>';
  }
  function mdClick(e,after){
    var card=e.target.closest('.mdcard');if(!card)return false;
    var path=card.getAttribute('data-path'),view=card.querySelector('[data-view]'),st=card.querySelector('[data-st]');
    if(e.target.closest('[data-edit]')){e.preventDefault();readFile(path).then(function(t){view.innerHTML='<textarea class="md-edit" aria-label="Editar '+esc(path)+'">'+esc(t)+'</textarea><div class="row"><button class="btn primary small" type="button" data-save>Salvar</button><button class="btn small" type="button" data-cancel>Cancelar</button></div>'});return true}
    if(e.target.closest('[data-save]')){var txt=card.querySelector('textarea').value;st.textContent='salvando…';putFile(path,txt).then(function(){st.textContent='salvo';view.innerHTML=mdBox(txt);if(after)after(path,txt)}).catch(function(x){st.textContent=x.message});return true}
    if(e.target.closest('[data-cancel]')){readFile(path).then(function(t){view.innerHTML=mdBox(t);st.textContent=''});return true}
    return false;
  }

  var TAB_KEY={'Visão geral':'overview','Briefing':'brief','Identidade':'identity','Social':'social','Documentos':'documents','Materiais':'assets'};
  var STATE_LABEL={ok:['Completa','ok'],rascunho:['Em rascunho','warn'],vazia:['Vazia','bad']};
  function renderOverview(el){
    var c=cview.check;
    var cards=Object.keys(c.tabs).map(function(k){var s=STATE_LABEL[c.tabs[k]]||[c.tabs[k],'warn'];
      return '<button class="tabcard" type="button" data-go="'+TAB_KEY[k]+'"><b>'+esc(k)+'</b><span class="pill pill-'+s[1]+'">'+s[0]+'</span></button>'}).join('')+
      '<button class="tabcard" type="button" data-go="videos"><b>Produção</b><span class="pill pill-ok">'+c.jobs.length+(c.jobs.length===1?' job':' jobs')+'</span></button>';
    var todo=c.problems.map(esc).concat(c.open.map(function(o){return '<code>'+esc(o[0])+'</code>: '+o[1]+(o[1]>1?' itens':' item')+' a confirmar'}));
    el.innerHTML='<section class="ws-card"><h3>Como está este cliente</h3><div class="tabcards">'+cards+'</div></section>'+
      (todo.length?'<section class="ws-card"><h3>O que falta</h3><ul class="todo">'+todo.map(function(t){return '<li>'+t+'</li>'}).join('')+'</ul></section>':'')+
      mdCard('Leia antes','LEIA-ANTES.md',cview.warning)+mdCard('Visão geral','visao-geral.md',cview.overview)+
      '<section class="ws-card"><h3>Como criar uma peça</h3><p class="hint">Cole no Claude Code, na pasta do motor:</p>'+
      copyBlock('/vf-pack '+cview.slug,'Montar ou atualizar o pack')+copyBlock('/vf-carousel <tema do post> '+cview.slug,'Novo carrossel')+copyBlock('/vf-docs '+cview.slug+' proposal','Nova proposta em PDF')+'</section>';
    el.onclick=function(e){var g=e.target.closest('[data-go]');if(g){ctx.go(g.getAttribute('data-go'));return}
      var cp=e.target.closest('[data-copy]');if(cp){copyText(cp);return}mdClick(e,function(){return load().then(cload)})};
  }

  function renderBriefClient(el){
    el.innerHTML=mdCard('Briefing','brief.md',data.brief,{note:'O agente lê este briefing antes de criar qualquer peça deste cliente.'});
    el.onclick=function(e){mdClick(e)};
  }

  function fileEditor(title,path,hint){
    return '<section class="ws-card fileed" data-fpath="'+esc(path)+'"><div class="setup-top"><h3>'+esc(title)+'</h3><span class="hint" data-st></span></div><p class="hint">'+hint+'</p><textarea class="md-edit tall" aria-label="'+esc(title)+'">carregando…</textarea><div class="row"><button class="btn primary small" type="button" data-fsave>Salvar e atualizar o manual</button></div></section>';
  }
  function renderIdentity(el){
    var pdf=(data.exports||[]).find(function(f){return f.name==='manual-de-marca.pdf'});
    el.innerHTML='<div class="manual-bar"><div><b>Identidade e manual de marca</b><span class="hint"> montado a partir do marca.json, do guia visual e das fotos do cliente.</span></div>'+
      '<div class="row"><button class="btn primary" type="button" id="manual-pdf">Baixar PDF</button>'+(pdf?'<a class="btn" href="'+url(pdf.path)+'" target="_blank" rel="noopener">Abrir último PDF</a>':'')+'<span class="hint" id="manual-state" aria-live="polite">'+(pdf?'último PDF: '+new Date(pdf.mtime*1000).toLocaleString('pt-BR'):'')+'</span></div></div>'+
      '<iframe class="manual-frame" id="manual-frame" title="Manual de marca" src="/manual?g='+encodeURIComponent(ctx.gallery)+'"></iframe>'+
      '<details class="ws-card fold"><summary>Editar identidade</summary><div class="fold-body">'+
      fileEditor('Dados da marca (marca.json)','marca.json','Cores, fontes, logo, tom, contatos, certificações e regras. Formato JSON.')+
      fileEditor('Guia visual','identidade/guia-visual.md','Formas, tipografia, cor, fotografia e o que fazer e não fazer.')+'</div></details>';
    document.getElementById('manual-pdf').onclick=function(){
      var st=document.getElementById('manual-state'),b=this;b.disabled=true;st.textContent='gerando PDF…';
      ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/manual-pdf',{method:'POST'}).then(function(r){
        var a=document.createElement('a');a.href=url(r.path);a.download='manual-de-marca.pdf';document.body.appendChild(a);a.click();a.remove();
        st.textContent='PDF baixado ('+size(r.size)+')';b.disabled=false;
      }).catch(function(x){st.textContent=x.message;b.disabled=false});
    };
    [].forEach.call(el.querySelectorAll('.fileed'),function(sec){readFile(sec.getAttribute('data-fpath')).then(function(t){sec.querySelector('textarea').value=t})});
    el.onclick=function(e){var sv=e.target.closest('[data-fsave]');if(!sv)return;var sec=sv.closest('.fileed'),st=sec.querySelector('[data-st]');
      st.textContent='salvando…';putFile(sec.getAttribute('data-fpath'),sec.querySelector('textarea').value).then(function(){st.textContent='salvo';var f=document.getElementById('manual-frame');f.src='/manual?g='+encodeURIComponent(ctx.gallery)+'&t='+Date.now()}).catch(function(x){st.textContent=x.message})};
  }

  function renderSocial(el){
    var packs=(cview.packs||[]).map(function(p){return '<section class="ws-card"><h3>Pack: '+esc(p.name)+'</h3>'+
      (p.grade?'<p><img alt="Grade do perfil" style="max-width:360px;width:100%;border-radius:8px;border:1px solid var(--line)" src="'+url(p.grade)+'"></p>':'')+
      '<div class="row">'+(p.zip?'<a class="btn primary small" href="'+url(p.zip)+'" download>Baixar pack (zip)</a>':'')+(p.resumo?'<a class="btn small" href="'+url(p.resumo)+'" target="_blank" rel="noopener">Abrir resumo</a>':'')+'</div>'+
      '<p class="hint">Grade na ordem de leitura (post 1 no canto superior esquerdo). Gerado por <code>vf pack build</code>.</p></section>'}).join('');
    el.innerHTML=packs+mdCard('Calendário','social/calendario.md',cview.calendar,{fold:true,open:true})+mdCard('Plano de conteúdo','social/plano.md',cview.plan,{fold:true});
    el.onclick=function(e){mdClick(e,function(){return load().then(cload)})};
  }

  var DOC_ORDER=['presentation','proposal','contract','statement','estimate'];
  function dday(ts){return new Date(ts*1000).toLocaleDateString('pt-BR')}
  function renderDocuments(el){
    var rows=DOC_ORDER.map(function(k){var d=cview.docs[k],last=d.pdfs[0];
      var status=!d.data?'<span class="pill pill-bad">Sem dados</span>':!last?'<span class="pill pill-warn">Dados prontos</span>':last.draft?'<span class="pill pill-warn">Rascunho</span>':'<span class="pill pill-ok">Final</span>';
      var acts=!d.data?'<button class="btn small primary" type="button" data-act="new">Criar</button>':
        (last?'<button class="btn small primary" type="button" data-act="view">Ver</button><a class="btn small" href="'+url(last.path)+'" download="'+esc(last.name)+'">Baixar PDF</a>':'')+'<button class="btn small'+(last?'':' primary')+'" type="button" data-act="build">'+(last?'Gerar de novo':'Gerar PDF')+'</button><button class="btn small" type="button" data-act="edit">Editar dados</button>';
      return '<tr data-doc="'+k+'"><td><b>'+esc(d.label)+'</b></td><td>'+status+'</td><td>'+(last?dday(last.mtime):'—')+'</td><td class="acts">'+acts+'<span class="hint" data-state aria-live="polite"></span></td></tr><tr class="ed" data-ed="'+k+'" hidden><td colspan="4"></td></tr>';
    }).join('');
    var others=cview.other_pdfs.map(function(f){return '<tr><td><b>'+esc(f.name)+'</b></td><td><span class="pill">Arquivo</span></td><td>'+dday(f.mtime)+'</td><td class="acts"><a class="btn small primary" href="'+url(f.path)+'" download="'+esc(f.name)+'">Baixar PDF</a></td></tr>'}).join('');
    var older=[];DOC_ORDER.forEach(function(k){cview.docs[k].pdfs.slice(1).forEach(function(f){older.push(f)})});
    el.innerHTML='<div class="tablewrap"><table class="doc-table"><thead><tr><th>Documento</th><th>Situação</th><th>Atualizado</th><th></th></tr></thead><tbody>'+rows+others+'</tbody></table></div>'+
      '<p class="hint">Situação <b>Rascunho</b>: ainda há [CONFIRMAR] nos dados do documento ou nos dados da agência (<code>saida/agency.json</code>).</p>'+
      (older.length?'<details class="ws-card fold"><summary>Versões anteriores ('+older.length+')</summary><div class="fold-body">'+older.map(function(f){return '<div class="row"><a class="btn small" href="'+url(f.path)+'" download="'+esc(f.name)+'">Baixar</a><span class="hint">'+esc(f.name)+' · '+dday(f.mtime)+'</span></div>'}).join('')+'</div></details>':'');
    function again(){cload().then(function(){renderDocuments(el)})}
    el.onclick=function(e){
      var btn=e.target.closest('[data-act],[data-save]');if(!btn)return;
      var tr=btn.closest('tr[data-doc]'),ed=btn.closest('tr.ed');
      var k=tr?tr.getAttribute('data-doc'):ed.getAttribute('data-ed');
      var st=tr?tr.querySelector('[data-state]'):ed.querySelector('[data-edst]');
      var post=function(a){return ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/doc/'+k+'/'+a,{method:'POST'})};
      var act=btn.getAttribute('data-act');
      if(act==='new'){post('new').then(again).catch(function(x){st.textContent=x.message})}
      else if(act==='build'){btn.disabled=true;st.textContent='gerando…';post('build').then(function(r){st.textContent=r.open?'rascunho: '+r.open+' [CONFIRMAR]':'pronto';setTimeout(again,500)}).catch(function(x){st.textContent=x.message;btn.disabled=false})}
      else if(act==='view'){var vr=el.querySelector('tr[data-ed="'+k+'"]'),lp=cview.docs[k].pdfs[0].path;
        if(!vr.hidden&&vr.querySelector('iframe')){vr.hidden=true;return}
        var src=k==='presentation'?url(lp.replace(/\.pdf$/,'.html')):url(lp);
        vr.hidden=false;vr.firstChild.innerHTML='<iframe class="doc-view" src="'+src+'" title="'+esc(cview.docs[k].label)+'"></iframe><div class="row"><a class="btn small" href="'+src+'" target="_blank" rel="noopener">Abrir em tela cheia</a></div>'}
      else if(act==='edit'){var row=el.querySelector('tr[data-ed="'+k+'"]');
        if(!row.hidden){row.hidden=true;return}
        readFile('documentos/'+k+'.json').then(function(t){row.hidden=false;row.firstChild.innerHTML='<textarea class="md-edit tall" aria-label="Dados do documento">'+esc(t)+'</textarea><div class="row"><button class="btn primary small" type="button" data-save>Salvar dados</button><span class="hint" data-edst></span></div>'})}
      else if(btn.hasAttribute('data-save')){var ta=ed.querySelector('textarea'),body;
        try{body=JSON.parse(ta.value)}catch(x){st.textContent='JSON inválido: '+x.message;return}
        ctx.api('/api/gallery/'+encodeURIComponent(ctx.gallery)+'/doc/'+k,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(){st.textContent='salvo';setTimeout(again,400)}).catch(function(x){st.textContent=x.message})}
    };
  }

  var USE_LABEL={cover:'capa',background:'fundo',detail:'detalhe',proof:'prova',team:'equipe',logo:'logo',discard:'descartada'};
  function renderCatalog(el){
    var items=cview.catalog||[],f={use:'',orient:'',q:'',all:false};
    if(!items.length){el.innerHTML='<div class="empty">Ainda não há catálogo. Copie as fotos para <code>'+esc(data.home)+'/assets/images</code> e peça ao Claude: <code>/vf-assets '+esc(cview.slug)+'</code>.</div>';return}
    function chips(key,opts){return '<div class="row">'+opts.map(function(o){return '<button class="chip" type="button" data-f="'+key+'" data-v="'+o[0]+'" aria-pressed="'+(f[key]===o[0])+'">'+o[1]+'</button>'}).join('')+'</div>'}
    function visible(){var q=f.q.toLowerCase();return items.filter(function(i){
      if(!f.all&&(i.blank||i.duplicate_of||(i.use||[]).indexOf('discard')>=0))return false;
      if(f.use&&(i.use||[]).indexOf(f.use)<0)return false;
      if(f.orient&&i.orient!==f.orient)return false;
      if(q&&(i.subject+' '+(i.tags||[]).join(' ')+' '+i.path).toLowerCase().indexOf(q)<0)return false;return true})}
    function card(i,k){var t=i.kind==='video'?'<video muted preload="metadata" src="'+url('assets/'+i.path)+'#t=1"></video>':'<img loading="lazy" alt="" src="'+url('assets/'+i.path)+'"'+((i.w/i.h)>1.6?' style="object-fit:contain;background:#fff"':'')+'>';
      var badges=[];if(i.quality==='baixa')badges.push('<span class="pill pill-warn">baixa resolução</span>');if(i.rights==='confirm')badges.push('<span class="pill">direitos a confirmar</span>');if(i.people)badges.push('<span class="pill">pessoas</span>');if(i.duplicate_of)badges.push('<span class="pill">repetida</span>');
      return '<button class="cat-card" type="button" data-i="'+k+'"><div class="cat-thumb">'+t+'</div><div class="cat-info"><b>'+esc((i.subject||i.path).slice(0,60))+'</b><div class="row">'+(i.use||[]).map(function(u){return '<span class="pill pill-ok">'+(USE_LABEL[u]||u)+'</span>'}).join('')+badges.join('')+'</div></div></button>'}
    function draw(){var v=visible();document.getElementById('cat-count').textContent=v.length+' de '+items.length+' arquivos';
      document.getElementById('cat-grid').innerHTML=v.map(function(i){return card(i,items.indexOf(i))}).join('')||'<div class="empty">Nada com esses filtros.</div>';
      [].forEach.call(el.querySelectorAll('[data-f]'),function(b){b.setAttribute('aria-pressed',f[b.getAttribute('data-f')]===b.getAttribute('data-v'))})}
    el.innerHTML='<div class="cat-bar">'+chips('use',[['','Todas'],['cover','Capa'],['background','Fundo'],['detail','Detalhe'],['proof','Prova']])+chips('orient',[['','Qualquer formato'],['vertical','Vertical'],['horizontal','Horizontal'],['square','Quadrada']])+
      '<input class="search" id="cat-q" type="search" placeholder="Buscar por assunto ou tag" aria-label="Buscar"><label class="check"><input type="checkbox" id="cat-all"> mostrar descartadas e repetidas</label></div>'+
      '<p class="hint" id="cat-count"></p><div class="cat-grid" id="cat-grid"></div>'+
      '<p class="hint">Adicionou arquivos? Copie para <code>'+esc(data.home)+'/assets/</code> e peça ao Claude: <code>/vf-assets '+esc(cview.slug)+'</code>. Direitos, uso e assunto de cada foto ficam em <code>assets/index.json</code>.</p>';
    draw();
    el.onclick=function(e){var b=e.target.closest('[data-f]');if(b){f[b.getAttribute('data-f')]=b.getAttribute('data-v');draw();return}
      var c=e.target.closest('.cat-card');if(!c)return;var i=items[+c.getAttribute('data-i')];var u=url('assets/'+i.path);
      ctx.openDoc(i.subject?i.subject.slice(0,70):i.path,(i.kind==='video'?'<video controls src="'+u+'"></video>':'<img alt="" src="'+u+'">')+
        '<table><tbody><tr><th>Uso</th><td>'+((i.use||[]).map(function(x){return USE_LABEL[x]||x}).join(', ')||'—')+'</td></tr><tr><th>Tags</th><td>'+esc((i.tags||[]).join(', ')||'—')+'</td></tr><tr><th>Tamanho</th><td>'+i.w+' × '+i.h+' · qualidade '+esc(i.quality)+'</td></tr><tr><th>Pessoas</th><td>'+(i.people===true?'sim':i.people===false?'não':'—')+'</td></tr><tr><th>Direitos</th><td>'+(i.rights==='ok'?'confirmados':'a confirmar')+'</td></tr><tr><th>Observação</th><td>'+esc(i.note||'—')+'</td></tr><tr><th>Arquivo</th><td><code>'+esc(i.path)+'</code></td></tr></tbody></table>')};
    el.oninput=function(e){if(e.target.id==='cat-q'){f.q=e.target.value;draw()}};
    el.onchange=function(e){if(e.target.id==='cat-all'){f.all=e.target.checked;draw()}};
  }

  window.Workspace={
    render:function(tab,el,context){
      ctx=context;document.onpaste=null;el.onclick=null;el.oninput=null;el.onchange=null;
      el.innerHTML='<div class="empty">carregando…</div>';
      var clientTab=!!ctx.client&&(tab==='overview'||tab==='identity'||tab==='social'||tab==='documents'||tab==='assets'||tab==='brief');
      (clientTab?cload():Promise.resolve()).then(load).then(function(){
        if(ctx.client&&tab==='overview')renderOverview(el);
        else if(ctx.client&&tab==='identity')renderIdentity(el);
        else if(ctx.client&&tab==='social')renderSocial(el);
        else if(ctx.client&&tab==='documents')renderDocuments(el);
        else if(ctx.client&&tab==='assets')renderCatalog(el);
        else if(ctx.client&&tab==='brief')renderBriefClient(el);
        else if(tab==='brief')renderBrief(el);
        else if(tab==='assets')renderAssets(el);
        else if(tab==='references')renderReferences(el);
        else if(tab==='manual')renderManual(el);
        else renderResearch(el);
      }).catch(function(e){el.innerHTML='<div class="empty">'+esc(e.message||'Ligue o painel para ver esta aba.')+'</div>'});
    },
    leave:function(){document.onpaste=null}
  };
})();
