from aligned_textgrid import AlignedTextGrid, \
    custom_classes,\
    SequenceInterval
from syllabify import SLAX, VOWELS, O2, O3
import re
from icecream import ic

O2.add(("HH", "W"))

def make_syllable_constituents(word: SequenceInterval):
    parts = [p for p in word.contains]
    nuclei = [x for x in parts if re.match(r"[AEIOU]", x.label)]

    if len(nuclei) == 0:
        return
    
    for n in nuclei:
        stress = re.findall(r"\d", n.contains[0].label)[0]
        n.set_feature("stress", stress)
        n.label = "nucleus"

        if n.prev.label == "Y" and \
           "UW" in n.last.label:
            if (n.prev.prev.label != "#") and \
               n.prev.prev not in nuclei:
                n.fuse_leftwards(label_fun = lambda x,y: y)

        if n.prev.label != "#" and \
           n.prev.label != "NG" and\
           n.prev not in nuclei:
            n.prev.label = "onset"

        if n.prev.label == "onset":
            maximized = False
            while not maximized:
                current_onsets = n.prev.sub_labels
                candidate_segment = n.prev.prev
                candidate_label = candidate_segment.label
                if candidate_label == "#":
                    maximized = True
                    break

                if (candidate_label, current_onsets[0]) in O2:
                    n.prev.fuse_leftwards(label_fun=lambda x, y: y)
                else:
                    maximized = True

    for n in nuclei:
        cleanedup = False
        while not cleanedup:
            if n.fol.label == "#":
                cleanedup = True
                break
            if n.fol.label in ["onset", "nucleus"]:
                cleanedup = True
                break
            
            if n.fol.label != "coda":
                n.fol.label = "coda"

            if n.fol.fol.label == "#":
                cleanedup = True
                break
            if n.fol.fol.label in ["onset", "nucleus"]:
                cleanedup = True
                break

            n.fol.fuse_rightwards(label_fun = lambda x, y: x)


def syllabify_word(word: SequenceInterval):
    """Syllabify a single word

    Args:
        word (SequenceInterval): The word Sequence Interval to syllabify
    """

    tg_entry_classes = {c.__name__ for gr in word.intier.within.within.entry_classes for c in gr}
    if "SylPart" not in tg_entry_classes:
        word.intier.within.within.interleave_class(
            "SylPart",
            above = "Phone",
            timing_from = "below"
        )

    make_syllable_constituents(word)

    tg_entry_classes = {c.__name__ for gr in word.intier.within.within.entry_classes for c in gr}
    if "Syllable" not in tg_entry_classes:
        word.intier.within.within.interleave_class(
            "Syllable",
            below = "Word",
            timing_from = "below"
        )

    constituents = [c for c in word]
    nuclei = [c for c in constituents if c.label == "nucleus"]
    
    if len(nuclei) == 0:
        return
    
    for n in nuclei:
        stress = n.last.stress
        n.label = f"syl-{stress}"

        if n.prev.label == "onset":
            n.fuse_leftwards(lambda x, y: y)
        
        if n.fol.label == "coda":
            n.fuse_rightwards(lambda x,y: x)


def syllabify_tg(tg: AlignedTextGrid):
    """Syllabify an entire AlignedTextGrid
    Args:
        tg (AlignedTextGrid): The textgrid to syllabify
    """

    tg.interleave_class(
        "SylPart",
        above = "Phone",
        timing_from = "below"
    )

    word_tiers = [tgr.Word for tgr in tg]
    words = [seq for tier in word_tiers for seq in tier]

    for word in words:
        make_syllable_constituents(word)
    
    tg.interleave_class(
        "Syllable",
        below = "Word",
        timing_from = "below"
    )

    for word in words:
        syllabify_word(word)

