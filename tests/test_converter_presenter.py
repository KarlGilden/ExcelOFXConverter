from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from application.converter import ConverterPresenter, ConverterService, ConverterView


class ConverterPresenterTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.log_file = Path(self.directory.name) / "error.log"
        self.view = Mock(spec=ConverterView)
        self.service = Mock(spec=ConverterService)
        self.presenter = ConverterPresenter(self.view, self.service, self.log_file)
        self.select_action, self.convert_action = self.view.bind_actions.call_args.args

    def test_conversion_requires_selection(self):
        self.convert_action()
        self.service.convert_file.assert_not_called()
        self.view.show_warning.assert_called_once_with(
            "No File Selected", "Please select an Excel file first."
        )

    def test_selected_file_is_converted_and_result_displayed(self):
        self.view.choose_excel_file.return_value = "rent.xlsx"
        self.service.convert_file.return_value = (Path("rent.ofx"), 2)
        self.select_action()
        self.convert_action()
        self.view.show_selected_file.assert_called_once_with("rent.xlsx")
        self.service.convert_file.assert_called_once_with("rent.xlsx")
        self.view.show_info.assert_called_once_with(
            "Conversion Successful",
            "Transactions Imported: 2\n\nOFX File Created:\n\nrent.ofx",
        )

    def test_cancelling_selection_keeps_previous_file(self):
        self.view.choose_excel_file.side_effect = ["rent.xlsx", ""]
        self.select_action()
        self.select_action()
        self.assertEqual(self.presenter.selected_file, "rent.xlsx")
        self.view.show_selected_file.assert_called_once_with("rent.xlsx")

    def test_conversion_error_is_logged_and_displayed(self):
        self.view.choose_excel_file.return_value = "rent.xlsx"
        self.service.convert_file.side_effect = ValueError("Invalid spreadsheet")
        self.select_action()
        self.convert_action()
        self.view.show_error.assert_called_once_with(
            "Conversion Error", "Invalid spreadsheet"
        )
        self.assertIn("ValueError: Invalid spreadsheet", self.log_file.read_text())
        self.view.show_info.assert_not_called()

    def test_startup_connects_view_and_service_then_runs_view(self):
        import ofx_converter

        with patch.object(ofx_converter, "TkinterConverterView") as view_factory, \
                patch.object(ofx_converter, "ExcelOFXConverter") as service_factory:
            ofx_converter.main()
            view = view_factory.return_value
            view.run.assert_called_once_with()
            select_action, convert_action = view.bind_actions.call_args.args
            view.choose_excel_file.return_value = "rent.xlsx"
            service_factory.return_value.convert_file.return_value = (Path("rent.ofx"), 1)
            select_action()
            convert_action()
            service_factory.return_value.convert_file.assert_called_once_with("rent.xlsx")


if __name__ == "__main__":
    unittest.main()
