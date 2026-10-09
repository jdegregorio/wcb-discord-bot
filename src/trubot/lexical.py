"""Conservative grammatical equivalence for retrieval, never source quotation."""

import re

# Explicit domain nouns avoid stemming names or merging arbitrary words. This is
# a retrieval vocabulary, not a list of persona interests or semantic synonyms.
_PLURALS = {
    plural: singular
    for singular, plural in (
        ("champion", "champions"),
        ("draft", "drafts"),
        ("kicker", "kickers"),
        ("league", "leagues"),
        ("matchup", "matchups"),
        ("opponent", "opponents"),
        ("pick", "picks"),
        ("player", "players"),
        ("playoff", "playoffs"),
        ("quarterback", "quarterbacks"),
        ("roster", "rosters"),
        ("rule", "rules"),
        ("seed", "seeds"),
        ("team", "teams"),
        ("trade", "trades"),
        ("waiver", "waivers"),
        ("winner", "winners"),
    )
}


def words(text: str) -> tuple[str, ...]:
    """Keep token boundaries, numbers and order; normalize only known noun plurals."""
    return tuple(_PLURALS.get(word, word) for word in re.findall(r"[a-z0-9]+", text.casefold()))


def phrase(text: str) -> str:
    """A padded phrase for whole-word, contiguous reviewed-alias matching."""
    return " " + " ".join(words(text)) + " "
