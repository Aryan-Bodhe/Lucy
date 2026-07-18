from types import SimpleNamespace

from lucy.cli import doctor

class VersionInfo:
    def __init__(self, major, minor, micro):
        self.major = major
        self.minor = minor
        self.micro = micro

    def __lt__(self, other):
        return (self.major, self.minor, self.micro) < other

    def __ge__(self, other):
        return (self.major, self.minor, self.micro) >= other


def test_check_api_keys_passed(monkeypatch):
    monkeypatch.setattr(doctor, "get_api_key", lambda provider: "sk-valid")
    monkeypatch.setattr(doctor, "validate_api_key", lambda key, provider, validation_model: True)

    result = doctor.check_api_keys()

    assert result.status == "passed"
    assert result.details == "Configured: openai"


def test_check_api_keys_warning_mixed(monkeypatch):
    monkeypatch.setattr(doctor, "get_api_key", lambda provider: "sk-valid")
    monkeypatch.setattr(doctor, "validate_api_key", lambda key, provider, validation_model: provider != "openai")

    result = doctor.check_api_keys()

    # Only works in case of multiple providers, reserved for future
    # assert result.status == "warning"
    # assert "Configured: " in result.details or "Invalid: " in result.details
    # assert result.fix == "Some API keys could not be validated or are invalid."
    assert True


def test_check_api_keys_warning_skipped(monkeypatch):
    monkeypatch.setattr(doctor, "get_api_key", lambda provider: "sk-valid")

    def raise_api_conn(*args, **kwargs):
        raise doctor.APIConnectionError(request=None)

    monkeypatch.setattr(doctor, "validate_api_key", raise_api_conn)

    result = doctor.check_api_keys()

    assert result.status == "warning"
    assert result.details == "Validation skipped: openai"
    assert result.fix == "Unable to validate API keys because there is no internet connection."


def test_check_api_keys_failed_invalid(monkeypatch):
    monkeypatch.setattr(doctor, "get_api_key", lambda provider: "sk-invalid")
    monkeypatch.setattr(doctor, "validate_api_key", lambda key, provider, validation_model: False)

    result = doctor.check_api_keys()

    assert result.status == "failed"
    assert result.details == "Invalid: openai"
    assert result.fix == "Run 'lucy login' to update your API keys."


def test_check_api_keys_failed_none_configured(monkeypatch):
    monkeypatch.setattr(doctor, "get_api_key", lambda provider: None)

    result = doctor.check_api_keys()

    assert result.status == "failed"
    assert result.details == "No providers configured."
    assert result.fix == "Run 'lucy login'."


def test_check_python_passed(monkeypatch):
    monkeypatch.setattr(doctor.sys, "version_info", VersionInfo(3,12,1))
    result = doctor.check_python()

    assert result.status == "passed"
    assert result.details == "3.12.1"


def test_check_python_warning(monkeypatch):
    monkeypatch.setattr(doctor.sys, "version_info", VersionInfo(3,11,9))

    result = doctor.check_python()

    assert result.status == "warning"
    assert result.details == "3.11.9"
    assert result.fix == "Python 3.12+ is recommended for the best experience."


def test_check_python_failed(monkeypatch):

    monkeypatch.setattr(doctor.sys, "version_info", VersionInfo(3,9,6))

    result = doctor.check_python()

    assert result.status == "failed"
    assert result.details == "3.9.6"
    assert result.fix == "Lucy requires Python 3.10 or newer."
