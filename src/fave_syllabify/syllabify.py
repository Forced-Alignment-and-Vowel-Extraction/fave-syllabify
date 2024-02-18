from aligned_textgrid import AlignedTextGrid, \
    custom_classes,\
    SequenceInterval
from syllabify import SLAX, VOWELS, O2, O3
import re

O2.add(("HH", "W"))
O2.add(("B", "Y"))

def syllabify_word(word: SequenceInterval):
    """Syllabify a single word

    Args:
        word (SequenceInterval): The word Sequence Interval to syllabify
    """
    parts = [x for p in word.contains for x in p.contains]
    nuclei = [x for x in parts if re.match(r"[AEIOU]", x.label)]

    if len(nuclei) == 0:
        return

    for n in nuclei:
        stress = re.findall(r"\d", n.contains[0].label)[0]
        n.set_feature("stress", stress)
        n.label = "nucleus"
        n.within.label = f"syl-{n.stress}"

        if n.within.prev.label != "#" and \
           n.within.prev.label != "NG" and\
           n.within.prev.last not in nuclei:
            n.within.prev.last.label = "onset"
            n.within.fuse_leftwards(label_fun=lambda x, y: y)

        if n.prev.label == "onset":
            maximized = False
            while not maximized:
                current_onsets = n.prev.sub_labels
                candidate_set = n.prev.within.prev
                if candidate_set.label == "#":
                    maximized = True
                    break
                
                candidate_segment = n.prev.within.prev.last
                candidate_label = candidate_segment.label

                if (candidate_label, current_onsets[0]) in O2:
                    n.prev.within.fuse_leftwards(label_fun=lambda x, y: y)
                    n.prev.fuse_leftwards(label_fun=lambda x, y: y)
                else:
                    maximized = True

    for n in nuclei:
        cleanedup = False
        while not cleanedup:
            if n.within.fol.label == "#":
                cleanedup = True
                break
            if "syl" in n.within.fol.label:
                cleanedup = True
                break
            n.within.fuse_rightwards(label_fun=lambda x,y: x)
        
        if n.fol.label != "#":
            n.fol.label = "coda"

            codaed = False
            while not codaed:
                if n.fol.fol.label == "#":
                    codaed = True
                    break
                n.fol.fuse_rightwards(label_fun = lambda x, y: x)

def syllabify_tg(tg: AlignedTextGrid):
    """Syllabify an entire AlignedTextGrid
    Args:
        tg (AlignedTextGrid): The textgrid to syllabify

    """

    tg.interleave_class(
        "Syllable",
        below = "Word",
        timing_from = "below"
    )

    tg.interleave_class(
        "SylPart",
        above = "Phone",
        timing_from = "below"
    )

    word_tiers = [tgr.Word for tgr in tg]
    words = [seq for tier in word_tiers for seq in tier]

    for word in words:
        syllabify_word(word)
