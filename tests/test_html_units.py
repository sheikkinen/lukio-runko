"""Leaf block extraction from built pages, the page list and topic groups. Fast, no network."""

from __future__ import annotations

from lukio_runko.html_units import Block, page_blocks, site_pages, topic_group


def test_leaf_blocks_with_region_and_tag():
    html = (
        "<header><nav><ul><li><a href='#'>Etusivu</a></li></ul></nav></header>"
        "<main><h1>Otsikko</h1><p>Ensimmäinen <em>kappale</em><br>jatkuu.</p></main>"
        "<footer><p>Alatunniste</p></footer>"
    )
    assert page_blocks(html) == [
        Block("li", "nav", "Etusivu"),
        Block("h1", "main", "Otsikko"),
        Block("p", "main", "Ensimmäinen kappale jatkuu."),
        Block("p", "footer", "Alatunniste"),
    ]


def test_nested_blocks_own_their_text():
    html = "<main><ul><li>Kohta <p>sisempi kappale</p> loppu</li></ul><blockquote><p>Lainaus</p></blockquote></main>"
    assert page_blocks(html) == [Block("li", "main", "Kohta loppu"), Block("p", "main", "sisempi kappale"), Block("p", "main", "Lainaus")]


def test_scripts_are_skipped_and_text_outside_blocks_is_ignored():
    html = "<body><script>var a = '<p>ei</p>';</script><div>irrallinen</div><p>  väli   lyöntejä  </p></body>"
    assert page_blocks(html) == [Block("p", "body", "väli lyöntejä")]


def test_unclosed_block_still_counts():
    assert page_blocks("<main><p>Ei loppua") == [Block("p", "main", "Ei loppua")]


def test_site_pages_leave_out_print_pages(tmp_path):
    for name in ("index.html", "fi1/01-a/index.html", "fi1/01-a/tunti/index.html", "tulosta/fi1/index.html", "fi1/other.html"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("<p>x</p>", encoding="utf-8")
    assert site_pages(tmp_path) == ["fi1/01-a/index.html", "fi1/01-a/tunti/index.html", "index.html"]


def test_student_and_lesson_page_share_a_topic_group():
    assert topic_group("fi1/01-a/index.html") == "fi1/01-a/"
    assert topic_group("fi1/01-a/tunti/index.html") == "fi1/01-a/"
    assert topic_group("index.html") == "/"
    assert topic_group("polku/index.html") == "polku/"
