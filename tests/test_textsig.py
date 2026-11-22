"""Text signatures: normalising, sentence splitting, unit ids, MinHash, LSH and union-find. Fast, no network."""

from __future__ import annotations

import hashlib

from lukio_runko import textsig
from lukio_runko.textsig import UnionFind, jaccard, minhash, normalise, shingles, split_sentences, unit_id, word_count


def test_normalise_ignores_case_punctuation_and_markup_spacing():
    assert normalise("Hei,  maailma!") == "hei maailma"
    assert normalise("HEI — maailma.") == normalise("hei maailma")
    assert normalise("  rivi\nja\ttoinen  ") == "rivi ja toinen"


def test_normalise_keeps_finnish_letters_and_composes_them():
    assert normalise("ÄÖÅ äöå") == "äöå äöå"
    decomposed = "Päivä"  # a + combining diaeresis
    assert normalise(decomposed) == normalise("Päivä") == "päivä"
    assert normalise("opis­kelija") == "opiskelija"  # a soft hyphen splits no word


def test_normalise_replaces_dates_and_numbers():
    assert normalise("Tarkistettu 22.11.2026.") == "tarkistettu <pvm>"
    assert normalise("Tarkistettu 2026-11-22") == "tarkistettu <pvm>"
    assert normalise("Aika: 15 min, osa 2") == "aika <n> min osa <n>"
    assert normalise("Moduuli FI1.s1") == "moduuli fi<n> s<n>"  # a code stays two words, not four
    assert normalise("Tarkistettu 1.8.2025") == normalise("Tarkistettu 31.12.2030")


def test_normalise_removes_urls():
    assert normalise("Katso https://example.org/a?b=1 ja www.oph.fi/x tästä.") == "katso ja tästä"


def test_word_count_and_unit_id():
    assert word_count(normalise("Yksi kaksi, kolme.")) == 3
    expected = hashlib.sha256(b"hei maailma").hexdigest()[:16]
    assert unit_id("hei maailma") == expected
    assert len(expected) == 16


def test_split_at_sentence_ends():
    text = "Ensimmäinen lause. Toinen lause! Kolmas lause? Neljäs lause… Viides."
    assert split_sentences(text) == ["Ensimmäinen lause.", "Toinen lause!", "Kolmas lause?", "Neljäs lause…", "Viides."]


def test_split_needs_an_uppercase_letter_digit_quote_or_bracket_next():
    assert split_sentences("Loppu. 2 tehtävää jää.") == ["Loppu.", "2 tehtävää jää."]
    assert split_sentences('Hän sanoi. "Tule tänne."') == ["Hän sanoi.", '"Tule tänne."']
    assert split_sentences("Lue tämä. (Vapaaehtoinen.)") == ["Lue tämä.", "(Vapaaehtoinen.)"]
    assert split_sentences("Pieni alku. pieni jatko.") == ["Pieni alku. pieni jatko."]


def test_split_skips_abbreviations_initials_and_ordinals():
    assert split_sentences("Esim. Helsinki on kaupunki. Ks. Liite 2.") == ["Esim. Helsinki on kaupunki.", "Ks. Liite 2."]
    # an abbreviation at a real sentence end keeps the two sentences together: a missed split, never a wrong one
    assert split_sentences("Lue kirjat, lehdet jne. Kirjoita sitten.") == ["Lue kirjat, lehdet jne. Kirjoita sitten."]
    assert split_sentences("J. V. Snellman kirjoitti. Hän oli filosofi.") == ["J. V. Snellman kirjoitti.", "Hän oli filosofi."]
    assert split_sentences("Opiskelija on 1. vuoden opiskelija.") == ["Opiskelija on 1. vuoden opiskelija."]
    assert split_sentences("Valitse 1. 2. tai 3. vaihtoehto.") == ["Valitse 1. 2. tai 3. vaihtoehto."]
    assert split_sentences("Vuonna 2024. Seuraava vuosi.") == ["Vuonna 2024.", "Seuraava vuosi."]


def test_shingles_and_jaccard():
    first = shingles(normalise("Arvioi jokainen kohta asteikolla yhdestä neljään."))
    assert jaccard(first, first) == 1.0
    second = shingles(normalise("Arvioi jokainen kohta asteikolla yhdestä viiteen."))
    assert 0.7 < jaccard(first, second) < 1.0
    unrelated = shingles(normalise("Tänään sataa lunta koko päivän."))
    assert jaccard(first, unrelated) < 0.1
    assert len(shingles("abc")) == 1  # shorter than one shingle


def test_minhash_is_fixed_and_order_free():
    values = shingles(normalise("Kirjoita vastaukset omaan muistioosi ja palaa niihin myöhemmin."))
    signature = minhash(values)
    assert len(signature) == textsig.BINS
    assert minhash(sorted(values, reverse=True)) == signature
    assert minhash(set(values)) == signature


def test_candidate_pairs_find_near_texts_only():
    texts = {
        "a": "Helpompi polku: lue ensin tiivistelmä ja tee sitten tehtävä yksi rauhassa.",
        "b": "Helpompi polku: lue ensin tiivistelmä ja tee sitten tehtävä kaksi rauhassa.",
        "c": "Syvempi polku vertaa kahta filosofia ja kirjoittaa niistä lyhyen esseen.",
    }
    signatures = {key: minhash(shingles(normalise(text))) for key, text in texts.items()}
    pairs = textsig.candidate_pairs(signatures)
    assert ("a", "b") in pairs
    assert all("c" not in pair for pair in pairs)


def test_union_find_joins_and_keeps_the_smallest_root():
    joined = UnionFind()
    joined.union("d", "b")
    joined.union("c", "d")
    joined.union("x", "y")
    joined.find("lonely")
    assert joined.find("d") == "b"
    assert joined.clusters() == [["b", "c", "d"], ["x", "y"]]
