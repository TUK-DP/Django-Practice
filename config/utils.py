import inflection

def transfer_camel_case(data):
    if isinstance(data, dict):
        return {inflection.camelize(key, False): transfer_camel_case(value) for key, value in data.items()}
    else:
        return data
