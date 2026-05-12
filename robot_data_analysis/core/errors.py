"""Typed exceptions used by robot_data_analysis."""


class RobotDataAnalysisError(Exception):
    """Base exception for library-specific failures."""


class MissingColumnsError(ValueError, RobotDataAnalysisError):
    """Raised when a DataFrame does not contain required columns."""

    def __init__(self, missing_columns):
        self.missing_columns = tuple(missing_columns)
        missing = ", ".join(self.missing_columns)
        super().__init__(f"missing required columns: {missing}")


class DataLoadError(RobotDataAnalysisError):
    """Raised when a data source cannot be loaded."""

