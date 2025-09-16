import os
from pathlib import Path
from typing import Any, cast

import yaml
from dotenv import load_dotenv

# Global variable to cache the loaded configuration
_config: dict[str, Any] | None = None
_config_path = Path(__file__).parent.parent.parent / "configs"


def _load_config_from_yaml(file_path: Path) -> dict[str, Any]:
    """Loads a YAML file and returns its content."""
    try:
        with open(file_path) as f:
            return cast(dict[str, Any], yaml.safe_load(f))
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at {file_path}. Skipping.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}")
        raise


def _override_with_env_variables(config: dict[str, Any], prefix: str = "") -> None:
    """Recursively overrides config with environment variables."""
    for key, value in config.items():
        env_var_name = f"{prefix}{key}".upper()
        if isinstance(value, dict):
            _override_with_env_variables(value, f"{env_var_name}_")
        else:
            env_value = os.getenv(env_var_name)
            if env_value is not None:
                # Attempt to cast env_value to the type of the original value
                try:
                    original_type = type(value)
                    if original_type == bool:
                        config[key] = env_value.lower() in ("true", "1", "t")
                    else:
                        config[key] = original_type(env_value)
                except (ValueError, TypeError):
                    config[key] = env_value  # Fallback to string


def get_config() -> dict[str, Any]:
    """
    Loads, merges, and caches the project configuration.

    The loading process is as follows:
    1. Loads the main `config.yaml`.
    2. Loads the `logging_config.yaml` and merges it under a 'logging' key.
    3. Loads environment variables from a `.env` file (if it exists).
    4. Overrides any configuration with corresponding environment variables.
    5. Resolves log file paths to be absolute and configures logging.

    Returns:
        A dictionary containing the fully merged and overridden configuration.
    """
    global _config
    if _config is not None:
        return _config

    # Load environment variables from .env file
    load_dotenv()

    # 1. Load base configuration
    base_config_path = _config_path / "config.yaml"
    config = _load_config_from_yaml(base_config_path)

    # 2. Load and merge logging configuration
    logging_config_path = _config_path / "logging_config.yaml"
    logging_config = _load_config_from_yaml(logging_config_path)
    if logging_config:
        config["logging_config"] = logging_config

    # 3. Override with environment variables
    _override_with_env_variables(config)

    # 4. Resolve log file paths
    if "logging_config" in config:
        log_config = config["logging_config"]
        project_root = Path(__file__).resolve().parent.parent.parent
        for handler in log_config.get("handlers", {}).values():
            if "filename" in handler:
                handler["filename"] = str(project_root / handler["filename"])

    # Cache the configuration
    _config = config
    return _config


# Example of how to use it:
if __name__ == "__main__":
    # This block will only run when the script is executed directly
    # It's useful for testing the configuration loading logic
    config = get_config()
    import pprint

    pprint.pprint(config)
