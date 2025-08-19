from .mushafs.views import MushafViewSet
from .surahs.views import SurahViewSet
from .ayahs.views import AyahViewSet
from .words.views import WordViewSet
from .translations.views import TranslationViewSet
from .recitations.views import RecitationViewSet
from .takhtits.views import TakhtitViewSet

__all__ = [
	"MushafViewSet",
	"SurahViewSet",
	"AyahViewSet",
	"WordViewSet",
	"TranslationViewSet",
	"RecitationViewSet",
	"TakhtitViewSet",
]
