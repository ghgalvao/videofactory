/* New-gallery wizard: pick what you are creating, answer a few questions, get a brief (gallery PRD).
   Gamified: every answer earns points and raises the brief level. Identifiers in English, text in Portuguese. */
(function(){
  var TYPES=[
    {id:'channel',label:'Canal de vídeo',hint:'YouTube, TikTok, Reels: conteúdo recorrente com a mesma cara'},
    {id:'social',label:'Página ou perfil',hint:'Instagram, LinkedIn: posts, carrosséis e vídeos curtos'},
    {id:'brand',label:'Marca',hint:'identidade de um produto ou empresa: logo, cores, tom'},
    {id:'client',label:'Cliente',hint:'trabalho para alguém: entregas, aprovador e prazos'},
    {id:'campaign',label:'Campanha',hint:'lançamento ou oferta com período e peças definidas'},
    {id:'series',label:'Série',hint:'conjunto de episódios sobre um tema'}
  ];
  var COMMON=[
    {id:'goal',label:'Objetivo',ask:'O que esta galeria precisa alcançar?',ph:'ex.: atrair clientes para a loja online',area:true,pts:15},
    {id:'audience',label:'Público',ask:'Quem assiste ou lê? O que já sabe e o que quer?',ph:'ex.: adultos de 25 a 40 curiosos por ciência',area:true,pts:15},
    {id:'tone',label:'Tom de voz',ask:'Como fala?',ph:'ex.: direto, bem-humorado, sem termos técnicos',pts:10},
    {id:'avoid',label:'Evitar',ask:'O que não pode aparecer de jeito nenhum?',ph:'ex.: promessa de resultado rápido, palavrão',pts:5}
  ];
  var QUESTIONS={
    channel:[
      {id:'theme',label:'Tema do canal',ask:'Sobre o que é o canal, em uma frase?',ph:'ex.: curiosidades de ciência em 1 minuto',pts:10},
      {id:'platforms',label:'Plataformas',ask:'Onde vai publicar?',chips:['YouTube','YouTube Shorts','TikTok','Instagram Reels','Kwai'],pts:5},
      {id:'format',label:'Formato',ask:'Vídeos curtos, longos ou os dois?',chips:['Curto (até 60 s)','Médio (1 a 3 min)','Longo (5 min+)'],pts:5},
      {id:'frequency',label:'Frequência',ask:'Quantos vídeos por semana?',ph:'ex.: 3 por semana',pts:5},
      {id:'host',label:'Apresentador',ask:'Quem aparece ou narra? Personagem, avatar, voz?',ph:'ex.: mascote ilustrado com voz do Edge',pts:10},
      {id:'styles',label:'Estilos preferidos',ask:'Quais estilos do motor combinam?',chips:['paper','whiteboard','stick-figure','animated-caption','pixel-avatar','ken-burns','data-infographic','mechanism-3d'],pts:5},
      {id:'topics',label:'Primeiros temas',ask:'Liste de 3 a 5 temas para começar.',ph:'um por linha',area:true,pts:15}
    ],
    social:[
      {id:'niche',label:'Nicho',ask:'Qual é o assunto da página?',ph:'ex.: receitas rápidas para a semana',pts:10},
      {id:'platforms',label:'Plataformas',ask:'Onde vai publicar?',chips:['Instagram','LinkedIn','TikTok','Facebook','Pinterest'],pts:5},
      {id:'formats',label:'Formatos',ask:'Que tipos de post?',chips:['Carrossel','Reels','Stories','Post único','Vídeo longo'],pts:5},
      {id:'pillars',label:'Pilares de conteúdo',ask:'Quais 3 ou 4 assuntos se repetem?',ph:'ex.: dica rápida, mito ou verdade, bastidores',area:true,pts:10},
      {id:'frequency',label:'Frequência',ask:'Quantos posts por semana?',ph:'ex.: 4 por semana',pts:5},
      {id:'topics',label:'Primeiros temas',ask:'Liste de 3 a 5 temas para começar.',ph:'um por linha',area:true,pts:15}
    ],
    brand:[
      {id:'product',label:'O que vende',ask:'Produto ou serviço, em uma frase.',ph:'ex.: sistema de gestão para lanchonetes',pts:10},
      {id:'edge',label:'Diferencial',ask:'Por que escolher esta marca e não outra?',area:true,pts:10},
      {id:'values',label:'Valores',ask:'Três palavras que a marca precisa transmitir.',ph:'ex.: simples, confiável, rápido',pts:5},
      {id:'competitors',label:'Concorrentes',ask:'Quem são os concorrentes ou referências?',ph:'nomes ou links',pts:5},
      {id:'applications',label:'Onde a marca aparece',ask:'Em que peças a marca vai ser usada?',chips:['App ou site','Redes sociais','Vídeos','Impressos','Embalagem','Fachada'],pts:5}
    ],
    client:[
      {id:'company',label:'Empresa',ask:'Nome e ramo do cliente.',ph:'ex.: indústria de equipamentos de cozinha',pts:10},
      {id:'product',label:'Produto ou serviço',ask:'O que vamos divulgar?',pts:10},
      {id:'deliverables',label:'Entregas',ask:'O que foi combinado entregar?',chips:['Vídeos','Carrosséis','Banners','Impressos','Manual de marca'],pts:10},
      {id:'approver',label:'Quem aprova',ask:'Quem dá o ok final do lado do cliente?',ph:'cargo ou nome',pts:5},
      {id:'deadline',label:'Prazo',ask:'Prazo e ritmo de entregas.',ph:'ex.: 4 vídeos por mês, entrega toda sexta',pts:5},
      {id:'restrictions',label:'Restrições',ask:'O que o cliente não aceita?',area:true,pts:5}
    ],
    campaign:[
      {id:'offer',label:'Oferta',ask:'O que está sendo lançado ou oferecido?',ph:'ex.: plano anual com 30% de desconto',pts:10},
      {id:'period',label:'Período',ask:'Quando começa e quando acaba?',ph:'ex.: 01/12 a 15/12',pts:5},
      {id:'pieces',label:'Peças',ask:'Quais peças a campanha precisa?',chips:['Vídeo curto','Carrossel','Banner','Story','Impresso','E-mail'],pts:10},
      {id:'cta',label:'Chamada',ask:'O que a pessoa deve fazer ao ver?',ph:'ex.: chamar no WhatsApp',pts:10},
      {id:'goal_number',label:'Meta',ask:'Como vamos saber se deu certo?',ph:'ex.: 50 conversas no WhatsApp',pts:5}
    ],
    series:[
      {id:'theme',label:'Tema da série',ask:'Sobre o que é a série?',ph:'ex.: como funcionam os eletrodomésticos',pts:10},
      {id:'episodes',label:'Episódios',ask:'Quantos episódios e de quanto tempo?',ph:'ex.: 6 episódios de 40 s',pts:5},
      {id:'structure',label:'Estrutura',ask:'O que se repete em todo episódio?',ph:'ex.: abre com um erro comum, explica, fecha com a regra',area:true,pts:10},
      {id:'styles',label:'Estilo',ask:'Qual estilo do motor?',chips:['paper','whiteboard','stick-figure','animated-caption','pixel-avatar','ken-burns','data-infographic'],pts:5},
      {id:'topics',label:'Episódios',ask:'Liste o tema de cada episódio.',ph:'um por linha',area:true,pts:15}
    ]
  };
  var LEVELS=[[0,'Rascunho'],[40,'Esboço'],[80,'Bem definido'],[120,'Pronto pra produzir']];
  var st=null;

  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
  function slug(t){return t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')}
  function questions(){return st.type?QUESTIONS[st.type].concat(COMMON):[]}
  function answered(q){var v=st.answers[q.id];return Array.isArray(v)?v.length>0:!!(v&&String(v).trim())}
  function points(){
    var p=st.name?10:0;
    questions().forEach(function(q){if(answered(q))p+=q.pts});
    if(st.colors.some(function(c){return c})) p+=10;
    if(st.cta)p+=5;
    return p;
  }
  function maxPoints(){return 10+questions().reduce(function(a,q){return a+q.pts},0)+15}
  function level(p){var l=LEVELS[0][1];LEVELS.forEach(function(x){if(p>=x[0])l=x[1]});return l}

  var STEPS=['Tipo','Nome','Perguntas','Identidade','Revisão'];
  function header(){
    var p=points(),m=maxPoints(),pct=st.type?Math.min(100,Math.round(100*p/m)):0;
    return '<div class="wz-head"><div class="wz-steps">'+STEPS.map(function(s,i){return '<span class="wz-step'+(i===st.step?' on':'')+(i<st.step?' done':'')+'">'+(i+1)+'. '+s+'</span>'}).join('')+'</div>'+
      '<div class="wz-xp"><b>'+p+' pts</b><span>'+level(p)+'</span><div class="progress"><div class="track"><i style="width:'+pct+'%"></i></div></div></div></div>';
  }
  function render(){
    var body='',el=document.getElementById('wizard-body');
    if(st.step===0){
      body='<h2>O que você está criando?</h2><p class="hint">Cada tipo tem perguntas próprias. Dá para mudar depois no brief.</p><div class="wz-types">'+
        TYPES.map(function(t){return '<button type="button" class="wz-type'+(st.type===t.id?' on':'')+'" data-type="'+t.id+'"><b>'+t.label+'</b><span>'+t.hint+'</span></button>'}).join('')+'</div>';
    }else if(st.step===1){
      body='<h2>Nome e pasta</h2><label>Nome<input id="wz-name" value="'+esc(st.name)+'" placeholder="ex.: Canal de Ciência"></label>'+
        '<label>Pasta<input id="wz-folder" value="'+esc(st.folder)+'" placeholder="saida/nome"></label><p class="hint">Criada sozinha dentro de <code>saida/</code>. É aqui que ficam o brief, a identidade, os assets, as referências e os jobs.</p>';
    }else if(st.step===2){
      var qs=questions();
      body='<h2>Perguntas</h2><p class="hint">Responda o que já souber: cada resposta vale pontos e deixa os vídeos mais certeiros. O resto você completa depois.</p>'+
        qs.map(function(q){
          var v=st.answers[q.id],ok=answered(q),input;
          if(q.chips)input='<div class="wz-chips">'+q.chips.map(function(c){return '<button type="button" class="chip" data-chip="'+q.id+'" data-value="'+esc(c)+'" aria-pressed="'+((v||[]).indexOf(c)>=0)+'">'+esc(c)+'</button>'}).join('')+'</div>';
          else if(q.area)input='<textarea data-q="'+q.id+'" rows="3" placeholder="'+esc(q.ph||'')+'">'+esc(v||'')+'</textarea>';
          else input='<input data-q="'+q.id+'" value="'+esc(v||'')+'" placeholder="'+esc(q.ph||'')+'">';
          return '<div class="wz-q'+(ok?' ok':'')+'"><div class="setup-top"><b>'+q.ask+'</b><span class="wz-pts">'+(ok?'✓ ':'+')+q.pts+'</span></div>'+input+'</div>';
        }).join('');
    }else if(st.step===3){
      body='<h2>Identidade (opcional)</h2><p class="hint">Cores e chamada final já entram nos vídeos. Logo e fontes você completa depois na aba Brief.</p>'+
        '<div class="field-title">Cores principais</div><div class="wz-colors">'+[0,1,2].map(function(i){return '<label class="wz-color"><input type="color" data-color="'+i+'" value="'+(st.colors[i]||['#2d6be0','#14171d','#f3ecdf'][i])+'"><input type="checkbox" data-use-color="'+i+'"'+(st.colors[i]?' checked':'')+'> usar</label>'}).join('')+'</div>'+
        '<label>Chamada final<input id="wz-cta" value="'+esc(st.cta)+'" placeholder="ex.: Segue pra mais dicas"></label>';
    }else{
      body='<h2>Revisão</h2><p class="hint">Este é o brief que o agente vai ler antes de criar qualquer coisa aqui. Pode editar antes de criar.</p>'+
        '<textarea id="wz-brief" class="brief-text">'+esc(briefText())+'</textarea>'+
        '<div class="wz-final"><b>'+level(points())+'</b> · '+points()+' de '+maxPoints()+' pontos'+(points()<maxPoints()?' · dá para completar depois na aba Brief':'')+'</div>';
    }
    var nav='<div class="row wz-nav">'+(st.step>0?'<button class="btn" type="button" id="wz-back">Voltar</button>':'')+
      '<button class="btn" type="button" id="wz-cancel">Cancelar</button>'+
      (st.step<4?'<button class="btn primary" type="button" id="wz-next"'+((st.step===0&&!st.type)||(st.step===1&&!st.name.trim())?' disabled':'')+'>Continuar</button>':'<button class="btn primary" type="button" id="wz-create">Criar galeria</button>')+
      '<span class="error" id="wz-error" aria-live="polite"></span></div>';
    el.innerHTML=header()+'<div class="wz-body">'+body+'</div>'+nav;
  }
  function briefText(){
    var t=TYPES.find(function(x){return x.id===st.type}),a=st.answers,out=['# '+st.name,'','## Tipo',t?t.label:''];
    questions().forEach(function(q){
      var v=a[q.id];if(!answered(q))return;
      v=Array.isArray(v)?v.join(', '):String(v).trim();
      if(q.id==='topics'||q.id==='pillars')v=v.split(/\n+/).map(function(l,i){return (i+1)+'. '+l.replace(/^\d+[.)]\s*/,'')}).join('\n');
      out.push('','## '+q.label,v);
    });
    var missing=questions().filter(function(q){return !answered(q)}).map(function(q){return q.label});
    if(missing.length)out.push('','## A completar',missing.map(function(m){return '- '+m}).join('\n'));
    return out.join('\n')+'\n';
  }
  function collect(){
    var el=document.getElementById('wizard-body');
    if(st.step===1){st.name=el.querySelector('#wz-name').value;st.folder=el.querySelector('#wz-folder').value.trim()}
    if(st.step===2)[].forEach.call(el.querySelectorAll('[data-q]'),function(i){st.answers[i.getAttribute('data-q')]=i.value});
    if(st.step===3){[0,1,2].forEach(function(i){st.colors[i]=el.querySelector('[data-use-color="'+i+'"]').checked?el.querySelector('[data-color="'+i+'"]').value:''});st.cta=el.querySelector('#wz-cta').value.trim()}
    if(st.step===4)st.brief=el.querySelector('#wz-brief').value;
  }
  function create(ctx){
    var err=document.getElementById('wz-error'),btn=document.getElementById('wz-create');
    btn.disabled=true;err.textContent='criando…';
    var folder=st.folder||('saida/'+(slug(st.name)||'galeria'));
    var list=ctx.userGalleries().concat([{name:st.name.trim(),folders:[folder]}]);
    ctx.saveGalleries(list).then(function(){
      var g=ctx.findGallery(st.name.trim());
      if(!g)throw new Error('galeria criada, mas não encontrei o id');
      var base='/api/gallery/'+encodeURIComponent(g.id),json={'Content-Type':'application/json'};
      var colors=st.colors.filter(Boolean).map(function(h,i){return {name:['principal','apoio','fundo'][i],hex:h}});
      return ctx.api(base+'/brief',{method:'PUT',headers:json,body:JSON.stringify({text:st.brief})})
        .then(function(){return ctx.api(base+'/brand',{method:'PUT',headers:json,body:JSON.stringify({name:st.name.trim(),colors:colors,cta:st.cta,voice:[],avoid:[]})})})
        .then(function(){document.getElementById('wizard').close();ctx.afterCreate(g.id)});
    }).catch(function(e){err.textContent=e.message;btn.disabled=false});
  }

  window.Wizard={
    open:function(ctx){
      st={step:0,type:'',name:'',folder:'',answers:{},colors:['','',''],cta:'',brief:''};
      var dlg=document.getElementById('wizard');render();dlg.showModal();
      var el=document.getElementById('wizard-body');
      el.onclick=function(e){
        var t=e.target.closest('[data-type]');if(t){st.type=t.getAttribute('data-type');render();return}
        var c=e.target.closest('[data-chip]');
        if(c){var id=c.getAttribute('data-chip'),v=c.getAttribute('data-value'),arr=st.answers[id]||[];collect();
          st.answers[id]=arr.indexOf(v)>=0?arr.filter(function(x){return x!==v}):arr.concat([v]);render();return}
        if(e.target.id==='wz-next'){collect();if(st.step===1&&!st.folder)st.folder='saida/'+(slug(st.name)||'galeria');st.step++;render();return}
        if(e.target.id==='wz-back'){collect();st.step--;render();return}
        if(e.target.id==='wz-cancel'){dlg.close();return}
        if(e.target.id==='wz-create'){collect();create(ctx)}
      };
      el.oninput=function(e){
        if(e.target.id==='wz-name'){st.name=e.target.value;var n=document.getElementById('wz-next');if(n)n.disabled=!st.name.trim();
          var f=document.getElementById('wz-folder');if(f&&(!f.dataset.touched))f.value='saida/'+slug(st.name);}
        if(e.target.id==='wz-folder')e.target.dataset.touched='1';
        if(e.target.hasAttribute('data-q')){var q=e.target.getAttribute('data-q');st.answers[q]=e.target.value;
          var box=e.target.closest('.wz-q'),ok=!!e.target.value.trim(),pts=box.querySelector('.wz-pts');box.classList.toggle('ok',ok);
          var qq=questions().find(function(x){return x.id===q});pts.textContent=(ok?'✓ ':'+')+qq.pts;
          var head=el.querySelector('.wz-head');head.outerHTML=header();}
      };
    }
  };
})();
