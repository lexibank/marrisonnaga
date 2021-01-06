from collections import defaultdict
from pathlib import Path
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Language
from pylexibank import FormSpec
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
    form_spec = FormSpec(
            missing_data=("*", "---", ""),
            brackets={"[": "]", "(": ")"}
            )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        wl = lingpy.Wordlist(self.raw_dir.joinpath("GEM-CNL.csv").as_posix())
        concepts = args.writer.add_concepts(
                id_factory=lambda x: x.id.split('-')[-1]+'_'+slug(x.english),
                lookup_factory="Name"
                )
        for concept in self.conceptlists[0].concepts.values():
            for cis in concept.attributes['lexibank_gloss']:
                if cis not in concepts:
                    concepts[cis] = concepts[concept.english]

        languages = args.writer.add_languages(
                lookup_factory="STEDT_Name")
        args.writer.add_sources()

        for idx, language, concept, value, pos in wl.iter_rows("doculect", "concept", "reflex", "gfn"):
            # Fix for 251479
            if concept == "top (i.e. highest point":
                concept = "top (i.e. highest point)"

            if concept not in concepts:
                args.log.warning(concept)
            else:
                args.writer.add_forms_from_value(
                    Language_ID=languages[language],
                    Parameter_ID=concepts[concept],
                    Value=value,
                    Source=["Marrison1967"],
                )
