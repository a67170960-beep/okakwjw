"""
Генератор ~400 000+ уникальных коротких юзернеймов для Telegram.
Telegram требует: 5–32 символа, только a-z, 0-9, _ (без двойных __).
"""

import itertools
import random
import string

# ─────────────────────────────────────────────
#  Словарные блоки
# ─────────────────────────────────────────────

PREFIXES = [
    "the", "mr", "ms", "dr", "pro", "max", "neo", "dev", "web", "top",
    "best", "hot", "cool", "super", "mega", "ultra", "hyper", "real",
    "true", "just", "pure", "only", "free", "fast", "dark", "light",
    "black", "white", "red", "blue", "gold", "star", "sky", "sun",
    "big", "epic", "king", "ace", "raw", "sharp", "smart", "bold",
    "deep", "wild", "rich", "zen", "vip", "one", "two", "x", "y", "z",
    "alpha", "beta", "gamma", "delta", "omega", "sigma", "crypto",
    "tech", "code", "hack", "byte", "bit", "net", "app", "ai", "bot",
    "auto", "cyber", "dig", "e", "i", "ix", "xo", "vx", "fx", "qx",
    "rx", "px", "ux", "ux", "lab", "hub", "io", "co", "go", "do",
]

NOUNS = [
    "wolf", "fox", "lion", "bear", "hawk", "eagle", "raven", "shark",
    "tiger", "panther", "cobra", "viper", "dragon", "phoenix", "ghost",
    "shadow", "storm", "blade", "arrow", "spark", "flame", "frost",
    "wave", "rock", "stone", "steel", "iron", "forge", "vault", "gate",
    "core", "edge", "peak", "rise", "flow", "rush", "pulse", "flux",
    "grid", "node", "link", "path", "road", "trail", "map", "mark",
    "view", "port", "base", "zone", "space", "void", "realm", "world",
    "force", "power", "mind", "soul", "hand", "eye", "arm", "fist",
    "hero", "ace", "boss", "lord", "king", "duke", "knight", "ranger",
    "scout", "pilot", "rider", "runner", "hunter", "seeker", "finder",
    "maker", "builder", "coder", "hacker", "trader", "player", "gamer",
    "racer", "drifter", "wanderer", "nomad", "rebel", "rogue", "sage",
    "wizard", "mage", "monk", "ninja", "samurai", "warrior", "sentinel",
    "guardian", "defender", "striker", "sniper", "raider", "brawler",
    "tank", "medic", "agent", "spy", "phantom", "cipher", "signal",
    "vector", "matrix", "nexus", "apex", "zenith", "nadir", "orbit",
    "comet", "meteor", "pulsar", "quasar", "nova", "stellar",
]

ADJECTIVES = [
    "fast", "swift", "quick", "slow", "bold", "brave", "calm", "cool",
    "dark", "deep", "elite", "epic", "evil", "fair", "fierce", "fine",
    "fire", "firm", "free", "fresh", "full", "good", "great", "grim",
    "hard", "harsh", "high", "holy", "huge", "keen", "last", "late",
    "lean", "live", "lone", "long", "loud", "mad", "main", "mega",
    "mild", "mint", "neon", "next", "nice", "night", "odd", "open",
    "pale", "peak", "prime", "pure", "rare", "raw", "rich", "real",
    "sharp", "sick", "slim", "small", "smart", "smooth", "solid",
    "stark", "still", "strong", "super", "tall", "true", "ultra",
    "vast", "void", "warm", "wide", "wild", "wise", "young", "zen",
]

SUFFIXES = [
    "pro", "max", "plus", "x", "xx", "hd", "v2", "v3", "go", "io",
    "tv", "gg", "ok", "hub", "lab", "ai", "bot", "dev", "net", "app",
    "one", "two", "007", "101", "404", "777", "99", "88", "00", "01",
    "rx", "px", "fx", "vx", "ix", "0x", "xo", "ox",
]

NUMBERS = [str(n) for n in range(10)] + \
          [str(n) for n in range(100)] + \
          ["007", "404", "777", "999", "123", "321", "666", "888", "000",
           "1337", "2024", "2025", "69", "42", "911", "911"]


# ─────────────────────────────────────────────
#  Генераторы комбинаций
# ─────────────────────────────────────────────

def _valid(name: str) -> bool:
    """Проверяет базовые требования Telegram."""
    if len(name) < 5 or len(name) > 32:
        return False
    if "__" in name:
        return False
    if name.startswith("_") or name.endswith("_"):
        return False
    allowed = set(string.ascii_lowercase + string.digits + "_")
    return all(c in allowed for c in name)


def _gen_all() -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    def add(name: str):
        name = name.lower()
        if name not in seen and _valid(name):
            seen.add(name)
            result.append(name)

    # 1. adj + noun  (~3 500)
    for a, n in itertools.product(ADJECTIVES, NOUNS):
        add(f"{a}{n}")
        add(f"{a}_{n}")

    # 2. prefix + noun  (~3 700)
    for p, n in itertools.product(PREFIXES, NOUNS):
        add(f"{p}{n}")
        add(f"{p}_{n}")

    # 3. noun + suffix  (~4 200)
    for n, s in itertools.product(NOUNS, SUFFIXES):
        add(f"{n}{s}")
        add(f"{n}_{s}")

    # 4. prefix + noun + suffix  (~40 000)
    for p, n, s in itertools.product(PREFIXES[:25], NOUNS[:80], SUFFIXES[:20]):
        add(f"{p}{n}{s}")
        add(f"{p}_{n}_{s}")

    # 5. adj + noun + number  (~80 000)
    nums_short = [str(n) for n in range(100)] + ["007", "777", "999", "404", "123"]
    for a, n, num in itertools.product(ADJECTIVES[:50], NOUNS[:80], nums_short[:40]):
        add(f"{a}{n}{num}")

    # 6. noun + number  (~15 000)
    for n, num in itertools.product(NOUNS, nums_short):
        add(f"{n}{num}")
        add(f"{n}_{num}")

    # 7. prefix + adj + noun  (~50 000)
    for p, a, n in itertools.product(PREFIXES[:30], ADJECTIVES[:40], NOUNS[:50]):
        add(f"{p}{a}{n}")

    # 8. 3-letter combos + nouns  (~50 000)
    chars = string.ascii_lowercase
    for c1, c2, n in itertools.product(chars[:10], chars[:10], NOUNS[:50]):
        add(f"{c1}{c2}{n}")
        add(f"{n}{c1}{c2}")

    # 9. noun + _ + noun  (~10 000)
    for n1, n2 in itertools.product(NOUNS[:50], NOUNS[:50]):
        if n1 != n2:
            add(f"{n1}_{n2}")

    # 10. adj + _ + adj + noun  (~20 000)
    for a1, a2, n in itertools.product(ADJECTIVES[:20], ADJECTIVES[:20], NOUNS[:50]):
        if a1 != a2:
            add(f"{a1}_{a2}{n}")

    # 11. Шаблоны с числами в середине  (~30 000)
    for n, num, s in itertools.product(NOUNS[:60], nums_short[:30], SUFFIXES[:17]):
        add(f"{n}{num}{s}")

    # 12. Тематические crypto/tech  (~20 000)
    crypto = ["btc", "eth", "ton", "sol", "xrp", "bnb", "ada", "dot",
              "link", "uni", "avax", "matic", "ltc", "doge", "shib",
              "near", "algo", "atom", "apt", "arb", "op", "base"]
    tech = ["dev", "code", "hack", "byte", "bit", "api", "sdk", "git",
            "cli", "ssh", "vpn", "cdn", "dns", "lan", "wan", "ram",
            "cpu", "gpu", "ssd", "usb", "html", "css", "js", "ts",
            "py", "go", "rs", "c", "cpp", "sql", "gql", "rpc"]
    for t, n in itertools.product(tech, NOUNS[:60]):
        add(f"{t}{n}")
        add(f"{t}_{n}")
    for c, n in itertools.product(crypto, NOUNS[:40]):
        add(f"{c}{n}")
        add(f"{c}_{n}")
    for t, num in itertools.product(tech, nums_short[:50]):
        add(f"{t}{num}")

    # Перемешиваем для разнообразия
    random.shuffle(result)
    return result


# ─────────────────────────────────────────────
#  Публичный API
# ─────────────────────────────────────────────

_CACHE: list[str] | None = None


def get_all_usernames() -> list[str]:
    global _CACHE
    if _CACHE is None:
        _CACHE = _gen_all()
    return _CACHE


def get_total_count() -> int:
    return len(get_all_usernames())


def get_page(page: int, per_page: int = 50) -> tuple[list[str], int]:
    """Возвращает (список юзернеймов, всего страниц)."""
    all_u = get_all_usernames()
    total_pages = (len(all_u) + per_page - 1) // per_page
    start = page * per_page
    end = start + per_page
    return all_u[start:end], total_pages


def search_usernames(query: str, page: int = 0, per_page: int = 50) -> tuple[list[str], int]:
    """Поиск по подстроке."""
    q = query.lower().strip()
    filtered = [u for u in get_all_usernames() if q in u]
    total_pages = max(1, (len(filtered) + per_page - 1) // per_page)
    start = page * per_page
    return filtered[start:start + per_page], total_pages


def get_random_usernames(count: int = 50) -> list[str]:
    """Случайная выборка."""
    all_u = get_all_usernames()
    return random.sample(all_u, min(count, len(all_u)))


def get_stats() -> dict:
    all_u = get_all_usernames()
    lengths = [len(u) for u in all_u]
    return {
        "total": len(all_u),
        "avg_len": round(sum(lengths) / len(lengths), 1),
        "min_len": min(lengths),
        "max_len": max(lengths),
        "with_underscore": sum(1 for u in all_u if "_" in u),
        "with_numbers": sum(1 for u in all_u if any(c.isdigit() for c in u)),
    }
