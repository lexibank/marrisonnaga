from collections import defaultdict

import lingpy
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.dataset import Language
from tqdm import tqdm
import attr

@attr.s
class OurLanguage(Language):
    STEDT_Name = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Coverage = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    Latitude = attr.ib(default=None)
    Area = attr.ib(default=None)

class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "marrisonnaga"
    language_class = OurLanguage

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
            for c in self.conceptlist.concepts.values():
                if c.english not in concepts:
                    concepts[c.english] = c.id
                ds.add_concept(
                    ID=c.id,
                    Name=c.english,
                    Concepticon_ID=c.concepticon_id,
                    Concepticon_Gloss=c.concepticon_gloss,
                )

            ds.add_concepts(id_factory=lambda c: c.id)
            ds.add_languages()
            languages = {k["STEDT_Name"]: k['ID'] for k in self.languages}
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
