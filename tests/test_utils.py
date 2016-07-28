from django.http.request import QueryDict
from magicbox.utils import parse_qsl_with_brackets


class TestParsesQueryStringListWithBrackets:
    def assertEqual(self, valone, valtwo):
        assert valone == valtwo

    def test_can_parse_single_query_string(self):
        qs = 'filters[name]==kirill'
        query_list = QueryDict(qs, encoding='utf-8').lists()
        parsed_qsl = parse_qsl_with_brackets(query_list)
        self.assertEqual(parsed_qsl, {
            'filters': {'name': '=kirill'}
        })

    def test_can_parse_multiple_query_strings(self):
        qs = 'filters[name]==kirill&filters[status]==active'
        query_list = QueryDict(qs, encoding='utf-8').lists()
        parsed_qsl = parse_qsl_with_brackets(query_list)
        self.assertEqual(parsed_qsl, {
            'filters': {
                'name': '=kirill',
                'status': '=active'
            }
        })

    def test_can_parse_nested_query_string(self):
        qs = 'filters[name]==kirill&filters[status]==active&filters[or][status]==superactive'
        query_list = QueryDict(qs, encoding='utf-8').lists()
        parsed_qsl = parse_qsl_with_brackets(query_list)
        self.assertEqual(parsed_qsl, {
            'filters': {
                'name': '=kirill',
                'status': '=active',
                'or': {
                    'status': '=superactive'
                }
            }
        })

    def test_can_correctly_parse_when_values_have_brackets(self):
        qs = 'filters[name]=[kirill,simon,joe,moe]'
        query_list = QueryDict(qs, encoding='utf-8').lists()
        parsed_qsl = parse_qsl_with_brackets(query_list)
        self.assertEqual(parsed_qsl, {
            'filters': {
                'name': '[kirill,simon,joe,moe]',
            }
        })