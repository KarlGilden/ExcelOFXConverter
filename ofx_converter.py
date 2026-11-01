"""Application entry point: select and connect the service and UI adapter."""

from pathlib import Path

from application.converter import ConverterPresenter
from services.excel_ofx_converter import ExcelOFXConverter
from ui.tkinter_view import TkinterConverterView


def main():
    view = TkinterConverterView()
    presenter = ConverterPresenter(
        view=view,
        service=ExcelOFXConverter(),
        log_file=Path.home() / "anz_ofx_error.log",
    )
    view.run()


if __name__ == "__main__":
    main()
