import inflection

def transfer_dict_key_to_camel_case(obj: dict):
    return {
        inflection.camelize(key, False):
            (
                value if not isinstance(value, dict) else
                transfer_dict_key_to_camel_case(value)
            )
        for key, value in obj.items()
    }