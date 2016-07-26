class FiltersFactory:
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
        parsed_filters = {}

        for column, token_value_string in filters.items():
            method, token, value = cls.determine_filter_token_and_value(token_value_string)

            if method not in parsed_filters:
                parsed_filters[method] = {}

            parsed_filters[method][column + token] = value

        return parsed_filters

    @classmethod
    def determine_filter_token_and_value(cls, query_value):

        if query_value[0] in cls.supported_tokens_one_char:
            token, method = cls.supported_tokens[query_value[0]]
            value = query_value[1:]
            return method, token, value

        if query_value[:2] in cls.supported_tokens_two_char:
            token, method = cls.supported_tokens[query_value[:2]]
            value = query_value[2:]
            return method, token, value

    @classmethod
    def apply_filters_to_query(cls, filters, query):
        parsed_filters = cls.parse_filters(filters)

        if 'filter' in parsed_filters:
            query = query.filter(**parsed_filters['filter'])

        if 'exclude' in parsed_filters:
            query = query.exclude(**parsed_filters['exclude'])

        return query


class DjangoRepository:
    def __init__(self, model):
        self.model = None
        self.filters = {}
        self.set_model(model)

    def set_model(self, model):
        self.model = model
        return self

    def set_filters(self, filters):
        self.filters = filters
        return self

    def query(self):
        query = self.model.objects
        query = self._modify_query(query)
        return query

    def _modify_query(self, query):
        filters = self.filters

        if filters:
            query = FiltersFactory.apply_filters_to_query(filters, query)

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

    def all(self):
        return self.query().all().values()

        # def find(self, id):
        #     return self.query()
