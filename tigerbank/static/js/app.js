
// simple auto carousel
let idx = 0;
function rotateSlides(){
  const slides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  slides.forEach((s,i)=>s.classList.toggle('active', i===idx));
  dots.forEach((d,i)=>d.classList.toggle('active', i===idx));
  idx = (idx+1)%slides.length;
}
setInterval(()=>{ if(document.querySelector('.carousel-container')) rotateSlides(); }, 5000);

// ===== PIX UI =====
(function(){
  const form = document.getElementById('form-pix');
  if(!form) return;

  const chipGroup = document.getElementById('tipo-chave');
  const inputChave = document.getElementById('input-chave');
  const labelChave = document.getElementById('label-chave');
  const hintChave  = document.getElementById('hint-chave');
  const inputValor = document.getElementById('input-valor');
  const quando     = document.getElementById('quando');
  const grupoData  = document.getElementById('grupo-data');
  const inputData  = document.getElementById('input-data');

  const hiddenChave = document.getElementById('chave-hidden');
  const hiddenValor = document.getElementById('valor-hidden');
  const hiddenAg    = document.getElementById('agendado-hidden');
  const hiddenData  = document.getElementById('data-hidden');
  const inputHora  = document.getElementById('input-hora');
  const hiddenHora = document.getElementById('hora-hidden');

  let tipo = 'email';

  // chips tipo de chave
  chipGroup.querySelectorAll('.chip').forEach(chip=>{
    chip.addEventListener('click', ()=>{
      chipGroup.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));
      chip.classList.add('active');
      tipo = chip.dataset.type;
      configureKeyField(tipo);
      inputChave.focus();
    });
  });

  function configureKeyField(t){
    inputChave.value = '';
    inputChave.removeEventListener('input', maskCpfCnpj);
    inputChave.removeEventListener('input', maskCelular);

    if(t==='email'){
      labelChave.textContent = 'Chave PIX (e-mail)';
      inputChave.type = 'email';
      inputChave.placeholder = 'nome@dominio.com';
      hintChave.textContent = 'Ex.: pessoa@provedor.com';
    } else if(t==='cpf_cnpj'){
      labelChave.textContent = 'Chave PIX (CPF/CNPJ)';
      inputChave.type = 'text';
      inputChave.placeholder = '000.000.000-00 ou 00.000.000/0000-00';
      hintChave.textContent = 'Somente números serão enviados';
      inputChave.addEventListener('input', maskCpfCnpj);
    } else if(t==='celular'){
      labelChave.textContent = 'Chave PIX (celular)';
      inputChave.type = 'tel';
      inputChave.placeholder = '(11) 99999-9999';
      hintChave.textContent = 'DDD + número';
      inputChave.addEventListener('input', maskCelular);
    } else {
      labelChave.textContent = 'Chave PIX (aleatória)';
      inputChave.type = 'text';
      inputChave.placeholder = 'UUID da chave';
      hintChave.textContent = 'Cole a chave aleatória';
    }
  }
  configureKeyField(tipo);

  // máscaras simples
  function onlyDigits(s){ return (s||'').replace(/\\D+/g,''); }
  function maskCpfCnpj(e){
    let v = onlyDigits(e.target.value);
    if(v.length <= 11){
      v = v.replace(/(\\d{3})(\\d)/,'$1.$2').replace(/(\\d{3})(\\d)/,'$1.$2').replace(/(\\d{3})(\\d{1,2})$/,'$1-$2');
    } else {
      v = v.replace(/(\\d{2})(\\d)/,'$1.$2').replace(/(\\d{3})(\\d)/,'$1.$2').replace(/(\\d{3})(\\d)/,'$1/$2').replace(/(\\d{4})(\\d{1,2})$/,'$1-$2');
    }
    e.target.value = v;
  }
  function maskCelular(e){
    let v = onlyDigits(e.target.value).slice(0,11);
    v = v.replace(/(\\d{2})(\\d)/,'($1) $2').replace(/(\\d{5})(\\d{1,4})$/,'$1-$2');
    e.target.value = v;
  }

// ---- moeda BRL robusta (sem NaN)
(function(){
  const form = document.getElementById('form-pix');
  if(!form) return;

  const inputValor = document.getElementById('input-valor');
  const hiddenValor = document.getElementById('valor-hidden');

  function onlyDigits(s){ return (s || '').replace(/\D+/g,''); }

  function fmtBRL(str){
    const digits = onlyDigits(str);
    const cents  = digits === '' ? 0 : parseInt(digits, 10);
    const n = Number.isFinite(cents) ? (cents/100) : 0;
    return 'R$ ' + n.toFixed(2).replace('.', ',');
  }

  // Formata enquanto digita
  inputValor.addEventListener('input', (e)=>{
    const pos = e.target.selectionStart;
    e.target.value = fmtBRL(e.target.value);
    e.target.setSelectionRange(e.target.value.length, e.target.value.length);
  });

  // Garante formato ao focar e ao sair
  inputValor.addEventListener('focus', ()=> {
    if (onlyDigits(inputValor.value) === '') inputValor.value = 'R$ 0,00';
  });
  inputValor.addEventListener('blur', ()=> {
    inputValor.value = fmtBRL(inputValor.value);
  });

  // No submit envia número normalizado (12.34)
  form.addEventListener('submit', ()=>{
    const cents = parseInt(onlyDigits(inputValor.value) || '0', 10);
    hiddenValor.value = (cents/100).toFixed(2);
    });
  })(); 

  /* mostrar/ocultar grupo */
quando.addEventListener('change', ()=>{
  const val = form.querySelector('input[name="quando"]:checked').value;
  grupoData.style.display = val==='agendado' ? '' : 'none';
});

  // imediato x agendado
  quando.addEventListener('change', ()=>{
    const val = form.querySelector('input[name=\"quando\"]:checked').value;
    grupoData.style.display = val==='agendado' ? '' : 'none';
  });

  /* mínimo de horário quando a data é hoje */
function roundUpToNextMinutes(date, minutes) {
  const ms = minutes*60*1000;
  return new Date(Math.ceil(date.getTime()/ms)*ms);
}
function adjustMinTime() {
  if (!inputData.value) return;
  const todayISO = new Date().toISOString().slice(0,10);
  if (inputData.value === todayISO) {
    const t = roundUpToNextMinutes(new Date(), 15);
    const hh = String(t.getHours()).padStart(2,'0');
    const mm = String(t.getMinutes()).padStart(2,'0');
    inputHora.min = `${hh}:${mm}`;
    if (inputHora.value < inputHora.min) inputHora.value = inputHora.min;
  } else {
    inputHora.min = '';
  }
}
inputData && inputData.addEventListener('change', adjustMinTime);
adjustMinTime();

/* submit: persistir data e hora */
form.addEventListener('submit', (e)=>{
  e.preventDefault();
  hiddenData.value = inputData.value || '';
  hiddenHora.value = inputHora.value || '09:00';
});

  // envio normalizado
  form.addEventListener('submit', (e)=>{
    // validações básicas
    const rawValor = onlyDigits(inputValor.value);
    if(!rawValor || parseInt(rawValor,10) < 1){ e.preventDefault(); alert('Informe um valor válido.'); return; }
    if(form.querySelector('input[name=\"quando\"]:checked').value==='agendado' && !inputData.value){
      e.preventDefault(); alert('Selecione a data do agendamento.'); return;
    }

    // chave normalizada
    let chave = inputChave.value.trim();
    if(tipo==='cpf_cnpj' || tipo==='celular') chave = onlyDigits(chave);

    hiddenChave.value = chave;
    hiddenValor.value = (parseInt(rawValor,10)/100).toFixed(2); // 12.34
    hiddenAg.value    = form.querySelector('input[name=\"quando\"]:checked').value==='agendado' ? '1' : '0';
    hiddenData.value  = inputData.value || '';
  });
})();
