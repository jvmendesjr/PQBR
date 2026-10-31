from pqbr.workflows.auditor_gemini import grupos


def test_grupos_cobrem_tudo():
    for n in range(1, 15):
        for k in (1, 2, 3, 4, 20):
            g = grupos(list(range(n)), k)
            assert sum(g, []) == list(range(n)) and len(g) == min(k, n) and all(g)
            assert max(map(len, g)) - min(map(len, g)) <= 1
