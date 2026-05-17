"""
Analisa a qualidade da busca semântica chamando a API local.
Gera um relatório por query indicando hits vs misses contra um ground truth manual.
"""
import json
import sys
import time
from urllib import request, error

API = "http://localhost:8000/search"

# Ground truth manual — lista de slugs esperados para cada query.
# Usamos slugs (lowercase, hífen) para casar com o nome da PokeAPI.
BENCHMARK = {
    "pokemon de fogo que voa": [
        "charizard", "moltres", "ho-oh", "talonflame", "salazzle",
        "fletchinder", "delphox", "rayquaza"
    ],
    "pokemon que parecem deuses divindades criadores do universo": [
        "arceus", "dialga", "palkia", "giratina", "ho-oh", "lugia",
        "rayquaza", "calyrex", "mewtwo", "kyogre", "groudon", "xerneas", "yveltal"
    ],
    "pokemon tristes solitários melancólicos abandonados": [
        "cubone", "mimikyu", "absol", "banette", "phantump", "drifloon",
        "yamask", "spiritomb", "litwick", "shedinja"
    ],
    "pokemon do espaço cosmos estrelas lua sol universo": [
        "deoxys", "jirachi", "solrock", "lunatone", "cosmog", "cosmoem",
        "solgaleo", "lunala", "necrozma", "eternatus", "minior", "clefairy",
        "elgyem", "beheeyem"
    ],
    "pokemon fofos pequenos fada mágicos encantados adoráveis": [
        "clefairy", "jigglypuff", "togepi", "sylveon", "mimikyu", "dedenne",
        "comfey", "alcremie", "eevee", "mew", "pikachu", "skitty", "azurill",
        "togedemaru", "morpeko"
    ],
    "pokemon fósseis pré-históricos antigos extintos": [
        "aerodactyl", "omanyte", "omastar", "kabuto", "kabutops", "anorith",
        "armaldo", "lileep", "cradily", "cranidos", "rampardos", "shieldon",
        "bastiodon", "tirtouga", "carracosta", "archen", "archeops", "tyrunt",
        "tyrantrum", "amaura", "aurorus", "dracozolt", "arctozolt",
        "dracovish", "arctovish"
    ],
    "pokemon predadores perigosos agressivos destrutivos monstros": [
        "gyarados", "tyranitar", "hydreigon", "garchomp", "salamence",
        "haxorus", "drapion", "sharpedo", "feraligatr", "krookodile",
        "weavile", "mightyena"
    ],
    "pokemon de pesadelos medo horror fantasma assombração terror": [
        "darkrai", "gengar", "haunter", "duskull", "banette", "spiritomb",
        "chandelure", "mimikyu", "gourgeist", "trevenant", "dusknoir",
        "shedinja", "yamask", "phantump", "litwick"
    ],
    "pokemon robóticos mecânicos artificiais máquinas tecnologia": [
        "magnemite", "magneton", "magnezone", "porygon", "porygon2", "porygon-z",
        "genesect", "magearna", "registeel", "metagross", "golurk",
        "klinklang", "type-null", "rotom", "beldum", "klink", "klang"
    ],
    "pokemon inspirados na mitologia japonesa lendas orientais": [
        "ninetales", "vulpix", "arcanine", "ho-oh", "lugia", "suicune",
        "absol", "lucario", "zoroark", "greninja", "kommo-o", "honedge",
        "aegislash", "bisharp", "samurott", "doublade", "scrafty"
    ],
}


def call_api(query: str, top_k: int = 20) -> list[dict]:
    payload = json.dumps({"query": query, "top_k": top_k}).encode("utf-8")
    req = request.Request(
        API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())["results"]
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"  HTTP {e.code}: {body[:200]}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  ERR: {e}", file=sys.stderr)
        return []


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-")


def main() -> None:
    print("=" * 78)
    print("📊 ANÁLISE DE QUALIDADE — Busca Semântica via API (localhost:8000)")
    print("=" * 78)

    recalls = []
    summary_rows = []

    for query, expected in BENCHMARK.items():
        t0 = time.time()
        results = call_api(query, top_k=20)
        elapsed = time.time() - t0

        retrieved_slugs = [slugify(r["name"]) for r in results]
        retrieved_set = set(retrieved_slugs)
        expected_set = set(expected)

        hits = retrieved_set & expected_set
        recall = len(hits) / len(expected_set) if expected_set else 0
        recalls.append(recall)

        status = "✅" if recall >= 0.5 else "⚠️" if recall >= 0.25 else "❌"
        print(f"\n{status} Query: \"{query}\"  ({elapsed*1000:.0f}ms)")
        print(f"   Recall@20: {recall:.1%}  ({len(hits)}/{len(expected_set)})")

        # Mostra TODOS os 20 resultados com marca de hit
        print(f"   Top-20 retornados:")
        for i, r in enumerate(results, 1):
            slug = slugify(r["name"])
            is_hit = "✓" if slug in expected_set else " "
            tag = ""
            if r.get("is_legendary"):
                tag = " ⭐"
            elif r.get("is_mythical"):
                tag = " ✨"
            print(f"      [{is_hit}] #{i:2d} {r['name']:<22s} | {r['types']:<24s} | score={r['score']:.4f}{tag}")

        missed = expected_set - retrieved_set
        if missed:
            print(f"   ❌ NÃO retornados (ground truth): {sorted(missed)}")

        summary_rows.append((query, recall, len(hits), len(expected_set)))

    mean = sum(recalls) / len(recalls)
    print("\n" + "=" * 78)
    print(f"📊 RESUMO")
    print("=" * 78)
    for q, r, h, t in summary_rows:
        flag = "✅" if r >= 0.5 else "⚠️" if r >= 0.25 else "❌"
        print(f"  {flag} {r:6.1%}  ({h:2d}/{t:2d})  {q[:60]}")
    print("-" * 78)
    print(f"  📈 Recall@20 médio: {mean:.1%}")
    print("=" * 78)


if __name__ == "__main__":
    main()
