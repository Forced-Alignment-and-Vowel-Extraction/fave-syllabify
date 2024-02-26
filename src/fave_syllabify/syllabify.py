from aligned_textgrid import AlignedTextGrid, \
    SequenceInterval
import re
from warnings import warn
O2 = {('P', 'R'), ('T', 'R'), ('K', 'R'), ('B', 'R'), ('D', 'R'),
      ('G', 'R'), ('F', 'R'), ('TH', 'R'),
      ('P', 'L'), ('K', 'L'), ('B', 'L'), ('G', 'L'),
      ('F', 'L'), ('S', 'L'),
      ('K', 'W'), ('G', 'W'), ('S', 'W'),
      ('S', 'P'), ('S', 'T'), ('S', 'K'),
      ('HH', 'Y'), # "clerihew"
      ('R', 'W'), ("HH", "W"),
}

def build_nucleus(
        nucleus: SequenceInterval,
        nuclei: list[SequenceInterval]
    ):
    stress = re.findall(r"\d", nucleus.contains[0].label)[0]
    nucleus.set_feature("stress", stress)
    nucleus.label = "nucleus"

    nucleus.set_feature("onset", None)
    nucleus.set_feature("coda", None)

    nucleus.last.set_feature("onset", None)
    nucleus.last.set_feature("coda", None)

    if not (nucleus.prev.label == "Y" and \
            "UW" in nucleus.last.label):
        return

    if (nucleus.prev.prev.label != "#") and \
        nucleus.prev.prev not in nuclei:
        nucleus.fuse_leftwards(label_fun = lambda x,y: y)

def build_onset(nucleus):
    if nucleus.prev.label == "#" or \
       nucleus.prev.label == "NG" or \
       nucleus.prev.label == "nucleus":
        return
    
    nucleus.prev.label = "onset"

    nucleus.onset = nucleus.prev

    nucleus.last.onset = nucleus.prev

    maximized = False
    while not maximized:
        current_onsets = nucleus.prev.sub_labels
        candidate_segment = nucleus.prev.prev
        candidate_label = candidate_segment.label

        if candidate_label == "#":
            maximized = True
            return

        if not (candidate_label, current_onsets[0]) in O2:
            maximized = True
            return

        nucleus.prev.fuse_leftwards(label_fun=lambda x, y: y)
    
def build_coda(nucleus):
    cleanedup = False
    while not cleanedup:
        if nucleus.fol.label == "#":
            cleanedup = True
            return
        
        if nucleus.fol.label in ["onset", "nucleus"]:
            cleanedup = True
            return

        nucleus.fol.label = "coda"

        nucleus.coda = nucleus.fol
        nucleus.last.coda = nucleus.fol

        if nucleus.fol.fol.label == "#":
            cleanedup = True
            return
        
        if nucleus.fol.fol.label in ["onset", "nucleus"]:
            cleanedup = True
            return
        
        nucleus.fol.fuse_rightwards(label_fun = lambda x, y: x)    
    

def make_syllable_constituents(word: SequenceInterval):
    """Make syllable constituents for a word interval

    Args:
        word (SequenceInterval): A SequenceInterval for a word.
    """

    parts = [p for p in word.contains]
    nuclei = [x for x in parts if re.match(r"[AEIOU]", x.label)]

    if len(nuclei) == 0:
        return
    
    for n in nuclei:
        build_nucleus(n, nuclei)

    for n in nuclei:
        build_onset(n)

    for n in nuclei:
        build_coda(n)

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
        n.set_feature("nucleus", n.last)
        n.set_feature("onset", None)
        n.set_feature("coda", None)

        if n.prev.label == "onset":
            n.onset = n.prev.last
            n.fuse_leftwards(lambda x, y: y)
        
        if n.fol.label == "coda":
            n.coda = n.fol.first
            n.fuse_rightwards(lambda x,y: x)


def syllabify_tg(tg: AlignedTextGrid):
    """Syllabify an entire AlignedTextGrid
    
    Args:
        tg (AlignedTextGrid): The textgrid to syllabify
    """

    tg_entry_classes = {
        c.__name__ 
        for gr in tg.entry_classes 
        for c in gr
    }

    if "Syllable" in tg_entry_classes or \
       "SylPart" in tg_entry_classes:
        warn(f"TextGrid with groups {[gr.name for gr in tg]} already syllabified.")
        return

    for tgr in tg:
        for p in tgr.Phone:
            p.set_feature("old_id", p.id)

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

