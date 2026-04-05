from __future__ import annotations

from typing import Type

from parsers.base_parser import BaseParser
from parsers.davv_parser import DavvParser
from parsers.jiwaji_parser import JiwajiParser
from parsers.mp_portal_parser import MpPortalParser
from parsers.rgpv_parser import RgpvParser

PARSER_REGISTRY: dict[str, Type[BaseParser]] = {
    "rgpv": RgpvParser,
    "davv": DavvParser,
    "jiwaji": JiwajiParser,
    "mp_portal": MpPortalParser,
}
