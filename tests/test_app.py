from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.model
APP = str(Path(__file__).resolve().parents[1] / "app.py")


def button(at, label):
    return next(b for b in at.button if b.label == label)


@pytest.fixture
def app():
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception
    return at


def summarize_example(at):
    button(at, "📄 Load example").click().run()
    button(at, "🚀 Summarize").click().run()
    assert not at.exception


def test_app_loads_the_model(app):
    assert any("Model ready" in s.value for s in app.success)
    assert "Summarize" in app.info[0].value


def test_summary_appears_with_download_and_copy(app):
    summarize_example(app)
    summary = app.session_state["result"]["summary"]
    assert any("summary-box" in m.value for m in app.markdown)
    assert app.code[0].value == summary  # the copyable plain-text version
    assert app.get("download_button")


def test_summary_survives_a_rerun(app):
    summarize_example(app)
    summary = app.session_state["result"]["summary"]
    app.checkbox[0].uncheck().run()  # any other interaction reruns the script
    assert app.session_state["result"]["summary"] == summary
    assert app.code[0].value == summary


def test_long_text_shows_its_parts(app):
    # The tiny model reads 100 tokens, so the example is split into parts.
    summarize_example(app)
    result = app.session_state["result"]
    assert result["chunks"] > 1 and result["parts"]
    assert any("parts" in e.label for e in app.expander)


def test_clear_empties_the_input_and_the_summary(app):
    summarize_example(app)
    button(app, "🔄 Clear").click().run()
    assert app.text_area(key="input_text").value == ""
    assert "result" not in app.session_state


def test_short_text_is_rejected(app):
    app.text_area(key="input_text").input("Too short.").run()
    button(app, "🚀 Summarize").click().run()
    assert any("at least 50 characters" in e.value for e in app.error)


def test_changed_input_marks_the_summary_as_stale(app):
    summarize_example(app)
    app.text_area(key="input_text").input("A different text that is long enough to summarize, surely.").run()
    assert any("changed since" in c.value for c in app.caption)
