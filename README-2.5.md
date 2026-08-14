# AutoControl 2.5 — Blue Operations

Atualização sobre a base AutoControl 2.4, mantendo o `legacy-desktop` intacto.

## Novidades
- Central de Operações para manutenção e diagnóstico.
- Backup completo em JSON e restauração com validação de estrutura.
- Indicador online/offline e suporte PWA.
- Central de notificações para estoque crítico, OS com baixa progressão e agenda atrasada.
- Atalho de instalação do PWA quando o navegador oferecer suporte.
- Diagnóstico rápido das coleções locais, sessão e service worker.
- Ferramentas de manutenção e boas práticas dentro do app.
- Service Worker atualizado para incluir a nova tela.
- Cache invalidável após restauração de backup.

## Testes executados
```text
PASS: seed/auth/db/validation smoke + corruption + quota
PASS: hardening, corruption, quota rollback, auth, validation
PASS: JavaScript syntax for all JS files
PASS: index/service-worker references
PASS: central route, backup/restore, notifications, PWA and offline hooks
```

## Observação
A aplicação continua sendo uma PWA local com `localStorage`. Para uso em equipe com vários dispositivos, o próximo salto técnico é uma API + banco remoto + autenticação real + sincronização.
