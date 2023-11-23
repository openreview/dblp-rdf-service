import typing as t
from typing import Optional, cast
import os
import json

from marshmallow import Schema, fields, post_load
from dataclasses import dataclass

from dblp_service.lib.log import create_logger

from .schemas import StrField

log = create_logger(__file__)

@dataclass
class OpenReviewConfig:
    restApi: str
    restUser: str
    restPassword: str


class OpenReviewSchema(Schema):
    restApi = StrField
    restUser = StrField
    restPassword = StrField

    @post_load
    def make(self, data: t.Any, **_) -> OpenReviewConfig:
        return OpenReviewConfig(**data)


@dataclass
class ApacheJenaConfig:
    dbLocation: str


class ApacheJenaConfigSchema(Schema):
    connectionUrl = StrField
    dbLocation = StrField

    @post_load
    def make(self, data: t.Any, **_) -> ApacheJenaConfig:
        return ApacheJenaConfig(**data)

@dataclass
class Config:
    openreview: OpenReviewConfig
    jena: ApacheJenaConfig
    dblpServiceRoot: str


class ConfigSchema(Schema):
    openreview = fields.Nested(OpenReviewSchema)
    jena = fields.Nested(ApacheJenaConfigSchema)
    dblpServiceRoot = StrField

    @post_load
    def make(self, data: t.Any, **_) -> Config:
        return Config(**data)


def setenv(env: str):
    os.environ["env"] = env


def getenv():
    return os.environ["env"]


def read_config(config_path: str) -> t.Optional[Config]:
    config: t.Optional[Config] = None
    if os.path.exists(config_path):
        log.debug(f"Loading config '{config_path}'")
        with open(config_path) as f:
            jsonContent = json.load(f)
            loaded: Config = cast(Config, ConfigSchema().load(jsonContent))
            config = loaded

    return config


def load_config() -> t.Optional[Config]:
    config: t.Optional[Config] = None
    env = getenv()
    if "config" in os.environ:
        maybeConfig = os.environ["config"]
        config = read_config(maybeConfig)
        if config is not None:
            return config

    config_filename = f"config-{env}.json"
    workingdir = os.path.abspath(os.curdir)
    config_path = os.path.join(workingdir, config_filename)
    while workingdir != "/":
        log.debug(f"Looking for config '{config_filename}' in {workingdir}")
        config_path = os.path.join(workingdir, config_filename)

        config = read_config(config_path)
        if config is not None:
            return config
        workingdir = os.path.abspath(os.path.join(workingdir, os.pardir))
    else:
        log.warn(f"Could not find config {config_filename}")

    return config


global_app_config: Optional[Config] = None


def get_config() -> Config:
    global global_app_config
    if global_app_config is None:
        global_app_config = load_config()
    if global_app_config is None:
        raise Exception("Config file could not be loaded")

    return global_app_config
