// Validações (CPF/CNPJ) e formatação. Porta a lógica que faltava no utils/ do projeto original.
window.App = window.App || {};

(function () {
  function digits(s) {
    return String(s == null ? "" : s).replace(/\D/g, "");
  }

  function cpfValido(cpf) {
    cpf = digits(cpf);
    if (cpf.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cpf)) return false; // todos iguais
    let soma = 0;
    for (let i = 0; i < 9; i++) soma += parseInt(cpf[i], 10) * (10 - i);
    let d1 = (soma * 10) % 11;
    if (d1 === 10) d1 = 0;
    if (d1 !== parseInt(cpf[9], 10)) return false;
    soma = 0;
    for (let i = 0; i < 10; i++) soma += parseInt(cpf[i], 10) * (11 - i);
    let d2 = (soma * 10) % 11;
    if (d2 === 10) d2 = 0;
    return d2 === parseInt(cpf[10], 10);
  }

  function cnpjValido(cnpj) {
    cnpj = digits(cnpj);
    if (cnpj.length !== 14) return false;
    if (/^(\d)\1{13}$/.test(cnpj)) return false;
    const digito = (base, pesos) => {
      let soma = 0;
      for (let i = 0; i < pesos.length; i++) soma += parseInt(base[i], 10) * pesos[i];
      const resto = soma % 11;
      return resto < 2 ? 0 : 11 - resto;
    };
    const p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const p2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    if (digito(cnpj, p1) !== parseInt(cnpj[12], 10)) return false;
    return digito(cnpj, p2) === parseInt(cnpj[13], 10);
  }

  function formatCpf(v) {
    const d = digits(v);
    if (d.length !== 11) return v || "";
    return d.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  }

  function formatCnpj(v) {
    const d = digits(v);
    if (d.length !== 14) return v || "";
    return d.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
  }

  App.validation = { digits, cpfValido, cnpjValido, formatCpf, formatCnpj };
})();
