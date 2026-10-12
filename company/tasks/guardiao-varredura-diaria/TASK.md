---
name: "Guardião: varredura diária de segurança"
assignee: guardiao-seguranca
project: seguranca
recurring: true
---

Segredos, permissões por agente, idade das chaves, uso anômalo e auditoria das ações das últimas 24 h.

Inclui os **run-logs** do Paperclip (t415): rode `seguranca_varrer_logs` (24 h) e, se houver chave/JWT, abra ticket e peça rotação; IP/e-mail = PII, registre e siga a barreira.
