-- ERR-MON-02 (lote-2510, agente externo PQBR, 25/10/2026, OK do José t34u). Idempotente por código.
insert into pqbr.catalogo_erros (codigo, categoria, descricao, exemplo, prevencao, severidade, papeis_interessados) values
('ERR-MON-02','montagem','CTA personalizado substituído por genérico: na remontagem com voz dinâmica, o fechamento contextual do roteiro (ex.: "Tranca essa ansiedade na chave e segue o Porquê BR!") foi trocado pelo take padrão "Segue o Porquê BR!" (cta-padrao-B.mp3).',
 '{"tema":"lote-2510: fechadura, formiga, crostinha, brigadeiro, nao-e-bem-assim, olhos-da-cara","caminho":"scripts/montar_voz_dinamica.py (commit 3484342); corrigido em runtime/lote-saldo/<tema>/<tema>-pronto-v2.mp4"}',
 'Na voz/montagem, a fala final é SEMPRE a última frase original de narracao.txt do roteiro (CTA contextual, REGRAS §5/t467); um take padrão serve só como referência de entonação. montar_voz_dinamica.py recusa cta-padrao* sem --permitir-cta-generico (só quando o CTA original já é "Segue o Porquê BR"); o Auditor compara a última linha da legenda com a última linha do roteiro.','alta','{lider-editorial,auditor,dev}')
on conflict (codigo) do nothing;
