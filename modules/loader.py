import importlib
import yaml


def read_profile():
    file = open("profile.yaml", "r")
    profile = yaml.safe_load(file)
    return profile


def load_validation_registration_module(profile_value):
    module_path = f"modules.validate_registration.{profile_value}.impl"
    module = importlib.import_module(module_path)
    return module.validate_registration


def load_search_posts_module(profile_value):
    module_path = f"modules.search_posts.{profile_value}.impl"
    module = importlib.import_module(module_path)
    return module.search_posts


def load_refresh_token_module(profile_value):
    module_path = f"modules.refresh_token.{profile_value}.impl"
    module = importlib.import_module(module_path)
    return module.refresh_token


def load_get_comments_from_post_module(profile_value):
    module_path = f"modules.get_comments_from_post.{profile_value}.impl"
    module = importlib.import_module(module_path)
    return module.get_comments_from_post
