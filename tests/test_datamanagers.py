# -*- coding: utf-8 -*-
import os
import unittest
from pyramid.paster import get_appsettings
from skosprovider_sqlalchemy.utils import import_provider
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import transaction
from zope.sqlalchemy import ZopeTransactionExtension
from skosprovider_sqlalchemy.models import Base, ConceptScheme, LabelType, Language, MatchType, Concept, NoteType, Match
from atramhasis.data.datamanagers import ConceptSchemeManager, SkosManager, LanguagesManager
from fixtures.materials import materials
from fixtures.data import trees, geo


here = os.path.dirname(__file__)
settings = get_appsettings(os.path.join(here, '../', 'tests/conf_test.ini'))


class DatamangersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.session_maker = sessionmaker(
            bind=cls.engine,
            extension=ZopeTransactionExtension()
        )

    def setUp(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        Base.metadata.bind = self.engine

        with transaction.manager:
            local_session = self.session_maker()
            import_provider(trees, ConceptScheme(id=1, uri='urn:x-skosprovider:trees'), local_session)
            import_provider(materials, ConceptScheme(id=4, uri='urn:x-vioe:materials'), local_session)
            import_provider(geo, ConceptScheme(id=2), local_session)
            local_session.add(ConceptScheme(id=3))
            local_session.add(LabelType('hiddenLabel', 'A hidden label.'))
            local_session.add(LabelType('altLabel', 'An alternative label.'))
            local_session.add(LabelType('prefLabel', 'A preferred label.'))
            local_session.add(Language('nl', 'Dutch'))
            local_session.add(Language('en', 'English'))

            local_session.add(MatchType('broadMatch', ''))
            local_session.add(MatchType('closeMatch', ''))
            local_session.add(MatchType('exactMatch', ''))
            local_session.add(MatchType('narrowMatch', ''))
            local_session.add(MatchType('relatedMatch', ''))

            local_session.flush()

            match = Match()
            match.matchtype_id = 'narrowMatch'
            match.uri = 'urn:test'
            match.concept_id = 1
            local_session.add(match)


class ConceptSchemeManagerTest(DatamangersTests):

    def setUp(self):
        super(ConceptSchemeManagerTest, self).setUp()
        self.conceptscheme_manager = ConceptSchemeManager(self.session_maker())

    def test_get(self):
        res = self.conceptscheme_manager.get(1)
        self.assertEqual('urn:x-skosprovider:trees', res.uri)

    def test_find(self):
        query = {'type': 'concept', 'label': 'es'}
        res = self.conceptscheme_manager.find(1, query)
        self.assertEqual(1, len(res))

    def test_get_concepts_for_scheme_tree(self):
        res = self.conceptscheme_manager.get_concepts_for_scheme_tree(2)
        self.assertEqual(1, len(res))

    def test_get_collections_for_scheme_tree(self):
        res = self.conceptscheme_manager.get_collections_for_scheme_tree(2)
        self.assertEqual(1, len(res))

    def test_get_all(self):
        res = self.conceptscheme_manager.get_all(2)
        self.assertEqual(10, len(res))


class SkosManagerTest(DatamangersTests):

    def setUp(self):
        super(SkosManagerTest, self).setUp()
        self.skos_manager = SkosManager(self.session_maker())

    def test_get_thing(self):
        res = self.skos_manager.get_thing(1, 1)
        self.assertEqual('urn:x-skosprovider:trees/1', res.uri)

    def test_save(self):
        thing = Concept()
        thing.concept_id = 123
        thing.conceptscheme_id = 1
        thing = self.skos_manager.save(thing)
        self.assertIsNotNone(thing.id)

    def test_delete_thing(self):
        thing = self.skos_manager.get_thing(1, 1)
        self.skos_manager.delete_thing(thing)
        self.assertRaises(NoResultFound, self.skos_manager.get_thing, 1, 1)

    def test_get_by_list_type(self):
        res = self.skos_manager.get_by_list_type(LabelType)
        self.assertEqual(3, len(res))

    def test_get_match_type(self):
        matchType= self.skos_manager.get_match_type('narrowMatch')
        self.assertEqual('narrowMatch', matchType.name)

    def test_get_match(self):
        match = self.skos_manager.get_match('urn:test', 'narrowMatch', 1)
        self.assertEqual('urn:test', match.uri)

    def test_get_all_label_types(self):
        res = self.skos_manager.get_all_label_types()
        self.assertEqual(3, len(res))

    def test_get_next_cid(self):
        res = self.skos_manager.get_next_cid(1)
        self.assertIsNotNone(res)


class LanguagesManagerTest(DatamangersTests):

    def setUp(self):
        super(LanguagesManagerTest, self).setUp()
        self.language_manager = LanguagesManager(self.session_maker())

    def test_get(self):
        res = self.language_manager.get('nl')
        self.assertEqual('Dutch', res.name)

    def test_save(self):
        language = Language('de', 'German')
        language = self.language_manager.save(language)
        self.assertEqual('German', language.name)

    def test_delete(self):
        language = self.language_manager.get('en')
        self.language_manager.delete(language)
        self.assertRaises(NoResultFound, self.language_manager.get, 'en')

    def test_get_all(self):
        res = self.language_manager.get_all()
        self.assertEqual(2, len(res))

    def test_get_all_sorted(self):
        res = self.language_manager.get_all_sorted('id', False)
        self.assertEqual('en', res[0].id)

    def test_get_all_sorted_desc(self):
        res = self.language_manager.get_all_sorted('id', True)
        self.assertEqual('nl', res[0].id)

    def test_count_languages(self):
        res = self.language_manager.count_languages('nl')
        self.assertEqual(1, res)