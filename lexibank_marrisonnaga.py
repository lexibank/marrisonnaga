from collections import defaultdict
from pathlib import Path
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Language
from pylexibank import FormSpec
from pylexibank.util import progressbar
from clldutils.misc import slug
import lingpy
import attr


@attr.s
class CustomLanguage(Language):
    STEDT_Name = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Coverage = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    Latitude = attr.ib(default=None)
    Area = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "marrisonnaga"
    language_class = CustomLanguage
    form_spec = FormSpec(missing_data=("*", "---", ""), brackets={"[": "]", "(": ")"})

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        wl = lingpy.Wordlist(self.raw_dir.joinpath("GEM-CNL.csv").as_posix())
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: x.id.split("-")[-1] + "_" + slug(x.english), lookup_factory="Name"
        )
        language_lookup = args.writer.add_languages(lookup_factory="STEDT_Name")
        args.writer.add_sources()
        # check for missing items
        missing = defaultdict(int)
        for idx, language, concept, value, pos in progressbar(
            wl.iter_rows("doculect", "concept", "reflex", "gfn")
        ):
            if concept not in concept_lookup:
                if pos == "n":
                    if concept + " (noun)" in concept_lookup:
                        concept = concept + " (noun)"
                    else:
                        missing[concept] += 1
                elif pos == "adj":
                    if concept + " (adj.)" in concept_lookup:
                        concept = concept + " (adj.)"
                    else:
                        missing[concept] += 1
                else:
                    missing[concept] += 1
            if concept not in missing:
                args.writer.add_forms_from_value(
                    Language_ID=language_lookup[language],
                    Parameter_ID=concept_lookup[concept],
                    Value=value,
                    Source=["Marrison1967"],
                )
