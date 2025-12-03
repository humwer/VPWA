import importlib
import yaml


def read_profile():
    file = open("profile.yaml", "r")
    profile = yaml.safe_load(file)


def load_validation_registration_module(profile_value):
    module_path = f"modules.validate_registration.{profile_value}.impl"
    module = importlib.import_module(module_path)
    return module.validate_registration
