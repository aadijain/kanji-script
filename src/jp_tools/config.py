"""Application settings via pydantic-settings.

Defaults are overridable by environment variables (prefix ``JP_TOOLS_``) or a
local ``.env`` file. CLI flags, where present, take precedence over these.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from jp_tools.core.freq import DEFAULT_FREQ_DICT


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="JP_TOOLS_", env_file=".env", extra="ignore"
    )

    input_dir: Path = Path("input")
    output_dir: Path = Path("output")
    output: str = "kanji"  # output filename stem (timestamp appended)
    freq_dict: Path = DEFAULT_FREQ_DICT
