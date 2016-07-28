class DjangoFiltersFactory:
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

    def __init__(self):
        pass

    @classmethod
    def parse_filters(cls, filters):
        # @TODO need to also remove fields that the model does not have.
        # if the model does not have a field called "some_field" then the "some_field" filter should not be applied.
        # Currently it will try to apply it and throws a django.core.exceptions.FieldError
        parsed_filters = {}

        for column, token_value_string in filters.items():

            # or statement logic
            if column == 'or' and isinstance(token_value_string, dict):
                continue  # @TODO logic needs to be implemented to handle these.

            # # and statement logic
            if column == 'and' and isinstance(token_value_string, dict):
                continue  # @TODO logic needs to be implemented to handle these.

            # Basic filter logic
            method, token, value = cls.determine_filter_token_and_value(token_value_string)

            if method not in parsed_filters:
                parsed_filters[method] = {}

            parsed_filters[method][column + token] = value

        print(parsed_filters)
        return parsed_filters

    @classmethod
    def determine_filter_token_and_value(cls, token_value):
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
        if token_value[0] in cls.supported_tokens_one_char:
            token, method = cls.supported_tokens[token_value[0]]
            value = token_value[1:]
            return method, token, value

        if token_value[:2] in cls.supported_tokens_two_char:
            token, method = cls.supported_tokens[token_value[:2]]
            value = token_value[2:]
            return method, token, value

    @classmethod
    def apply_filters_to_query(cls, filters, query):
        parsed_filters = cls.parse_filters(filters)

        if 'filter' in parsed_filters:
            query = query.filter(**parsed_filters['filter'])

        if 'exclude' in parsed_filters:
            query = query.exclude(**parsed_filters['exclude'])

        return query

        # @TODO Applying query filters needs to be refactored to use Q instead and be able to handle logic for OR, AND sequences.
        # def apply_filters_to_query(cls, filters, model):
        #     parsed_filters = cls.parse_filters(filters)
        #
        #     query = Q()
        #
        #     if 'filter' in parsed_filters:
        #         query.add(Q(**parsed_filters['filter']), Q.AND)
        #
        #     if 'exclude' in parsed_filters:
        #         query.add(~Q(**parsed_filters['exclude']), Q.AND)
        #
        #     if 'OR' in parsed_filters:
        #         sub_filters = parsed_filters['OR']
        #
        #         if 'filter' in sub_filters:
        #             query.add(Q(**sub_filters['filter']), Q.OR)
        #
        #         if 'exclude' in sub_filters:
        #             query.add(Q(**sub_filters['exclude']), Q.OR)
        #
        #     return query


class DjangoRepository:
    def __init__(self, model):
        self.model = None
        self.filters = {}
        self.includes = []
        self.set_model(model)

    def set_model(self, model):
        self.model = model
        return self

    def set_filters(self, filters):
        self.filters = filters
        return self

    def set_includes(self, includes):
        if isinstance(includes, str):
            self.includes = [includes]
        else:
            self.includes = includes
        return self

    def query(self):
        query = self.model.objects
        query = self._modify_query(query)
        return query

    def _modify_query(self, query):
        filters = self.filters
        includes = self.includes

        if filters:
            query = DjangoFiltersFactory.apply_filters_to_query(filters, query)

        # If has relations to include pass to factory.
        if includes:
            query = query.prefetch_related(*DjangoIncludeFactory(self.model).build_prefetch_list(includes))

        return query


        # print(test)
        # for filter in filter_tuple_list:
        #     if filter[1] is '=':
        #         query.filter()
        # print(query.values())
        # APPLY Filters
        # if filters_exist:
        #  # Apply depth restrictions to each filter
        # for (filter, value) in filters:
        #  # Filters deeper than the depth restriction + 1 are not allowed
        #  # Depth restriction is offset by 1 because filters terminate with a column
        #  # i.e. 'users.posts.title' => '=Great Post' but the depth we expect is 'users.posts'
        # if (count(explode(self::GLUE, $filter)) > ($this->getDepthRestriction() + 1)) {
        #                                                                               // Unset the disallowed filter
        # unset($filters[$filter]);
        # }
        # }
        #
        # Filter::applyQueryFilters($query, $filters, $columns, $temp_instance->getTable());
        # }

        # APPLY Group by methods if exists

        # APPLY Aggregate Methods if exists

        # APPLY Sort method if exists

    def _check_relation(self):
        pass

    def all(self):
        return self.query().all()

        # def find(self, id):
        #     return self.query()


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
