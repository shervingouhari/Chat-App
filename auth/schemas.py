from pydantic import BaseModel, Field, SecretStr, ConfigDict, model_validator


class AuthLogin(BaseModel):
    username: str = Field(
        ...,
        mix_length=8,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
    password: SecretStr = Field(..., min_length=8, max_length=20)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode='before')
    def no_spaces(cls, items):
        for value in items.values():
            if isinstance(value, str) and ' ' in value:
                raise ValueError('Fields must not contain spaces.')
        return items

    def model_dump(self, *args, **kwargs):
        dump = super().model_dump(*args, **kwargs)
        dump["password"] = self.password.get_secret_value()
        return dump
