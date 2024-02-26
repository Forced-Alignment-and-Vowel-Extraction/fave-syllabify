# fave-syllabify


![](https://img.shields.io/badge/Lifecycle-Maturing-lightgreen@2x.png)
![PyPI version](https://badge.fury.io/py/fave-syllabify.svg) [![Lint and
Test](https://github.com/Forced-Alignment-and-Vowel-Extraction/fave-syllabify/actions/workflows/lint-and-test.yml/badge.svg)](https://github.com/Forced-Alignment-and-Vowel-Extraction/fave-syllabify/actions/workflows/lint-and-test.yml)
[![Build
Docs](https://github.com/Forced-Alignment-and-Vowel-Extraction/fave-syllabify/actions/workflows/build_docs.yml/badge.svg)](https://forced-alignment-and-vowel-extraction.github.io/fave-syllabify/)
[![codecov](https://codecov.io/gh/Forced-Alignment-and-Vowel-Extraction/fave-syllabify/graph/badge.svg?token=WDBJ0O9P6L)](https://codecov.io/gh/Forced-Alignment-and-Vowel-Extraction/fave-syllabify)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10708119.svg)](https://doi.org/10.5281/zenodo.10708119)

Syllabify a force-aligned TextGrid

## Installation

``` bash
pip install fave-syllabify
```

## Usage

Import classes and functions

``` python
from aligned_textgrid import AlignedTextGrid, custom_classes
from fave_syllabify import syllabify_tg
from pathlib import Path
```

Read in a textgrid

``` python
tg = AlignedTextGrid(
    textgrid_path=Path(
        "docs",
        "data",
        "josef-fruehwald_speaker.TextGrid"
    ),
    entry_classes=custom_classes(
        ["Word", "Phone"]
    )
)

print(tg)
```

    AlignedTextGrid with 1 groups named ['group_0'] each with [2] tiers. [['Word', 'Phone']]

Syllabify the textgrid

``` python
syllabify_tg(tg)

print(tg)
```

    AlignedTextGrid with 1 groups named ['group_0'] each with [4] tiers. [['Word', 'Syllable', 'SylPart', 'Phone']]

### Exploring the syllabification

``` python
word_tier = tg.group_0.Word
raindrops = word_tier[5]

print(raindrops.label)
```

    raindrops

Each syllable is labelled with its stress.

``` python
print([
    syl.label 
    for syl in raindrops.contains
])
```

    ['syl-1', 'syl-2']

Each syllable contains its constituent parts in a flat hierarchy
(there’s no rhyme constituent).

``` python
syl = raindrops.first.fol
print([
    part.label
    for part in syl.contains
])
```

    ['onset', 'nucleus', 'coda']

Each constituent contains its relevant phone.

``` python
onset = syl.onset
print([
    phone.label
    for phone in onset
])
```

    ['D', 'R']
