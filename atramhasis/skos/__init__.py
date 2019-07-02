# -*- coding: utf-8 -*-

import logging

from skosprovider.uri import UriPatternGenerator
from skosprovider_sqlalchemy.providers import SQLAlchemyProvider
from sqlalchemy import create_engine

log = logging.getLogger(__name__)


def includeme(config):  # pragma: no cover
    skosregis = config.get_skos_registry()
    [skosregis.register_provider(provider) for provider in get_internal_providers(config)]


def get_internal_providers(config):
    ret = []
    engine = create_engine(config.get_settings()['sqlalchemy.url'], echo=True)
    engine.connect()
    result = engine.execute('SELECT * from conceptscheme')
    for row in result:
        scheme_db_id = row[0]
        scheme_uri = row[1]
        scheme_id = scheme_uri.split('/')[-1]
        scheme = SQLAlchemyProvider({
            'id': scheme_id,
            'conceptscheme_id': scheme_db_id
        }, config.registry.dbmaker, uri_generator=UriPatternGenerator(f'{scheme_uri}/%s'))
        ret.append(scheme)
    engine.dispose()
    return ret
