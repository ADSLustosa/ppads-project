/* =========================================================
        TIGERBANK APP.JS — ESTRUTURA PROFISSIONAL
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    console.log("%cTigerBank JS carregado com sucesso", "color:#ffa500; font-weight:bold;");

    /* =========================================================
                AUTO CAROUSEL
    ========================================================= */
    (function initCarousel() {
        let idx = 0;
        const rotateSlides = () => {
            const slides = document.querySelectorAll('.carousel-slide');
            const dots = document.querySelectorAll('.carousel-dot');
            if (!slides.length) return;

            slides.forEach((s, i) => s.classList.toggle('active', i === idx));
            dots.forEach((d, i) => d.classList.toggle('active', i === idx));

            idx = (idx + 1) % slides.length;
        };

        setInterval(() => {
            if (document.querySelector('.carousel-container')) rotateSlides();
        }, 5000);
    })();



    /* =========================================================
            FUNÇÕES DE MÁSCARA — CPF / CNPJ / CELULAR / REAL
    ========================================================= */
    const Mask = {
        cpf(v) {
            return v.replace(/\D/g, "")
                .slice(0, 11)
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
        },

        cnpj(v) {
            return v.replace(/\D/g, "")
                .slice(0, 14)
                .replace(/(\d{2})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d)/, "$1.$2")
                .replace(/(\d{3})(\d)/, "$1/$2")
                .replace(/(\d{4})(\d{1,2})$/, "$1-$2");
        },

        celular(v) {
            return v.replace(/\D/g, "")
                .slice(0, 11)
                .replace(/^(\d{2})(\d)/, "($1) $2")
                .replace(/(\d{5})(\d{4})$/, "$1-$2");
        },

        money(v) {
            v = v.replace(/\D/g, "");
            return "R$ " + (v / 100).toFixed(2).replace(".", ",");
        }
    };



    /* =========================================================
            MÁSCARA GLOBAL DE MOEDA (R$)
            — Funciona em todos os templates automaticamente
    ========================================================= */
    (function initGlobalMoneyMask() {

        function applyMoneyMask(e) {
            const input = e.target;
            if (!input.matches(".money-input, [data-money]")) return;
            input.value = Mask.money(input.value);
        }

        // Delegação global (pega qualquer input criado dinamicamente)
        document.addEventListener("input", applyMoneyMask);

        // Ajusta valores já existentes no carregamento
        document.querySelectorAll(".money-input, [data-money]").forEach(inp => {
            inp.value = Mask.money(inp.value);
        });

    })();



    /* =========================================================
            FORMULÁRIO DE TRANSFERÊNCIA — CPF / CNPJ
    ========================================================= */
    (function initDocMask() {
        const input = document.getElementById("doc-input");
        const tipo = document.getElementById("doc-tipo");
        const label = document.getElementById("doc-label");

        if (!input || !tipo || !label) return;

        tipo.addEventListener("change", () => {
            input.value = "";

            const config = {
                cpf: ["CPF do destinatário", "000.000.000-00"],
                cnpj: ["CNPJ do destinatário", "00.000.000/0000-00"]
            };

            const [lbl, ph] = config[tipo.value];
            label.textContent = lbl;
            input.placeholder = ph;
        });

        input.addEventListener("input", () => {
            input.value = tipo.value === "cpf"
                ? Mask.cpf(input.value)
                : Mask.cnpj(input.value);
        });
    })();



    /* =========================================================
            FORMULÁRIO PIX — CHAVES DINÂMICAS
    ========================================================= */
    (function initPixMask() {
        const tipoPix = document.getElementById("tipo-pix");
        const pixInput = document.getElementById("pix-input");
        const pixLabel = document.getElementById("pix-label");

        if (!tipoPix || !pixInput || !pixLabel) return;

        tipoPix.addEventListener("change", () => {
            pixInput.value = "";

            const tipos = {
                email: ["Chave PIX (e-mail)", "email@exemplo.com"],
                cpf: ["Chave PIX (CPF)", "000.000.000-00"],
                cnpj: ["Chave PIX (CNPJ)", "00.000.000/0000-00"],
                celular: ["Chave PIX (Celular)", "(00) 00000-0000"],
                aleatoria: ["Chave PIX Aleatória", "chave aleatória"]
            };

            const [lbl, ph] = tipos[tipoPix.value];
            pixLabel.textContent = lbl;
            pixInput.placeholder = ph;
        });

        pixInput.addEventListener("input", () => {
            const tipo = tipoPix.value;
            let v = pixInput.value;

            if (tipo === "cpf") pixInput.value = Mask.cpf(v);
            else if (tipo === "cnpj") pixInput.value = Mask.cnpj(v);
            else if (tipo === "celular") pixInput.value = Mask.celular(v);
        });

    })();

});
