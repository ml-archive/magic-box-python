import json
from functools import wraps

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from magicbox.magicbox.django.factories import DjangoIncludeFactory, DjangoSorterFactory, DjangoAggregatorFactory, \
    DjangoLimiterFactory
from magicbox.magicbox.utils import parse_qsl_with_brackets


def resource(model):
    """
    The resource decorator builds a repository for the model based on inbound request data.

    :param model: A Django model
    :return:
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Parse query params that include brackets
            query_params = parse_qsl_with_brackets(request.GET.lists())

            # If Django Rest Framework is being used we will use the already parsed data attribute.
            # but if not we will try to parse the data our selves from the body.
            body = getattr(request, 'data', None)
            if body is None and request.body and (request.method == 'POST' or request.method == 'PUT'):
                # @TODO we shouldn't just blindly think it's json data. We should be checking the Content-Type header.
                body = json.loads(request.body.decode(getattr(settings, 'DEFAULT_CHARSET', 'utf-8')))

            # Setup the DjangoRepository instance to pass into the view function.
            filters = query_params.get(getattr(settings, 'MAGIC_BOX_FILTERS_PARAM', 'filters'))
            include = query_params.get(getattr(settings, 'MAGIC_BOX_INCLUDE_PARAM', 'include'))
            aggregate = query_params.get(getattr(settings, 'MAGIC_BOX_AGGREGATE_PARAM', 'aggregate'))
            sort = query_params.get(getattr(settings, 'MAGIC_BOX_SORT_PARAM', 'sort'))

            repository = DjangoRepository(model) \
                .set_input(body) \
                .set_filters(filters) \
                .set_includes(include) \
                .set_aggregate(aggregate) \
                .set_sort_order(sort)

            return view_func(request, repository=repository, *args, **kwargs)

        return _wrapped_view

    return decorator


class DjangoRepository:
    """
    Some TODOs:
    Depth Restriction for limiter statements and includes...
    Convert Setters/Getters to whatever is the "pythonic way"
    """

    def __init__(self, model):
        self.model = model
        self.filters = {}
        self.includes = []
        self.query_set = None
        self.input = {}
        self.fillable = []
        self.aggregate = {}
        self.sort_order = {}

    def set_sort_order(self, sort_order):
        self.sort_order = sort_order
        return self

    def set_aggregate(self, aggregate):
        self.aggregate = aggregate
        return self

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
        aggregate = self.aggregate
        sort_orders = self.sort_order

        query_set = self.model.objects.get_queryset()

        if filters:
            query_set = DjangoLimiterFactory(query_set).construct_query_set(filters)

        # If has relations to include pass to factory.
        if includes:
            # @TODO right now this passes back a list for the prefetch object. LimiterFactory and IncludeFactory should work the same way for consistency sake.
            query_set = query_set.prefetch_related(*DjangoIncludeFactory(self.model).build_prefetch_list(includes))

        # APPLY Group by methods if exists

        # APPLY Aggregate Methods if exists
        if aggregate:
            aggregation = DjangoAggregatorFactory(self.model).construct_aggregator(aggregate)
            if aggregation:
                query_set = query_set.annotate(aggregation)

        # APPLY Sort method if exists
        if sort_orders:
            query_set = query_set.order_by(*DjangoSorterFactory(query_set).construct_order_by(sort_orders))

        print(query_set.query)  # @TODO temp, debugging...
        return query_set

    def all(self):
        return self.query().all()

    def save(self):
        pass

    def update(self):
        pass

    def _has_field(self, field):
        try:
            self.model._meta.get_field(field)
            return True
        except FieldDoesNotExist:
            return False

    def fill(self, instance):
        for field, value in self.input.items():
            if self._has_field(field):
                setattr(instance, field, value)

        instance.save()

    def create(self):
        instance = self.model()
        self.fill(instance)
        return instance

    # def save(self):
    #     pass

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

    # def execute(self):
    #     # @TODO maybe??
    #     # iterate over all query sets to execute them and return results.
    #     pass

    def _check_relation(self):
        pass
