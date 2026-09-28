# Sources and reuse

VIVA+ models are distributed under LGPL v3. The validation repository identifies simulation environments as Apache 2.0 (unless otherwise stated) and notebooks as CC BY 4.0. See the [upstream license description](https://openvt.eu/fem/viva/vivaplus-validation/-/blob/84-demetropoulos-1998-lumbar-spine/README.md) and [current model documentation](https://vivaplus.readthedocs.io/). This package does not redistribute the full HBM or modified model decks.

The reference CSVs are unchanged copies from the VIVA+ validation archive; original paths are documented in `docs/METHODS.md`. Their attribution remains with the VIVA+ contributors and original experimental authors. Our formatting and comparisons do not create ownership of the source data. Confirm any loadcase-specific notices when redistributing those datasets.

Dynasaur 1.3.18 is an unchanged GPLv3 dependency from VSI TU Graz. Its wheel includes Python source and license text. The full license is also reproduced in `analysis/vendor/LICENSE-Dynasaur.txt`. Source: https://gitlab.com/VSI-TUGraz/Dynasaur ; release: https://pypi.org/project/dynasaur/1.3.18/ . The force routine is unmodified.

New explanatory text and analysis scripts have not yet been assigned a general redistribution license by the project author. No blanket license overrides the upstream terms. Students may access the materials here; contact the author before redistributing newly authored material until a license is selected.
