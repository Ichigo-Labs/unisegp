from uniseg.breaking import Breakables
from uniseg.linebreak import LB, line_break
from uniseg.wrap import tt_wrap


def test_tt_wrap_001() -> None:
    actual = list(
        tt_wrap('A quick brown fox jumped over the lazy dog.', 24)
    )
    expect = [
        # ---------+---------+----
        'A quick brown fox ',
        'jumped over the lazy ',
        'dog.',
    ]
    assert expect == actual


def test_tt_wrap_002() -> None:
    actual = list(
        tt_wrap('A quick brown fox jumped over the lazy dog.', 36)
    )
    expect = [
        # ---------+---------+---------+------
        'A quick brown fox jumped over the ',
        'lazy dog.',
    ]
    assert expect == actual


def test_tt_wrap_003() -> None:
    actual = list(
        tt_wrap('和歌は、人の心を種として、万の言の葉とぞなれりける。', 24)
    )
    expect = [
        # ---------+---------+----
        '和歌は、人の心を種とし',
        'て、万の言の葉とぞなれり',
        'ける。'
    ]
    assert expect == actual


def test_tt_wrap_004() -> None:
    actual = list(
        tt_wrap('supercalifragilisticexpialidocious', 24)
    )
    expect = [
        # ---------+---------+----
        'supercalifragilisticexpialidocious',
    ]
    assert expect == actual


def test_tt_wrap_005() -> None:
    actual = list(
        tt_wrap('A\tquick\tbrown fox jumped\tover\tthe lazy dog.', 32)
    )
    expect = [
        # ---------+---------+---------+--
        'A       quick   brown fox ',
        'jumped  over    the lazy dog.',
    ]
    assert expect == actual


def test_tt_wrap_006() -> None:
    actual = list(
        tt_wrap('A\tquick\tbrown fox jumped\tover\tthe lazy dog.', 32, tab_width=10)
    )
    expect = [
        # ---------+---------+---------+--
        'A         quick     brown fox ',
        'jumped    over      the lazy ',
        'dog.',
    ]
    assert expect == actual


def test_tt_wrap_007() -> None:
    actual = list(
        tt_wrap('αβγδ εζηθι κλμνξο πρστυφχψω', 24)
    )
    expect = [
        # ---------+---------+----
        'αβγδ εζηθι κλμνξο ',
        'πρστυφχψω',
    ]
    assert expect == actual


def test_tt_wrap_008() -> None:
    actual = list(
        tt_wrap('αβγδ εζηθι κλμνξο πρστυφχψω', 24, ambiguous_as_wide=True)
    )
    expect = [
        # ---------+--
        'αβγδ εζηθι ',
        'κλμνξο ',
        'πρστυφχψω',
    ]
    assert expect == actual


def test_tt_wrap_009() -> None:
    actual = list(
        tt_wrap('A\tquick\tbrown fox jumped\tover\tthe lazy dog.', 30, cur=4)
    )
    expect = [
        # ---------+---------+---------+
        'A   quick   brown fox ',
        'jumped  over    the lazy dog.',
    ]
    #   ||||A   quick   brown fox
    #   jumped  over    the lazy dog.
    assert expect == actual


def test_tt_wrap_010() -> None:
    actual = list(
        tt_wrap('A\tquick\tbrown fox jumped\tover\tthe lazy dog.', 30, offset=2)
    )
    expect = [
        # ---------+---------+---------+
        'A     quick   brown fox ',
        'jumped        over    the ',
        'lazy dog.',
    ]
    #   ||A     quick   brown fox
    #   ||jumped        over    the
    #   ||lazy dog.
    assert expect == actual


def test_tt_wrap_011() -> None:
    actual = list(
        tt_wrap('なんかシュッ、としたやつ', 12)
    )
    expect = [
        'なんか',
        'シュッ、とし',
        'たやつ'
    ]
    assert expect == actual

    def tailor(s: str, breakables: Breakables) -> Breakables:
        return [
            1 if line_break(c) == LB.CJ else b for c, b in zip(s, breakables)
        ]

    actual = list(
        tt_wrap('なんかシュッ、としたやつ', 12, tailor=tailor)
    )
    expect = [
        # ---------+--
        'なんかシュ',
        'ッ、としたや',
        'つ'
    ]
    assert expect == actual


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
