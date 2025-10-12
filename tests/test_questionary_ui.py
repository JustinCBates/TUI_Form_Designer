"""Tests for QuestionaryUI functionality."""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

from tui_form_designer.ui.questionary_ui import QuestionaryUI


class TestQuestionaryUI:
    """Test suite for QuestionaryUI."""
    
    def test_init_default_theme(self):
        """Test QuestionaryUI initialization with default theme."""
        ui = QuestionaryUI()
        assert ui.style is not None
    
    def test_init_custom_theme(self):
        """Test QuestionaryUI initialization with custom themes."""
        # Test dark theme
        ui = QuestionaryUI(theme="dark")
        assert ui.style is not None
        
        # Test minimal theme
        ui = QuestionaryUI(theme="minimal")
        assert ui.style is not None
    
    def test_get_theme_style(self):
        """Test theme style retrieval."""
        ui = QuestionaryUI()
        
        # Test all theme types
        default_style = ui._get_theme_style("default")
        dark_style = ui._get_theme_style("dark")
        minimal_style = ui._get_theme_style("minimal")
        
        assert default_style is not None
        assert dark_style is not None
        assert minimal_style is not None
        
        # Test unknown theme falls back to default
        unknown_style = ui._get_theme_style("unknown")
        assert unknown_style == default_style
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_show_title(self, mock_print):
        """Test showing title."""
        ui = QuestionaryUI()
        ui.show_title("Test Title", "🚀")
        
        assert mock_print.call_count == 2
        # First call should be the title with icon
        mock_print.assert_any_call("\\n🚀 Test Title", style="bold blue")
        # Second call should be the separator
        mock_print.assert_any_call("============", style="blue")
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_show_phase_header(self, mock_print):
        """Test showing phase header."""
        ui = QuestionaryUI()
        ui.show_phase_header("Phase 1", "Description", "📋")
        
        assert mock_print.call_count == 3
        mock_print.assert_any_call("\\n📋 Phase 1", style="bold green")
        mock_print.assert_any_call("   Description", style="italic")
        mock_print.assert_any_call("-" * 50, style="dim")
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_show_section_header(self, mock_print):
        """Test showing section header."""
        ui = QuestionaryUI()
        ui.show_section_header("Section", "🔧")
        
        mock_print.assert_called_once_with("\\n🔧 Section", style="bold yellow")
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_show_messages(self, mock_print):
        """Test showing different message types."""
        ui = QuestionaryUI()
        
        ui.show_success("Success message")
        mock_print.assert_called_with("✅ Success message", style="bold green")
        
        ui.show_error("Error message")
        mock_print.assert_called_with("❌ Error message", style="bold red")
        
        ui.show_warning("Warning message")
        mock_print.assert_called_with("⚠️ Warning message", style="bold yellow")
        
        ui.show_info("Info message")
        mock_print.assert_called_with("ℹ️ Info message", style="bold")
        
        ui.show_step("Step message")
        mock_print.assert_called_with("   → Step message", style="dim")
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_show_progress(self, mock_print):
        """Test showing progress indicator."""
        ui = QuestionaryUI()
        ui.show_progress(3, 10, "Processing")
        
        # Should show progress bar with percentage
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "[" in call_args and "]" in call_args
        assert "30%" in call_args
        assert "(3/10)" in call_args
        assert "Processing" in call_args
    
    @patch('questionary.confirm')
    def test_confirm(self, mock_confirm):
        """Test confirmation prompt."""
        ui = QuestionaryUI()
        mock_confirm.return_value.ask.return_value = True
        
        result = ui.confirm("Continue?", default=True)
        
        assert result is True
        mock_confirm.assert_called_once_with("Continue?", default=True, style=ui.style)
    
    @patch('questionary.confirm')
    def test_confirm_keyboard_interrupt(self, mock_confirm):
        """Test confirmation prompt with keyboard interrupt."""
        ui = QuestionaryUI()
        mock_confirm.return_value.ask.side_effect = KeyboardInterrupt()
        
        with patch.object(ui, 'show_error') as mock_error:
            result = ui.confirm("Continue?")
            assert result is False
            mock_error.assert_called_once_with("Operation cancelled by user")
    
    @patch('tui_form_designer.ui.questionary_ui.text')
    def test_prompt(self, mock_text):
        """Test text prompt."""
        ui = QuestionaryUI()
        mock_text.return_value.ask.return_value = "test input"
        
        result = ui.prompt("Enter text:", default="default", allow_empty=True)
        
        assert result == "test input"
        mock_text.assert_called_once_with(
            "Enter text:", 
            default="default", 
            style=ui.style,
            validate=None
        )
    
    @patch('tui_form_designer.ui.questionary_ui.text')
    def test_prompt_empty_not_allowed(self, mock_text):
        """Test text prompt with empty input not allowed."""
        ui = QuestionaryUI()
        # First call returns empty, second returns valid input
        mock_text.return_value.ask.side_effect = ["", "valid input"]
        
        with patch.object(ui, 'show_error') as mock_error:
            result = ui.prompt("Enter text:", allow_empty=False)
            
            assert result == "valid input"
            mock_error.assert_called_once_with("This field is required")
    
    @patch('tui_form_designer.ui.questionary_ui.text')
    def test_prompt_int(self, mock_text):
        """Test integer prompt."""
        ui = QuestionaryUI()
        mock_text.return_value.ask.return_value = "42"
        
        result = ui.prompt_int("Enter number:", default=10, min_value=1, max_value=100)
        
        assert result == 42
    
    @patch('tui_form_designer.ui.questionary_ui.text')
    def test_prompt_int_invalid_then_valid(self, mock_text):
        """Test integer prompt with invalid then valid input."""
        ui = QuestionaryUI()
        mock_text.return_value.ask.side_effect = ["invalid", "42"]
        
        with patch.object(ui, 'show_error') as mock_error:
            result = ui.prompt_int("Enter number:")
            
            assert result == 42
            mock_error.assert_called_with("Please enter a valid number")
    
    @patch('tui_form_designer.ui.questionary_ui.text')
    def test_prompt_int_out_of_range(self, mock_text):
        """Test integer prompt with out of range values."""
        ui = QuestionaryUI()
        mock_text.return_value.ask.side_effect = ["0", "101", "50"]
        
        with patch.object(ui, 'show_error') as mock_error:
            result = ui.prompt_int("Enter number:", min_value=1, max_value=100)
            
            assert result == 50
            assert mock_error.call_count == 2
            mock_error.assert_any_call("Value must be at least 1")
            mock_error.assert_any_call("Value must be at most 100")
    
    @patch('questionary.password')
    def test_prompt_password(self, mock_password):
        """Test password prompt."""
        ui = QuestionaryUI()
        mock_password.return_value.ask.return_value = "secret123"
        
        result = ui.prompt_password("Enter password:")
        
        assert result == "secret123"
        mock_password.assert_called_once_with(
            "Enter password::", 
            style=ui.style,
            validate=None
        )
    
    @patch('questionary.password')
    def test_prompt_password_empty_retry(self, mock_password):
        """Test password prompt with empty input retry."""
        ui = QuestionaryUI()
        mock_password.return_value.ask.side_effect = ["", "secret123"]
        
        with patch.object(ui, 'show_error') as mock_error:
            result = ui.prompt_password("Enter password:")
            
            assert result == "secret123"
            mock_error.assert_called_once_with("Password cannot be empty")
    
    @patch('tui_form_designer.ui.questionary_ui.select')
    def test_select(self, mock_select):
        """Test select prompt."""
        ui = QuestionaryUI()
        mock_select.return_value.ask.return_value = "Option 2"
        
        choices = ["Option 1", "Option 2", "Option 3"]
        result = ui.select("Choose option:", choices, default="Option 1")
        
        assert result == "Option 2"
        mock_select.assert_called_once_with(
            "Choose option:",
            choices=choices,
            default="Option 1",
            style=ui.style
        )
    
    @patch('tui_form_designer.ui.questionary_ui.select')
    def test_select_with_dict_choices(self, mock_select):
        """Test select prompt with dictionary choices."""
        ui = QuestionaryUI()
        mock_select.return_value.ask.return_value = "Choice 1"
        
        choices = [{"name": "Choice 1", "value": "val1"}, {"name": "Choice 2", "value": "val2"}]
        result = ui.select("Choose option:", choices)
        
        assert result == "Choice 1"
        # Should extract names from dict choices
        expected_choices = ["Choice 1", "Choice 2"]
        mock_select.assert_called_once_with(
            "Choose option:",
            choices=expected_choices,
            default=None,
            style=ui.style
        )
    
    def test_select_empty_choices(self):
        """Test select prompt with empty choices list."""
        ui = QuestionaryUI()
        
        with pytest.raises(ValueError, match="Choices list cannot be empty"):
            ui.select("Choose option:", [])
    
    @patch('questionary.checkbox')
    def test_multiselect(self, mock_checkbox):
        """Test multiselect prompt."""
        ui = QuestionaryUI()
        mock_checkbox.return_value.ask.return_value = ["Option 1", "Option 3"]
        
        choices = ["Option 1", "Option 2", "Option 3"]
        result = ui.multiselect("Choose options:", choices)
        
        assert result == ["Option 1", "Option 3"]
        mock_checkbox.assert_called_once_with(
            "Choose options:",
            choices=choices,
            style=ui.style
        )
    
    @patch('questionary.press_any_key_to_continue')
    def test_pause(self, mock_pause):
        """Test pause functionality."""
        ui = QuestionaryUI()
        ui.pause("Press any key...")
        
        mock_pause.assert_called_once_with("Press any key...")
    
    @patch('tui_form_designer.ui.questionary_ui.form')
    def test_form(self, mock_form):
        """Test form functionality."""
        ui = QuestionaryUI()
        mock_form.return_value.ask.return_value = {"name": "John", "age": 30}
        
        questions = [
            {"name": "name", "type": "text", "message": "Name:"},
            {"name": "age", "type": "text", "message": "Age:"}
        ]
        
        result = ui.form(questions)
        
        assert result == {"name": "John", "age": 30}
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_table(self, mock_print):
        """Test table display."""
        ui = QuestionaryUI()
        
        data = [
            {"name": "John", "age": 30, "city": "NYC"},
            {"name": "Jane", "age": 25, "city": "LA"}
        ]
        headers = ["name", "age", "city"]
        
        ui.table(data, headers)
        
        # Should print header and data rows
        assert mock_print.call_count >= 3  # Header, separator, data rows
    
    @patch('tui_form_designer.ui.questionary_ui.qprint')
    def test_table_empty_data(self, mock_print):
        """Test table display with empty data."""
        ui = QuestionaryUI()
        ui.table([], ["name", "age"])
        
        mock_print.assert_called_once_with("ℹ️ No data to display", style="bold")
    
    @patch('os.system')
    def test_clear_screen(self, mock_system):
        """Test screen clearing."""
        ui = QuestionaryUI()
        ui.clear_screen()
        
        mock_system.assert_called_once_with('clear')