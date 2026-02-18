import yaml


def read_yaml() -> dict[str, list[str]]:
    with open("config.yml") as file:
        config: dict[str, list[str]] = yaml.safe_load(file)
        if "exclude" in config.keys():
            config["exclude"] = [] if config["exclude"] is None else config["exclude"]
        return config

CONFIG = read_yaml()
