from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q


class DjangoIncludeFactory:
    # @TODO this should be applied via a config.
    RELATION_DELIMITER = '.'
    RELATION_GLUE = '__'

    def __init__(self, model):
        self.model = model

    def parse_include(self, relation_chain):
        """
        Parses a relationship chain and formats into a valid django format.
        Relationships are validated. Relationship's that do not exist will break
        the chain and only the prior valid relationships will be returned.

        Relationship chains are delimited strings, ex: 'author.articles.comments'

        In the example above if `articles` was an invalid relationship then only
        the author relationship would be returned.

        Params:
            relation_chain (str) - A delimited string representing a relationship chain.

        Returns:
            str - Either an empty string if all relationships were invalid. Or a relationship chain.

        :param relation_chain:
        :return:
        """
        from django.core.exceptions import FieldDoesNotExist

        relation_list = []

        # Start cursor
        current_model = self.model

        # We split the chain by it's delimiter, verifying each relation as we
        # move the model cursor down the chain. In the end we join the valid
        # list of relations, creating a new valid relation chain.
        for related in relation_chain.split(self.RELATION_DELIMITER):

            try:
                current_model = current_model._meta.get_field(related).related_model

                relation_list.append(related)

            except FieldDoesNotExist:
                return self.RELATION_GLUE.join(relation_list)

        return self.RELATION_GLUE.join(relation_list)

    def build_prefetch_list(self, includes):
        from django.db.models import Prefetch

        prefetch_list = []

        for include in includes:
            include = self.parse_include(include)

            if include is not '':
                p = Prefetch(include)
                prefetch_list.append(p)

        return prefetch_list


class DjangoLimiterFactory:
    """
    Some TODOs:
    Add filtering across relationship chain: https://docs.djangoproject.com/en/1.9/topics/db/queries/#lookups-that-span-relationships
    All __in filters need to be properly parsed. Currently they will fail to parse correctly.
    """
    supported_tokens = {
        '^': ('__startswith', 'filter'),
        '~': ('__contains', 'filter'),
        '$': ('__endswith', 'filter'),
        '<': ('__lt', 'filter'),
        '>': ('__gt', 'filter'),
        '>=': ('__gte', 'filter'),
        '<=': ('__lte', 'filter'),
        '=': ('', 'filter'),
        '[': ('__in', 'filter'),
        '!=': ('', 'exclude'),
        '![': ('__in', 'exclude'),
        '!~': ('__contains', 'exclude'),
    }

    supported_tokens_one_char = [
        '^',
        '~',
        '$',
        '<',
        '>',
        '=',
        '[',
    ]

    supported_tokens_two_char = [
        '>=',
        '<=',
        '!=',
        '![',
        '!~',
    ]

    def __init__(self, query_set):
        self.query_set = query_set
        self.q = Q()

    def determine_limiter(self, token_value):
        """
        This method parses a token value string and performs a lookup against the
        supported_tokens returning the method, token, and value.

        @TODO consider removing the method as a parameter that is returned.

        Example:
                given a string like "=joe"

                it will return "filter", "", "joe"

                The first value is

        :param token_value: str
        :return: str, str, str
        """
        if token_value[0] in self.supported_tokens_one_char:
            token, method = self.supported_tokens[token_value[0]]
            value = token_value[1:]
            return method, token, value

        if token_value[:2] in self.supported_tokens_two_char:
            token, method = self.supported_tokens[token_value[:2]]
            value = token_value[2:]
            return method, token, value

    def construct_simple_query_set(self, filters):

        limiters = {
            'filter': {},
            'exclude': {},
        }

        query_set = self.query_set

        for column, limiter in filters.items():
            try:
                self.query_set.model._meta.get_field(column)
                method, token, value = self.determine_limiter(limiter)
                limiters[method][column + token] = value
            except FieldDoesNotExist:
                pass

        if limiters['filter']:
            query_set = query_set.filter(**limiters['filter'])

        if limiters['exclude']:
            query_set = query_set.exclude(**limiters['exclude'])

        return query_set

    def construct_complex_query_set(self, filters):
        query_dict = self.recursive_queries(filters, filters)

        q = self.q
        q = self.forward_build_qs(query_dict, q)

        return self.query_set.filter(q)

    def forward_build_qs(self, tree, q, operator=Q.AND):
        # @TODO figure out how you eneded up actually making it work... Try to improve code readability...
        popdq = q.add(tree.pop('q'), operator)

        if tree:
            for k, v in tree.items():
                if k == 'or':
                    self.forward_build_qs(v, popdq, Q.OR)
                if k == 'and':
                    self.forward_build_qs(v, popdq, Q.AND)

        return popdq

    def recursive_queries(self, dict_queries, current):
        apply = {}
        negate = {}

        new_tree = {}

        for k, v in dict_queries.items():
            if isinstance(v, dict):
                current = current[k]
                new_tree[k] = self.recursive_queries(v, current)
            else:
                try:
                    self.query_set.model._meta.get_field(k)
                    method, token, value = self.determine_limiter(v)

                    if method == 'filter':
                        apply[k + token] = value
                    if method == 'exclude':
                        negate[k + token] = value
                except FieldDoesNotExist:
                    pass

        if apply and negate:
            new_tree['q'] = Q(**apply) & ~Q(**negate)
        elif apply:
            new_tree['q'] = Q(**apply)
        elif negate:
            new_tree['q'] = ~Q(**negate)

        return new_tree

    def construct_query_set(self, filters):

        if 'and' not in filters and 'or' not in filters:
            return self.construct_simple_query_set(filters)

        return self.construct_complex_query_set(filters)


class DjangoRepository:
    """
    Some TODOs:
    Depth Restriction for limiter statements and includes...
    Convert Setters/Getters to whatever is the "pythonic way"
    """

    def __init__(self, model):
        self.model = None
        self.filters = {}
        self.includes = []
        self.set_model(model)
        self.query_set = None
        self.input = {}
        self.fillable = []

    def set_input(self, inputdict):
        self.input = inputdict
        return self

    def set_fillable(self, fillable):
        self.fillable = fillable
        return self

    def set_model(self, model):
        """
        Set model.

        :param model:
        :return:
        """
        self.model = model
        return self

    def set_filters(self, filters):
        """
        Set filters.

        :param filters:
        :return:
        """
        self.filters = filters
        return self

    def set_includes(self, includes):
        """
        Set includes.

        :param includes:
        :return:
        """
        if isinstance(includes, str):
            self.includes = [includes]
        else:
            self.includes = includes
        return self

    def query(self):
        query = self._modify_query()
        return query

    def _modify_query(self):
        filters = self.filters
        includes = self.includes

        query_set = self.model.objects.get_queryset()

        if filters:
            query_set = DjangoLimiterFactory(query_set).construct_query_set(filters)
            print(query_set.query)  # @TODO temp, debugging...

        # If has relations to include pass to factory.
        if includes:
            # @TODO right now this passes back a list for the prefetch object. LimiterFactory and IncludeFactory should work the same way for consistency sake.
            query_set = query_set.prefetch_related(*DjangoIncludeFactory(self.model).build_prefetch_list(includes))

        # APPLY Group by methods if exists

        # APPLY Aggregate Methods if exists

        # APPLY Sort method if exists

        return query_set

    def all(self):
        return self.query().all()

    def delete(self, pk=None):
        if pk:
            return self.delete_one(pk)

        deleted = self.query().delete()

        if deleted[0]:
            return deleted
        else:
            return False

    def delete_one(self, pk):
        try:
            return self.model.objects.get(pk=pk).delete()
        except self.model.DoesNotExist:
            return False

    def find(self, pk):
        try:
            return self.query().get(pk=pk)
        except self.model.DoesNotExist:
            return False

    def execute(self):
        # @TODO
        # iterate over all query sets to execute them and return results.
        pass

    def _check_relation(self):
        pass
