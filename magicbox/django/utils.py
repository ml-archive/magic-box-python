def parse_qsl_with_brackets(qs_lists):
    """

    :param qs_lists:
    :return:
    """
    import re
    parsed_params = {}

    for param, values in qs_lists:
        base = param[:param.find('[')]
        nested_params = re.findall(r'\[(.+?)\]', param)
        nested_len = len(nested_params)

        # normalize values into single value if array does not hold multiple values.
        if len(values) is 1:
            values = values[0]

        # If a base var of same name has not already been parsed add it as new dict.
        if base not in parsed_params and nested_len > 0:
            parsed_params[base] = {}

        if nested_len is 0:
            parsed_params[base] = values

        # Set current cursor.
        current = parsed_params[base]
        for index, key in enumerate(nested_params):

            # If the key does not already exist in the currently working param create new dict.
            if key not in current:
                current[key] = {}

            # If the key is the last nested param add the values to it
            if index + 1 is nested_len or nested_len is 0:
                current[key] = values

            # Move current cursor
            current = current[key]

    print(parsed_params)
    return parsed_params
