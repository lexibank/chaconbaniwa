import attr
from collections import defaultdict
import lingpy
from clldutils.misc import slug
from clldutils.path import Path
from pylexibank import Concept
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar


@attr.s
class CustomConcept(Concept):
    Portuguese_Gloss = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "chaconbaniwa"
    concept_class = CustomConcept

    def cmd_makecldf(self, args):
        # add sources
        args.writer.add_sources()

        # add language
        languages = {}
        sources = defaultdict()
        for language in self.languages:
            args.writer.add_language(
                    ID=language["ID"],
                    Name=language["Name"],
                    Glottocode=language["Glottocode"]
                    )
            languages[language["Name"]] = language["ID"]
            sources[language["Name"]] = language["Source"]
        args.log.info("added languages")

        # add concepts
        concepts = args.writer.add_concepts(
            id_factory=lambda cpt: "%s_%s"
            % (cpt.id.split("_")[0], slug(cpt.english)),
            lookup_factory="Name",
        )

        # Hard-coded fixes to segment errors in raw source
        segments = {
            "áː": "áː/aː",
            "âː": "âː/aː",
            "aʰ": "a h",
            "ɐ̃ʰ": "ɐ̃ h",
            "í": "í/i",
            "íː": "íː/iː",
            "iʰ": "i h",
            "i̥": "i̥/i",
            "ka": "k a",
            "kw": "kʷ",  # the single instance is a labialized velar
            "nⁱ": "n i",
            "óː": "óː/oː",
            "teː": "t eː",
            "ú": "u/u",
            '#': '+'
        }

        # read wordlist with lingpy
        wl_file = self.raw_dir / "Bruzzi_Granadillo.txt"
        wl = lingpy.Wordlist(wl_file.as_posix())

        # iterate over wordlist
        for idx in progressbar(wl, desc="makecldf"):
            # write lexemes
            lex = args.writer.add_form_with_segments(
                Language_ID=languages[wl[idx, "doculect"]],
                Parameter_ID=concepts[wl[idx, "concept"]],
                Value=wl[idx, "entry_in_source"],
                Form=wl[idx, "ipa"],
                Segments=" ".join(
                    [segments.get(x, x) for x in wl[idx, "tokens"]]
                ).split(),
                Source=sources[wl[idx, "doculect"]]
            )

            args.writer.add_cognate(
                lexeme=lex,
                Cognateset_ID=wl[idx, "cogid"],
                Source=["Chacon2019"],
            )
