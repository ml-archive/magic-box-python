from django.db.models import Prefetch
from magicbox.django.factories import DjangoIncludeFactory, DjangoAggregatorFactory, DjangoLimiterFactory, \
    DjangoSorterFactory
from tests.django import MagicBoxTestCase as TestCase
from tests.django.fixtures.models import Person, Blog


class TestDjangoIncludeFactory(TestCase):
    def setUp(self):
        self.factory = DjangoIncludeFactory

    def test_can_init(self):
        """
        Tests if factory can be initialized.
        """
        instance = self.factory(Person)
        self.assertIsInstance(instance, self.factory)

    def test_simple_can_parse_include(self):
        """
        Tests if parse_include will return a simple relationship chain.

            Given
                A relationship chain 'articles.comments'
                And RELATION_DELIMITER is set to '.'
                And RELATION_GLUE is '__'
            When
                I try to parse 'articles.comments'
            Then
                I should get back 'articles__comments'
        """
        instance = self.factory(Person)
        relationship_presentation = 'articles' + instance.RELATION_DELIMITER + 'comments'
        includes = instance.parse_include(relationship_presentation)
        self.assertEqual(includes, 'articles' + instance.RELATION_GLUE + 'comments')
        self.assertIsInstance(includes, str)

    def test_can_parse_include_remove_invalid_relationships(self):
        """
        Tests if parse_include will remove all invalid relationships

            Given
                A relationship chain that is not valid: 'not_a_real.relationship'
                And RELATION_DELIMITER is set to: '.'
                And RELATION_GLUE is: '__'
            When
                I try to parse: 'not_a_real.relationship'
            Then
                I should get back: ''
        """
        instance = self.factory(Person)
        relationship_presentation = 'not_a_real' + instance.RELATION_DELIMITER + 'relationship'
        includes = instance.parse_include(relationship_presentation)
        self.assertEqual(includes, '')
        self.assertIsInstance(includes, str)

    def test_can_parse_include_keep_only_valid_relationships(self):
        """
        Tests if parse_include will keep valid relationships and remove invalid relationships

            Given
                A relationship chain that is partially valid: 'articles.invalid_relationship'
                And RELATION_DELIMITER is set to: '.'
                And RELATION_GLUE is: '__'
            When
                I try to parse: 'articles.invalid_relationship'
            Then
                I should get back: 'articles'
        """
        instance = self.factory(Person)
        relationship_presentation = 'articles' + instance.RELATION_DELIMITER + 'invalid_relationship'
        includes = instance.parse_include(relationship_presentation)
        self.assertEqual(includes, 'articles')
        self.assertIsInstance(includes, str)

    def test_can_build_prefetch_list_with_single_item(self):
        """
        Tests if build_prefetch_list will return a list with one Prefetch object.

            Given
                A list of includes: "['articles.comments']"
                And RELATION_DELIMITER is set to: '.'
                And RELATION_GLUE is: '__'
            When
                I try to build a list of Prefetch objects
            Then
                I should get back a list with length: 1
                I should get back a list: [Prefetch(articles__comments)]
        """
        from django.db.models import Prefetch
        instance = self.factory(Person)
        includes = ['articles' + instance.RELATION_DELIMITER + 'comments']
        prefetch_list = instance.build_prefetch_list(includes)

        self.assertIsInstance(prefetch_list, list)
        self.assertEquals(len(prefetch_list), 1)
        self.assertIsInstance(prefetch_list[0], Prefetch)
        self.assertEquals(prefetch_list[0], Prefetch('articles__comments'))

    def test_can_build_prefetch_list_with_multiple_items(self):
        """
        Tests if build_prefetch_list will return a list of multiple Prefetch objects.

            Given
                A list of includes: "['articles.comments', 'person']"
                And RELATION_DELIMITER is set to: '.'
                And RELATION_GLUE is: '__'
            When
                I try to build a list of Prefetch objects
            Then
                I should get back a list with length: 2
                I should get back a list: [Prefetch(articles__comments), Prefetch(person)]
        """
        instance = self.factory(Blog)
        includes = ['articles' + instance.RELATION_DELIMITER + 'comments', 'person']
        prefetch_list = instance.build_prefetch_list(includes)

        self.assertIsInstance(prefetch_list, list)
        self.assertEquals(len(prefetch_list), 2)
        self.assertIsInstance(prefetch_list[0], Prefetch)
        self.assertIsInstance(prefetch_list[1], Prefetch)
        self.assertEquals(prefetch_list[0], Prefetch('articles__comments'))
        self.assertEquals(prefetch_list[1], Prefetch('person'))

    def test_can_build_prefetch_list_when_no_valid_relationship(self):
        """
        Tests if build_prefetch_list will return an empty list if no valid relationships.

            Given
                A list of includes: "['not.a.valid', 'relationship.set']"
                And RELATION_DELIMITER is set to: '.'
                And RELATION_GLUE is: '__'
            When
                I try to build a list of Prefetch objects
            Then
                I should get back an empty list with length: 0
        """
        instance = self.factory(Blog)
        includes = [
            'not' + instance.RELATION_DELIMITER + 'a' + instance.RELATION_DELIMITER + 'valid',
            'relationship' + instance.RELATION_DELIMITER + 'set',
        ]
        prefetch_list = instance.build_prefetch_list(includes)

        self.assertIsInstance(prefetch_list, list)
        self.assertEquals(len(prefetch_list), 0)


class TestDjangoSorterFactory(TestCase):
    def setUp(self):
        self.factory = DjangoSorterFactory

    def test_can_init(self):
        """
        Tests if factory can be initialized.
        """
        from tests.django.fixtures.models import Person
        instance = self.factory(Person)
        self.assertIsInstance(instance, self.factory)

    def test_can_something(self):
        pass


class TestDjangoLimiterFactory(TestCase):
    def setUp(self):
        self.factory = DjangoLimiterFactory

    def test_can_init(self):
        """
        Tests if factory can be initialized.
        """
        from tests.django.fixtures.models import Person
        instance = self.factory(Person)
        self.assertIsInstance(instance, self.factory)

    def test_can_something(self):
        pass


class TestDjangoAggregatorFactory(TestCase):
    def setUp(self):
        self.factory = DjangoAggregatorFactory

    def test_can_init(self):
        """
        Tests if factory can be initialized.
        """
        from tests.django.fixtures.models import Person
        instance = self.factory(Person)
        self.assertIsInstance(instance, self.factory)

    def test_can_something(self):
        pass
