from enum import Enum, auto
from app.tosca.parser.impl.tosca_parser import ToskoseParserToscaParser


class ParserType(Enum):
    TOSCA_PARSER = auto()


class ToskoseParserFactory:
    
    @staticmethod
    def create(*, type, **kwargs):
        type = type.upper()
        if type == ParserType.TOSCA_PARSER.name:
            return ToskoseParserToscaParser(*arg, **kwargs)
        else:
            raise ValueError("Invalid parser type: {0}".format(type))