# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.path import Path
from pylexibank.dataset import NonSplittingDataset
from clldutils.misc import slug

from tqdm import tqdm
from collections import defaultdict

import lingpy


class Dataset(NonSplittingDataset):
    dir = Path(__file__).parent
    id = "marrisonnaga"

    def cmd_download(self, **kw):
        """
        Download files to the raw/ directory. You can use helpers methods of `self.raw`, e.g.

        >>> self.raw.download(url, fname)
        """
        pass

    def cmd_install(self, **kw):
        """
        Convert the raw data to a CLDF dataset.
        """

        data = lingpy.Wordlist(self.dir.joinpath(
            'raw',
            'GEM-CNL.csv').as_posix())
        languages, concepts = {}, {}
        missing = defaultdict(int)
        with self.cldf as ds:
            for concept in self.concepts:
                ds.add_concept(
                        ID=concept['NUMBER'],
                        Name=concept['ENGLISH'],
                        Concepticon_ID=concept['CONCEPTICON_ID'],
                        Concepticon_Gloss=concept['CONCEPTICON_GLOSS']
                        )
                concepts[concept['ENGLISH']] = concept['NUMBER']
            for language in self.languages:
                ds.add_language(
                        ID=slug(language['Language_in_source']),
                        Glottocode=language['Glottolog'],
                        Name=['Language_in_source']
                        )
                languages[language['Language_in_STEDT']] = slug(language['Language_in_source'])

            ds.add_sources(*self.raw.read_bib())
            for idx, language, concept, value in tqdm(data.iter_rows(
                'doculect', 'concept', 'reflex'), desc='cldfify the data'):
                segments = ''
                if value.strip():
                    if concept not in concepts:
                        missing[concept] += 1
                    else:
                        ds.add_lexemes(
                                Language_ID=languages[language],
                                Parameter_ID=concepts[concept],
                                Form=value.split(','),
                                Value=value,
                                Source=['Marrison1967']
                                )
            for i, m in enumerate(missing):
                print(str(i+1)+'\t'+m)



