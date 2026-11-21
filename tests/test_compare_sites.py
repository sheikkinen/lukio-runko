from lukio_runko.compare_sites import compare, main


def test_compare_lists_every_difference(tmp_path, capsys):
    golden, built = tmp_path / "golden", tmp_path / "built"
    for root in (golden, built):
        (root / "a").mkdir(parents=True)
        (root / "a" / "same.html").write_bytes(b"x\r\n")
    (golden / "a" / "eol.html").write_bytes(b"x\r\n")
    (built / "a" / "eol.html").write_bytes(b"x\n")
    (golden / "gone.html").write_text("g")
    (built / "new.html").write_text("n")
    assert compare(golden, built) == ["only in golden: gone.html", "only in built: new.html", "differs: a/eol.html"]
    assert main([str(golden), str(golden)]) == 0
    assert main([str(golden), str(built)]) == 1
    assert "3 differences" in capsys.readouterr().out
