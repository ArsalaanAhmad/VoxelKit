from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace


FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FakeStreamlit:
    def __init__(self, *, source: str, path_text: str, preview_clicked: bool = False) -> None:
        self._source = source
        self._path_text = path_text
        self._preview_clicked = preview_clicked
        self.calls: list[tuple[str, object]] = []

    def set_page_config(self, **kwargs) -> None:
        self.calls.append(("set_page_config", kwargs))

    def title(self, value: str) -> None:
        self.calls.append(("title", value))

    def caption(self, value: str) -> None:
        self.calls.append(("caption", value))

    def radio(self, label: str, options, horizontal: bool = False) -> str:
        self.calls.append(("radio", label))
        return self._source

    def file_uploader(self, *args, **kwargs):
        self.calls.append(("file_uploader", args[0]))
        return None

    def text_input(self, label: str, value: str = "") -> str:
        self.calls.append(("text_input", label))
        return self._path_text

    def info(self, value: str) -> None:
        self.calls.append(("info", value))

    def write(self, value: str) -> None:
        self.calls.append(("write", value))

    def subheader(self, value: str) -> None:
        self.calls.append(("subheader", value))

    def json(self, value) -> None:
        self.calls.append(("json", value))

    def error(self, value: str) -> None:
        self.calls.append(("error", value))

    def selectbox(self, label: str, options, index: int = 0):
        self.calls.append(("selectbox", label))
        return options[index]

    def checkbox(self, label: str, value: bool = False, key: str | None = None) -> bool:
        self.calls.append(("checkbox", label))
        return True

    def number_input(self, label: str, min_value: int = 0, value: int = 0, step: int = 1, key: str | None = None) -> int:
        self.calls.append(("number_input", label))
        return value

    def button(self, label: str, key: str | None = None) -> bool:
        self.calls.append(("button", label))
        return self._preview_clicked

    def image(self, value, caption: str | None = None, use_container_width: bool = False) -> None:
        self.calls.append(("image", caption))


def _load_app_module(monkeypatch):
    monkeypatch.setitem(sys.modules, "streamlit", ModuleType("streamlit"))
    module = importlib.import_module("voxelkit.gui.app")
    return importlib.reload(module)


def test_save_uploaded_file_preserves_nii_gz_suffix(monkeypatch) -> None:
    app = _load_app_module(monkeypatch)
    uploaded = SimpleNamespace(name="sample.nii.gz", getbuffer=lambda: b"abc123")

    saved_path = Path(app._save_uploaded_file(uploaded))
    try:
        assert saved_path.suffixes[-2:] == [".nii", ".gz"]
        assert saved_path.read_bytes() == b"abc123"
    finally:
        saved_path.unlink(missing_ok=True)


def test_render_app_smoke_for_local_nifti(monkeypatch) -> None:
    app = _load_app_module(monkeypatch)
    fake_streamlit = FakeStreamlit(
        source="Local file path",
        path_text=str(FIXTURES_DIR / "sample_3d.nii.gz"),
    )
    observed_paths: list[tuple[str, str]] = []

    monkeypatch.setattr(app, "st", fake_streamlit)
    monkeypatch.setattr(
        app,
        "inspect_file",
        lambda file_path: observed_paths.append(("inspect", file_path)) or {"items": []},
    )
    monkeypatch.setattr(
        app,
        "report_file",
        lambda file_path: observed_paths.append(("report", file_path)) or {"warnings": []},
    )

    app.render_app()

    assert observed_paths == [
        ("inspect", str(FIXTURES_DIR / "sample_3d.nii.gz")),
        ("report", str(FIXTURES_DIR / "sample_3d.nii.gz")),
    ]
    assert ("title", "VoxelKit Optional Local GUI") in fake_streamlit.calls
    assert ("json", {"items": []}) in fake_streamlit.calls
    assert ("json", {"warnings": []}) in fake_streamlit.calls
    assert ("button", "Generate preview") in fake_streamlit.calls