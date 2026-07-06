import sys
from pydantic import BaseModel, model_validator, field_validator, ValidationError
from typing import Any


def extract_config(path: str) -> dict[str, Any]:
    raw: dict[str, str] = {}
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ValueError(f"Invalid syntax at line: {line}")
                key, value = line.split("=", 1)
                raw[key.strip()] = value.strip()
        return raw
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")


class MazeConfig(BaseModel):
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool = True

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_coordinates(cls, value: str) -> tuple[int, int]:
        x_str, y_str = value.split(",")
        return (int(x_str), int(y_str)) 

    @field_validator("width", "height")
    @classmethod
    def must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Width and height must be positive")
        return value

    @classmethod
    def from_file(cls, path: str) -> "MazeConfig":
        raw = extract_config(path)
        raw_lower = {k.lower(): v for k, v in raw.items()}
        return cls(**raw_lower)

    @model_validator(mode="after")
    def check_entry_exit(self) -> "MazeConfig":
        if self.entry == self.exit:
            raise ValueError("Entry and exit must be different")
        x, y = self.entry
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Entry is outside the maze")
        x, y = self.exit
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Exit is outside the maze")
        return self


def load_config(path: str) -> MazeConfig:
    try:
        return MazeConfig.from_file(path)
    except FileNotFoundError as e:
        print(f"Error {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: Invalid configuration syntax: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid configuration syntax: {e}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)

    config = load_config(sys.argv[1])
    print(config)


if __name__ == "__main__":
    main()
