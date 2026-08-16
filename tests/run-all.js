// Roda a suíte inteira em sequência e resume o resultado.
const { spawnSync } = require("child_process");
const path = require("path");

const SUITE = [
  ["Sintaxe e referencias", "syntax-check.js"],
  ["Smoke de dados e auth", "core-smoke.js"],
  ["Hardening", "hardening.js"],
  ["Fluxo no DOM", "dom-flow.js"],
];

let falhas = 0;
for (const [nome, arquivo] of SUITE) {
  console.log(`\n─── ${nome} ${"─".repeat(Math.max(0, 46 - nome.length))}`);
  const r = spawnSync(process.execPath, [path.join(__dirname, arquivo)], { stdio: "inherit" });
  if (r.status !== 0) falhas++;
}

console.log("\n" + "═".repeat(52));
if (falhas) { console.log(`${falhas} de ${SUITE.length} suites falharam.`); process.exit(1); }
console.log(`Todas as ${SUITE.length} suites passaram.`);
