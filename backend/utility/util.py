

def get_key(key: str) -> str:
    """
    Get the value of an environment variable.

    Args:
        key (str): The name of the environment variable.

    Returns:
        str: The value of the environment variable.

    Raises:
        KeyError: If the environment variable is not found.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv(key)
    if not api_key:
        raise KeyError(f"Environment variable '{key}' not found.")
    else:
        print(f"env")
    return api_key





