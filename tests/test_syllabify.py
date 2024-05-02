import pytest
from aligned_textgrid import AlignedTextGrid, custom_classes, Word, Phone
from fave_syllabify import syllabify_tg
from pathlib import Path

def test_syllabify():
    tg_path = Path("tests", "data", "aligned", "words.TextGrid")

    tg = AlignedTextGrid(
        textgrid_path=tg_path,
        entry_classes=custom_classes(["Word", "Phone"])
    )

    assert len(tg[0]) == 2

    syllabify_tg(tg)

    syllables = tg[0].Syllable
    sylparts = tg[0].SylPart
    phones = tg[0].Phone

    for syl in syllables:
        if len(syl.label) > 0:
            assert "syl" in syl.label
    
    for sylp in sylparts:
        if len(syl.label) > 0:
            assert sylp.label in ["onset", "nucleus", "coda"]


    for p in phones:
        if len(syl.label)>0:
            assert p.within.label in ["onset", "nucleus", "coda"]


def test_syllabify_iter():

    tg_path = Path("tests", "data", "aligned", "words.TextGrid")

    entry_classes = classes = custom_classes(["Word", "Phone"])

    tg1 = AlignedTextGrid(
        textgrid_path=tg_path,
        entry_classes= entry_classes
    )

    tg2 = AlignedTextGrid(
        textgrid_path=tg_path,
        entry_classes= entry_classes
    )

    syllabify_tg(tg1)

    assert entry_classes[0].subset_class is entry_classes[1]
    assert not tg1[0].Word.subset_class is entry_classes[1]

    syllabify_tg(tg2)

