"""View contracts and presentation logic for Excel-to-OFX conversion."""

from pathlib import Path
import traceback
from typing import Callable, Protocol, Tuple


class ConverterService(Protocol):
    def convert_file(self, excel_file: str) -> Tuple[Path, int]:
        ...


class ConverterView(Protocol):
    def bind_actions(
        self, select_file: Callable[[], None], convert_file: Callable[[], None]
    ) -> None:
        ...

    def choose_excel_file(self) -> str:
        ...

    def show_selected_file(self, filename: str) -> None:
        ...

    def show_warning(self, title: str, message: str) -> None:
        ...

    def show_info(self, title: str, message: str) -> None:
        ...

    def show_error(self, title: str, message: str) -> None:
        ...

    def run(self) -> None:
        ...


class ConverterPresenter:
    """Coordinate a view and conversion service through injected interfaces."""

    def __init__(
        self,
        view: ConverterView,
        service: ConverterService,
        log_file: Path,
    ) -> None:
        self.view = view
        self.service = service
        self.log_file = log_file
        self.selected_file = None
        self.view.bind_actions(self.select_file, self.convert_file)

    def select_file(self) -> None:
        filename = self.view.choose_excel_file()
        if filename:
            self.selected_file = filename
            self.view.show_selected_file(filename)

    def convert_file(self) -> None:
        try:
            if not self.selected_file:
                self.view.show_warning(
                    "No File Selected",
                    "Please select an Excel file first.",
                )
                return
            output_file, count = self.service.convert_file(self.selected_file)
            self.view.show_info(
                "Conversion Successful",
                f"Transactions Imported: {count}\n\n"
                f"OFX File Created:\n\n"
                f"{output_file}",
            )
        except Exception as ex:
            with open(self.log_file, "w", encoding="utf-8") as file:
                file.write(traceback.format_exc())
            self.view.show_error("Conversion Error", str(ex))
