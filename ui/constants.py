from pathlib import Path

"""
Constants for the UI module.

This module defines constants used throughout the UI, including status messages, table headers, and symbols.

Note: Text symbols like SYMBOL_CHECK and SYMBOL_CROSS are deprecated in favor of icon constants ICON_CHECK, ICON_CROSS, ICON_PLAY for better cross-platform rendering.
"""

# --- Constants ---
SETTINGS_FILENAME = Path("settings.json")
STATUS_READY = "Ready"
STATUS_ANALYZING = "Analyzing..."
MSG_ERROR_PATHS = "Error: Paths 'pdf_dir' and 'wav_dir' must be set in settings.json"
MSG_NO_PAIRS = "No valid PDF-ZIP pairs found."
MSG_DONE = "Analysis completed. Processed {count} pairs."
MSG_ERROR = "Error: {error}"
MSG_SCANNING = "Scanning and pairing files..."
MSG_PROCESSING_PAIR = "Processing pair {current}/{total}: {filename}"
WINDOW_TITLE = "Final Cue Sheet Checker"
BUTTON_RUN_ANALYSIS = "Run analysis"
LABEL_FILTER = "Filter:"
FILTER_ALL = "All"
FILTER_OK = "OK"
FILTER_FAIL = "Fail"
FILTER_WARN = "Warn"
TABLE_HEADERS_TOP = ["#", "File", "Side", "Mode", "Side length", "Status", "PDF", "ZIP"]
TABLE_HEADERS_BOTTOM = ["#", "WAV file", "Title", "Length (PDF)", "Length (WAV)", "Difference(s)", "Match"]

# Table content strings

COLOR_WHITE = "white"
STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"

# Icon constants for UI rendering
ICON_CHECK = "check"
ICON_CROSS = "cross"
ICON_PLAY = "play"

# Deprecated: Use get_custom_icon('check') and get_custom_icon('cross') instead
# These constants are kept for backward compatibility but are no longer used in UI rendering
SYMBOL_CHECK = "✓"
SYMBOL_CROSS = "✗"
PLACEHOLDER_DASH = "-"
LABEL_TOTAL_TRACKS = "Total (tracks)"
# Interface strings
INTERFACE_MAIN = "Main"
