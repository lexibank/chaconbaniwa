import attr
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

        # add languages
        languages = args.writer.add_languages(lookup_factory="Name")

        # Hard-coded fixes to segment errors in raw source
        segments = {
            "aʰ": "a h",
            "ɐ̃ʰ": "ɐ̃ h",
            "iʰ": "i h",
            "ka": "k a",
            "nⁱ": "n i",
            "teː": "t eː",
        }

        # read wordlist with lingpy
        wl_file = self.raw_dir / "Bruzzi_Granadillo.txt"
        wl = lingpy.Wordlist(wl_file.as_posix())

        # iterate over wordlist
        concepts = {}
        for idx in progressbar(wl, desc="makecldf"):
            # Concepts need to be added one by one, due to the source struct
            # Given that the source has mixed items and no internal index,
            # we need to build the first item of `concept_cldf_id` manually
            if wl[idx, "concept"] not in concepts:
                concept_cldf_id = "%i_%s" % (
                    len(concepts) + 1,
                    slug(wl[idx, "concept"]),
                )

                args.writer.add_concept(
                    ID=concept_cldf_id,
                    Name=wl[idx, "concept"],
                    Concepticon_ID=wl[idx, "concepticon_id"] or "",
                    Portuguese_Gloss=wl[idx, "concept_portuguese"],
                )

                # only update `concepts` if key is not found
                concepts[wl[idx, "concept"]] = concept_cldf_id

            # write lexemes
            lex = args.writer.add_form_with_segments(
                Language_ID=languages[wl[idx, "doculect"]],
                Parameter_ID=concepts[wl[idx, "concept"]],
                Value=wl[idx, "entrj_in_source"],
                Form=wl[idx, "ipa"],
                Segments=" ".join(
                    [segments.get(x, x) for x in wl[idx, "tokens"]]
                ).split(),
                Source=["granadillo_ethnographic_2006", "silva_discoteca_1961"],
            )

            cid = "%s-%s" % (slug(wl[idx, "concept"]), wl[idx, "cogid"])
            args.writer.add_cognate(
                lexeme=lex, Cognateset_ID=cid, Source=["Chacon2018"]
            )
