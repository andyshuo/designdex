"""Tests for the BM25 ranking core."""

from uiux_pro_max.core import BM25


def test_tokenize_lowercases_and_splits_on_punctuation():
    assert BM25().tokenize("Dark-Mode, Glassmorphism!") == [
        "dark",
        "mode",
        "glassmorphism",
    ]


def test_tokenize_drops_tokens_of_two_characters_or_fewer():
    """Short tokens carry no signal and would match almost every row."""
    assert BM25().tokenize("ui ux css grid") == ["css", "grid"]


def test_score_puts_the_matching_document_first():
    bm25 = BM25()
    bm25.fit(["alpha beta gamma", "alpha beta", "delta epsilon zeta"])

    ranked = bm25.score("gamma")

    assert ranked[0][0] == 0
    assert ranked[0][1] > 0
    assert all(score == 0 for _, score in ranked[1:])


def test_score_returns_every_document_even_when_nothing_matches():
    bm25 = BM25()
    bm25.fit(["alpha beta", "gamma delta"])

    assert len(bm25.score("nothingrelevant")) == 2


def test_fit_twice_gives_the_same_scores_as_fit_once():
    """A second fit() must not accumulate document frequencies.

    ``fit`` counted into the same ``doc_freqs`` dict, so refitting the same
    corpus doubled every count. Terms that appear in most documents then got a
    negative IDF and the ranking quietly inverted.
    """
    documents = ["alpha beta gamma", "alpha beta", "alpha"]

    once = BM25()
    once.fit(documents)

    twice = BM25()
    twice.fit(documents)
    twice.fit(documents)

    assert dict(twice.idf) == dict(once.idf)
    assert all(value > 0 for value in twice.idf.values())


def test_empty_corpus_scores_nothing():
    bm25 = BM25()
    bm25.fit([])

    assert bm25.score("anything") == []


def test_documents_that_tokenize_to_nothing_do_not_divide_by_zero():
    bm25 = BM25()
    bm25.fit(["a b", "c"])

    assert bm25.avgdl == 0
    assert bm25.score("a b c") == [(0, 0), (1, 0)]


def test_rarer_terms_outrank_common_ones():
    """IDF should make the unusual word the deciding signal."""
    bm25 = BM25()
    bm25.fit(
        [
            "button button button spinner",
            "button input",
            "button select",
        ]
    )

    ranked = bm25.score("spinner button")

    assert ranked[0][0] == 0
