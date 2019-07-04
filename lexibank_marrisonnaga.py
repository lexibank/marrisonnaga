from collections import defaultdict

import lingpy
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import NonSplittingDataset
from tqdm import tqdm


class Dataset(NonSplittingDataset):
    dir = Path(__file__).parent
    id = "marrisonnaga"

    def clean_form(self, item, form):
        if form not in ["*", "---", ""]:
            return split_text(strip_brackets(form), ",;/")[0]

    def cmd_install(self, **kw):
        """
        Convert the raw data to a CLDF dataset.
        """

        data = lingpy.Wordlist(self.dir.joinpath("raw", "GEM-CNL.csv").as_posix())

        languages, concepts = {}, {}
        missing = defaultdict(int)
        with self.cldf as ds:
            concepts = {c.english: c.id for c in self.conceptlist.concepts.values()}
            for c in self.concepts:
                if c["ENGLISH"] not in concepts:
                    concepts[c["ENGLISH"]] = c["ID"]
                ds.add_concept(
                    ID=c["ID"],
                    Name=c["ENGLISH"],
                    Concepticon_ID=c["CONCEPTICON_ID"],
                    Concepticon_Gloss=c["CONCEPTICON_GLOSS"],
                )

            ds.add_concepts(id_factory=lambda c: c.id)

            for language in self.languages:
                ds.add_language(
                    ID=slug(language["Language_in_source"]),
                    Glottocode=language["Glottolog"],
                    Name=language["Language_in_STEDT"],
                )
                languages[language["Language_in_STEDT"]] = slug(language["Language_in_source"])

            ds.add_sources(*self.raw.read_bib())
            for idx, language, concept, value, pos in tqdm(
                data.iter_rows("doculect", "concept", "reflex", "gfn"),
                desc="cldfify",
                total=len(data),
            ):

                if value.strip():
                    if concept not in concepts:
                        if pos == "n":
                            if concept + " (noun)" in concepts:
                                concept = concept + " (noun)"
                            else:
                                missing[concept] += 1
                        elif pos == "adj":
                            if concept + " (adj.)" in concepts:
                                concept = concept + " (adj.)"
                            else:
                                missing[concept] += 1
                        else:
                            missing[concept] += 1

                    if concept not in missing:
                        ds.add_lexemes(
                            Language_ID=languages[language],
                            Parameter_ID=concepts[concept],
                            Value=self.lexemes.get(value, value),
                            Source=["Marrison1967"],
                        )
            for i, m in enumerate(missing):
                print(str(i + 1) + "\t" + m)
