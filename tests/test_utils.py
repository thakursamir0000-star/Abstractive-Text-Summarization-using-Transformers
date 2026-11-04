from src.utils import format_duration, html_text, reading_seconds, word_count


def test_html_text_escapes_markup_and_dollar_signs():
    out = html_text('<script>alert("x")</script> costs $5 and $6\nnext')
    assert "<script>" not in out and "&lt;script&gt;" in out
    assert "$" not in out and out.count("&#36;") == 2
    assert out.endswith("<br>next")


def test_reading_time():
    assert word_count("one two  three\nfour") == 4
    assert reading_seconds("word " * 230) == 60
    assert format_duration(0.2) == "1 s"
    assert format_duration(45) == "45 s"
    assert format_duration(210) == "3.5 min"
