from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Retrieves the value from the dictionary for the given key.

    Args:
        dictionary (dict): The dictionary from which to retrieve the value.
        key (str): The key whose value needs to be retrieved.

    Returns:
        The value associated with the provided key in the dictionary.
        Returns None if the key does not exist.
    """
    # Safely get the value from the dictionary using the provided key
    return dictionary.get(key)
