/* "Aprender" section of the panel: quick start, live setup, prompt library and tips.
   Identifiers in English; user-facing text in Portuguese. */
(function(){

  var START_STEPS=[
    {id:'setup',title:'Confira as ferramentas',text:'Abra <b>Setup</b> aqui no menu. Tudo que é obrigatório precisa estar verde; o que faltar vem com o comando para instalar.',action:['setup','Abrir Setup']},
    {id:'examples',title:'Conheça os estilos',text:'Abra a <b>Biblioteca de estilos</b> e assista dois ou três estilos. Cada vídeo vem com o prompt que o gerou, a folha de aprovação, o roteiro e o storyboard.',action:['library','Abrir a biblioteca']},
    {id:'first-cli',title:'Faça um vídeo pelo terminal',text:'O teste mais rápido é o vídeo de oferta, que já vem com dados de exemplo. Rode na pasta do motor:',code:'uv run vf oferta teste --exemplo\nuv run vf oferta teste --animar'},
    {id:'first-claude',title:'Faça um vídeo com o Claude Code',text:'Abra o Claude Code na pasta do motor (<code>claude</code>) e digite <code>/vf-video &lt;estilo&gt; &lt;tema&gt;</code>. O Claude escreve o roteiro, para para você aprovar, narra, monta a folha e para de novo antes de animar.',action:['skills','Ver as skills']},
    {id:'review',title:'Aprove a folha antes do render',text:'A folha fica em <code>2-aprovar/</code> e aparece aqui no painel com o status <b>a aprovar</b>. Olhe texto cortado, ordem das cenas e cores. Pediu ajuste? Só o storyboard muda; a voz não é refeita.'},
    {id:'organize',title:'Organize em galerias',text:'Crie uma galeria por canal, cliente ou série em <b>+ Nova galeria</b>, apontando para as pastas dos jobs. O painel mostra a etapa de cada vídeo e o próximo comando.'}
  ];

  var TIPS=[
    {title:'Roteiro',items:['Gancho nos primeiros 3 segundos: pergunta, número ou contradição.','Uma frase por linha. Frase curta sincroniza melhor com as cenas.','Linha em branco antes da chamada final vira uma pausa de 0,7 s.','30 a 45 segundos rendem mais que 60 para conteúdo explicativo.','Todo número e data com duas fontes. Na dúvida, escreva de forma cautelosa.']},
    {title:'Folha e storyboard',items:['Nunca anime sem olhar a folha: render custa minutos, ajuste custa segundos.','Rode `vf checar` antes da folha: ele pega texto fora da margem e plano sem tempo.','Mudou só o storyboard? Não precisa narrar de novo.','No avatar, título é l1 e l2. "t1" é reservado para tempo.','Cartão muito alto cobre o rosto do avatar: corte conteúdo ou padding.']},
    {title:'Voz',items:['Edge para testes e lotes: rápido e grátis.','Voicebox sem placa de vídeo é lento. Use o modelo 0.6B para testar e gere a versão final uma vez só.','O cache de voz reaproveita frases iguais: mudar uma frase não refaz o áudio inteiro.','Voz clonada só da sua ou de quem autorizou por escrito. Nunca de pessoa pública, dublador ou personagem.']},
    {title:'Render e máquina',items:['Feche outros programas pesados durante o render.','Pouca memória? Narre com `--modelo small` no Whisper.','A pasta _interno pode ser apagada: o motor refaz o que precisar.','O vídeo só aparece em 3-final quando termina; nunca fica arquivo pela metade.']},
    {title:'Som',items:['Rode os scripts de dentro de ferramentas/sound-layer, com caminhos relativos e sem acento.','O qa.py aponta som abafado pela voz e som fora do movimento: ajuste o tempo do cue ou troque por um som mais brilhante.','Guarde o vídeo sem som também, para remixar depois.']},
    {title:'Avatar e imagens',items:['Use sempre a mesma folha de referência do personagem e uma só ferramenta de imagem por projeto.','Para variações de boca, use editar imagem, não gerar de novo: a pose precisa ficar idêntica.','Recorte as poses na cintura e com fundo transparente antes de usar.','Deixe livre a faixa de cima (títulos) e a de baixo (legenda) nas imagens.']},
    {title:'Organização',items:['Uma galeria por canal, cliente ou série.','Cores, logo e fotos de marca ficam na pasta do job ou do seu projeto, nunca dentro do motor.','saida/ e galleries.json ficam fora do git: cada pessoa tem os seus.','Uma sessão nova do Claude por vídeo evita carregar contexto de outro trabalho.']}
  ];

  var ERRORS=[
    ['"rode antes `vf narrate`"','Falta narração ou o nome do job veio com saida/ na frente. Use só o nome: `vf storyboard meu-video`.'],
    ['Erro do ffmpeg com caminho','Pasta com acento ou espaço em algum script. Rode de dentro da pasta e use caminho relativo.'],
    ['Whisper estoura a memória','Narre de novo com `--modelo small`.'],
    ['Vídeo não toca no guia','Abra o guide.html de dentro da pasta do motor, ou pelo painel em Guia completo.'],
    ['Painel diz "servidor desligado"','Rode `uv run vf panel` na pasta do motor e deixe o terminal aberto.']
  ];

  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function codeBlock(text,label){return '<div class="code-block"><div class="code-bar"><span>'+esc(label||'PowerShell')+'</span><button class="btn small" type="button" data-copy>Copiar</button></div><pre>'+esc(text)+'</pre></div>'}
  function readSteps(){try{return JSON.parse(localStorage.getItem('vf-panel-start')||'{}')}catch(e){return {}}}
  function saveSteps(v){try{localStorage.setItem('vf-panel-start',JSON.stringify(v))}catch(e){}}

  function renderStart(el){
    var done=readSteps(),n=START_STEPS.filter(function(s){return done[s.id]}).length;
    el.innerHTML='<div class="learn-head"><h1>Começar</h1><p class="lede">Seis passos do zero ao primeiro vídeo organizado. Marque conforme avança; fica salvo neste navegador.</p><div class="progress"><div class="track"><i style="width:'+(100*n/START_STEPS.length)+'%"></i></div><span>'+n+' de '+START_STEPS.length+' feitos</span></div></div>'+
      '<ol class="learn-steps">'+START_STEPS.map(function(s){
        return '<li class="'+(done[s.id]?'done':'')+'"><div><h3>'+s.title+'</h3><p>'+s.text+'</p>'+(s.code?codeBlock(s.code):'')+
          '<div class="row"><label class="check"><input type="checkbox" data-step="'+s.id+'"'+(done[s.id]?' checked':'')+'> Feito</label>'+(s.action?'<button class="btn small" type="button" data-go="'+s.action[0]+'">'+s.action[1]+'</button>':'')+'</div></div></li>';
      }).join('')+'</ol>';
  }

  function renderSetup(el,api){
    el.innerHTML='<div class="learn-head"><h1>Setup</h1><p class="lede">Verificação ao vivo nesta máquina. O que faltar vem com o comando para resolver; depois de instalar, feche e abra o terminal e clique em Verificar de novo.</p><div class="row"><button class="btn" type="button" data-recheck>Verificar de novo</button><span class="hint" id="setup-summary">verificando…</span></div></div><div class="setup-list" id="setup-list"></div>'+
      '<div class="tip-card"><h3>Instalação do zero (Windows)</h3>'+codeBlock('winget install astral-sh.uv\nwinget install Gyan.FFmpeg\nwinget install OpenJS.NodeJS.LTS\nwinget install Git.Git\nnpm install -g pnpm\n# feche e abra o terminal\ngit clone https://github.com/ghgalvao/videofactory.git\ncd videofactory\nuv sync\ncd video; pnpm install; cd ..\nuv run vf panel')+'</div>';
    api('/api/setup').then(function(j){
      var req=j.items.filter(function(i){return i.required}),ok=req.filter(function(i){return i.ok}).length;
      document.getElementById('setup-summary').textContent=ok+' de '+req.length+' obrigatórios prontos'+(ok===req.length?' · pode produzir':'');
      document.getElementById('setup-list').innerHTML=j.items.map(function(i){
        var pill=i.ok?'<span class="status s-ready">pronto</span>':i.required?'<span class="status s-script">falta</span>':'<span class="status">opcional</span>';
        return '<div class="setup-item'+(i.ok?'':' missing')+'"><div class="setup-top"><b>'+esc(i.name)+'</b>'+pill+'</div><p class="hint">'+esc(i.use)+'</p><code>'+esc(i.detail)+'</code>'+(i.fix?codeBlock(i.fix,'Para resolver'):'')+'</div>';
      }).join('');
    }).catch(function(){document.getElementById('setup-summary').textContent='Servidor desligado: rode `uv run vf panel`.'});
  }

  var examples=[];
  function niceName(n){n=n.replace(/^e\d+b?-/,'').replace(/-/g,' ');return n.charAt(0).toUpperCase()+n.slice(1)}
  function md(text){
    if(window.MD)return '<div class="md">'+window.MD.render(text)+'</div>';
    var lines=esc(text).split('\n'),out=[],list=null;
    function inline(s){return s.replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>').replace(/`([^`]+)`/g,'<code>$1</code>')}
    lines.forEach(function(raw){
      var line=raw.trim(),num=line.match(/^\d+\.\s+(.*)/),bul=line.match(/^[-*]\s+(.*)/);
      if(num||bul){var tag=num?'ol':'ul';if(list!==tag){if(list)out.push('</'+list+'>');out.push('<'+tag+'>');list=tag}out.push('<li>'+inline((num||bul)[1])+'</li>');return}
      if(list&&raw.match(/^\s{2,}\S/)){out[out.length-1]=out[out.length-1].replace(/<\/li>$/,' '+inline(line)+'</li>');return}
      if(list){out.push('</'+list+'>');list=null}
      if(line)out.push('<p>'+inline(line)+'</p>');
    });
    if(list)out.push('</'+list+'>');
    return out.join('');
  }
  function renderSkills(el,api){
    el.innerHTML='<div class="learn-head"><h1>Skills</h1><p class="lede">Comandos do Claude Code que vêm com o motor (pasta <code>.claude/skills</code>). Abra o Claude Code na pasta do motor e digite o comando; ele conduz o trabalho e para nos portões de aprovação. Para ver vídeos prontos e o pedido que gerou cada um, abra a <button class="link" type="button" data-go="library">Biblioteca</button>.</p></div>'+
      '<div class="skills-grid" id="skills-grid"><div class="empty">carregando…</div></div>';
    api('/api/skills').then(function(r){
      document.getElementById('skills-grid').innerHTML=r.skills.map(function(s){
        return '<article class="skill"><div class="skill-head"><h3><code>/'+esc(s.name)+'</code></h3>'+(s.args?'<span class="hint">'+esc(s.args)+'</span>':'')+'</div>'+
          '<p>'+esc(s.when||s.description)+'</p>'+
          (s.examples.length?codeBlock(s.examples.join('\n'),'Exemplos'):'')+
          '<details><summary>O que faz</summary><div class="skill-doc">'+md(s.steps)+(s.output?'<h4>Entrega</h4>'+md(s.output):'')+(s.rules?'<h4>Regras</h4>'+md(s.rules):'')+'<p class="hint">Arquivo: <code>'+esc(s.path)+'</code></p></div></details></article>';
      }).join('')||'<div class="empty">Nenhuma skill em .claude/skills.</div>';
    }).catch(function(){document.getElementById('skills-grid').innerHTML='<div class="empty">Ligue o painel para ver as skills.</div>'});
  }

  var styleList=[];
  function styleName(key){var s=styleList.find(function(x){return x.key===key});return s?s.name:key}
  function redundant(s){var a=s.use.toLowerCase(),n=s.name.toLowerCase(),d=(s.detail||'').toLowerCase();return n.indexOf(a)>=0||a.indexOf(n)>=0||(d&&(d.indexOf(a)>=0||a.indexOf(d)>=0))}
  var STATUS_LABEL={tested:'testado',ready:'pronto',recipe:'só receita'};
  function renderLibrary(el,api){
    el.innerHTML='<div class="learn-head"><h1>Biblioteca de estilos</h1><p class="lede">Os estilos do motor e vídeos feitos com eles. Escolha um estilo e crie um vídeo, ou parta de um exemplo pronto copiando o pedido que o gerou.</p></div>'+
      '<div class="filters" id="style-kind"><button class="chip" type="button" data-kind="all" aria-pressed="true">Todos</button><button class="chip" type="button" data-kind="content" aria-pressed="false">Conteúdo</button><button class="chip" type="button" data-kind="business" aria-pressed="false">Empresa</button></div>'+
      '<h2 class="learn-h2">Estilos</h2><div class="style-cards" id="style-cards"><div class="empty">carregando…</div></div>'+
      '<h2 class="learn-h2">Exemplos e o pedido de cada um</h2>'+
      '<div class="row"><input class="search" id="lib-search" type="search" placeholder="Buscar exemplo" aria-label="Buscar exemplo"></div>'+
      '<div class="example-cards" id="example-cards"><div class="empty">carregando…</div></div>';
    var kind='all',style='all',q='';
    function drawStyles(){
      document.getElementById('style-cards').innerHTML=styleList.filter(function(s){return kind==='all'||s.kind===kind}).map(function(s){
        var cover=s.example?'<video muted preload="metadata" playsinline src="/styles/'+s.example.video+'#t=1.5"></video>':'<span>sem exemplo ainda</span>';
        return '<article class="style-card"><div class="style-cover">'+cover+'<span class="status">'+(s.kind==='business'?'empresa':'conteúdo')+' · '+s.format+'</span></div>'+
          '<div class="style-body"><h3>'+esc(s.name)+'</h3>'+(s.detail?'<p class="hint">'+esc(s.detail)+'</p>':'')+(redundant(s)?'':'<p>'+esc(s.use.charAt(0).toUpperCase()+s.use.slice(1))+'</p>')+
          '<div class="row"><span class="tag-s s-'+s.status+'">'+STATUS_LABEL[s.status]+'</span>'+
          (s.creatable?'<button class="btn small" type="button" data-new-style="'+esc(s.key)+'">Novo vídeo</button>':'<span class="hint">use com /vf-avatar</span>')+
          (s.example?'<button class="btn small" type="button" data-show-style="'+esc(s.key)+'">Ver exemplos</button>':'')+'</div></div></article>';
      }).join('');
    }
    function drawExamples(){
      var list=examples.map(function(it,k){return [it,k]}).filter(function(p){var it=p[0];return (style==='all'||it.style===style)&&(kind==='all'||(styleList.find(function(s){return s.key===it.style})||{}).kind===kind)&&(!q||(it.name+' '+styleName(it.style)+' '+it.prompt).toLowerCase().indexOf(q)>=0)});
      document.getElementById('example-cards').innerHTML=list.map(function(p){
        var it=p[0],k=p[1],src='/file?g=examples&b='+it.base+'&p='+encodeURIComponent(it.files.video)+'#t=1.5';
        return '<div class="example-card"><div class="cover"><video muted preload="metadata" playsinline src="'+src+'"></video><span class="status">'+esc(styleName(it.style))+'</span></div>'+
          '<div class="example-body"><h3>'+esc(niceName(it.name))+'</h3>'+codeBlock(it.prompt,'Pedido')+'<div class="row"><button class="btn small" type="button" data-example="'+k+'">Assistir e ver a folha</button></div></div></div>';
      }).join('')||'<div class="empty">Nenhum exemplo com esse filtro.</div>';
    }
    Promise.all([api('/api/styles'),api('/api/gallery/examples')]).then(function(r){
      styleList=r[0].styles;examples=r[1].items.filter(function(it){return it.prompt});drawStyles();drawExamples();
    }).catch(function(){document.getElementById('style-cards').innerHTML='<div class="empty">Ligue o painel para ver a biblioteca.</div>';document.getElementById('example-cards').innerHTML=''});
    document.getElementById('lib-search').addEventListener('input',function(e){q=e.target.value.toLowerCase();drawExamples()});
    document.getElementById('style-kind').addEventListener('click',function(e){var b=e.target.closest('[data-kind]');if(!b)return;kind=b.getAttribute('data-kind');style='all';[].forEach.call(this.children,function(x){x.setAttribute('aria-pressed',x===b)});drawStyles();drawExamples()});
    document.getElementById('style-cards').addEventListener('click',function(e){
      var s=e.target.closest('[data-show-style]');
      if(s){style=s.getAttribute('data-show-style');drawExamples();document.getElementById('example-cards').scrollIntoView({behavior:'smooth',block:'start'})}
    });
  }

  function renderTips(el){
    el.innerHTML='<div class="learn-head"><h1>Dicas</h1><p class="lede">O que aprendemos fazendo os vídeos de exemplo.</p></div>'+
      '<div class="tips-grid">'+TIPS.map(function(t){return '<div class="tip-card"><h3>'+t.title+'</h3><ul>'+t.items.map(function(i){return '<li>'+esc(i).replace(/`([^`]+)`/g,'<code>$1</code>')+'</li>'}).join('')+'</ul></div>'}).join('')+'</div>'+
      '<h2 class="learn-h2">Erros comuns</h2><div class="errors">'+ERRORS.map(function(e){return '<div class="error-row"><b>'+esc(e[0])+'</b><span>'+esc(e[1]).replace(/`([^`]+)`/g,'<code>$1</code>')+'</span></div>'}).join('')+'</div>';
  }

  window.Learn={
    render:function(view,el,api){
      if(view==='start')renderStart(el);
      else if(view==='setup')renderSetup(el,api);
      else if(view==='skills')renderSkills(el,api);
      else if(view==='library')renderLibrary(el,api);
      else renderTips(el);
    },
    toggleStep:function(id,on){var d=readSteps();d[id]=on;saveSteps(d)},
    example:function(k){return examples[+k]||null},
    md:function(t){return md(t)}
  };
})();
