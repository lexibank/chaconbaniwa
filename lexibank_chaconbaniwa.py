import attr
import lingpy
from clldutils.misc import slug
from clldutils.path import Path
from pylexibank.dataset import Concept
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import pb


@attr.s
class BDConcept(Concept):
    Portuguese_Gloss = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "chaconbaniwa"
    concept_class = BDConcept

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):

        wl = lingpy.Wordlist(self.raw.posix("Bruzzi_Granadillo.txt"))

        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())
            for k in pb(wl, desc="wl-to-cldf"):
                ds.add_language(
                    ID=slug(wl[k, "doculect"]), Name=wl[k, "doculect"], Glottocode="bani1255"
                )

                ds.add_concept(
                    ID=slug(wl[k, "concept"]),
                    Name=wl[k, "concept"],
                    Concepticon_ID=wl[k, "concepticon_id"] or "",
                    Portuguese_Gloss=wl[k, "concept_portuguese"],
                )

                for row in ds.add_lexemes(
                    Language_ID=slug(wl[k, "doculect"]),
                    Parameter_ID=slug(wl[k, "concept"]),
                    Value=wl[k, "entrj_in_source"],
                    Form=wl[k, "ipa"],
                    Segments=wl[k, "tokens"],
                    Source=["granadillo_ethnographic_2006", "silva_discoteca_1961"],
                ):
                    cid = slug(wl[k, "concept"] + "-" + "{0}".format(wl[k, "cogid"]))
                    ds.add_cognate(
                        lexeme=row,
                        Cognateset_ID=cid,
                        Source=["Chacon2018"],
                        Alignment=wl[k, "alignment"],
                        Alignment_Source="Chacon2018",
                    )
