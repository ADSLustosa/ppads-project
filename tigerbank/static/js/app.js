
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

// ========== PIX ==========
(function () {
  const form = document.getElementById('form-pix');
  if (!form) return;

  const chipGroup  = document.getElementById('tipo-chave');
  const inputChave = document.getElementById('input-chave');
  const labelChave = document.getElementById('label-chave');
  const hintChave  = document.getElementById('hint-chave');

  const inputValor = document.getElementById('input-valor');

  const quando    = document.getElementById('quando');
  const grupoData = document.getElementById('grupo-data');
  const inputData = document.getElementById('input-data');
  const inputHora = document.getElementById('input-hora');

  const hChave = document.getElementById('chave-hidden');
  const hValor = document.getElementById('valor-hidden');
  const hAg    = document.getElementById('agendado-hidden');
  const hData  = document.getElementById('data-hidden');
  const hHora  = document.getElementById('hora-hidden');

  const onlyDigits = (s)=> String(s||'').replace(/\D+/g,'');
  let tipo = 'email';

  // tipo de chave
  function setKeyUI(t){
    inputChave.value = '';
    inputChave.type = (t === 'email') ? 'email' : 'text';
    if (t === 'email'){
      labelChave.textContent = 'Chave PIX (e-mail)';
      inputChave.placeholder = 'nome@dominio.com';
      hintChave.textContent = 'Ex.: pessoa@provedor.com';
    } else if (t === 'cpf_cnpj'){
      labelChave.textContent = 'Chave PIX (CPF/CNPJ)';
      inputChave.placeholder = '000.000.000-00 ou 00.000.000/0000-00';
    } else if (t === 'celular'){
      labelChave.textContent = 'Chave PIX (celular)';
      inputChave.placeholder = '(11) 99999-9999';
    } else {
      labelChave.textContent = 'Chave PIX (aleatória)';
      inputChave.placeholder = 'UUID da chave';
      hintChave.textContent = 'Cole a chave aleatória';
    }
  }
  chipGroup.querySelectorAll('.chip').forEach(chip=>{
    chip.addEventListener('click', ()=>{
      chipGroup.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));
      chip.classList.add('active');
      tipo = chip.dataset.type;
      setKeyUI(tipo);
      inputChave.focus();
    });
  });
  setKeyUI(tipo);

  // moeda BRL
  function fmtBRL(str){
    const d = onlyDigits(str);
    const cents = d ? parseInt(d,10) : 0;
    return 'R$ ' + (cents/100).toFixed(2).replace('.',',');
  }
  inputValor.addEventListener('input', e=>{
    e.target.value = fmtBRL(e.target.value);
    e.target.setSelectionRange(e.target.value.length, e.target.value.length);
  });
  inputValor.addEventListener('focus', ()=>{
    if (onlyDigits(inputValor.value)==='') inputValor.value = 'R$ 0,00';
  });
  inputValor.addEventListener('blur', ()=>{
    inputValor.value = fmtBRL(inputValor.value);
  });

  // quando
  quando.addEventListener('change', ()=>{
    const v = form.querySelector('input[name="quando"]:checked').value;
    grupoData.style.display = v === 'agendado' ? '' : 'none';
  });

  // min time se data=hoje
  function roundUp(date, minutes){
    const ms = minutes*60*1000;
    return new Date(Math.ceil(date.getTime()/ms)*ms);
  }
  function adjustMinTime(){
    if (!inputData.value) return;
    const todayISO = new Date().toISOString().slice(0,10);
    if (inputData.value === todayISO){
      const t = roundUp(new Date(), 15);
      inputHora.min = `${String(t.getHours()).padStart(2,'0')}:${String(t.getMinutes()).padStart(2,'0')}`;
      if (inputHora.value < inputHora.min) inputHora.value = inputHora.min;
    } else {
      inputHora.min = '';
    }
  }
  inputData && inputData.addEventListener('change', adjustMinTime);
  adjustMinTime();

  // submit
  form.addEventListener('submit', (e)=>{
    const rawValor = onlyDigits(inputValor.value);
    if (!rawValor || parseInt(rawValor,10) < 1){
      e.preventDefault(); alert('Informe um valor válido.'); return;
    }

    const agendado = form.querySelector('input[name="quando"]:checked').value === 'agendado';
    if (agendado && (!inputData.value || !inputHora.value)){
      e.preventDefault(); alert('Selecione data e horário.'); return;
    }
    if (!inputChave.value.trim()){
      e.preventDefault(); alert('Informe a chave PIX.'); return;
    }

    let chave = inputChave.value.trim();
    if (tipo==='cpf_cnpj' || tipo==='celular') chave = onlyDigits(chave);

    hChave.value = chave;
    hValor.value = (parseInt(rawValor,10)/100).toFixed(2);
    hAg.value    = agendado ? '1' : '0';
    hData.value  = agendado ? inputData.value : '';
    hHora.value  = agendado ? (inputHora.value || '09:00') : '09:00';
    // deixa seguir o submit
  });
})();