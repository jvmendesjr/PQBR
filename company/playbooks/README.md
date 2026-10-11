# Playbooks de correção da PQBR (REGRAS §0 item 8, §3.1)
Cada falha conhecida tem passos ordenados. O agente escolhe entre eles, faz no máx. 3 tentativas (Camofox: 5–15 min sorteados entre elas) e grava o resultado de cada uma na issue. Esgotou: Diretor → Telegram → José. Nunca: excluir, segredos, regra canônica.

| Playbook | Dono | Gatilho |
|---|---|---|
| `tarefa-bloqueada.md` | Observador (detecta) / Diretor (reatribui) | issue `blocked` após falha de run |
| `camofox-sessao.md` | Observador + código (watchdog) | sessão do Studio caiu |
| `camofox-watchdog.md` | código (systemd) / Observador | serviço `pqbr-camofox` caiu |
| `saida-invalida.md` | dono da tarefa | saída fora do contrato Pydantic |
| `lock-preso.md` | Diretor | 409 persistente no checkout |
