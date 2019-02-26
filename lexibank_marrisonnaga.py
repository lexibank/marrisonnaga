# coding=utf-8
from __future__ import unicode_literals, print_function

from clldutils.path import Path
from pylexibank.dataset import NonSplittingDataset
from clldutils.misc import slug
from clldutils.text import split_text, strip_brackets

from tqdm import tqdm
from collections import defaultdict

import re
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

    def clean_form(self, item, form):
        if form not in ['*', '---', '']:
            return split_text(strip_brackets(form), ',;/')[0]

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
                        ID=concept['ID'],
                        Name=concept['ENGLISH'],
                        Concepticon_ID=concept['CONCEPTICON_ID'],
                        Concepticon_Gloss=concept['CONCEPTICON_GLOSS']
                        )
                concepts[concept['ENGLISH']] = concept['ID']
            for language in self.languages:
                ds.add_language(
                        ID=slug(language['Language_in_source']),
                        Glottocode=language['Glottolog'],
                        Name=language['Language_in_STEDT']
                        )
                languages[language['Language_in_STEDT']] = slug(language['Language_in_source'])

            ds.add_sources(*self.raw.read_bib())
            for idx, language, concept, value, pos in tqdm(data.iter_rows(
                'doculect', 'concept', 'reflex', 'gfn'), desc='cldfify the data'):

                if value.strip():
                    if concept not in concepts:
                        if pos == 'n':
                            if concept+' (noun)' in concepts:
                                concept = concept+' (noun)'
                            else:
                                missing[concept] +=1
                        elif pos == 'adj':
                            if concept+' (adj.)' in concepts:
                                concept = concept+' (adj.)'
                            else:
                                missing[concept] +=1
                        else:
                            missing[concept] += 1
                    
                    if concept not in missing:
                        ds.add_lexemes(
                                Language_ID=languages[language],
                                Parameter_ID=concepts[concept],
                                Value=self.lexemes.get(value, value),
                                Source=['Marrison1967']
                                )
            for i, m in enumerate(missing):
                print(str(i+1)+'\t'+m)



