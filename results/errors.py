class DiagnosisError(Exception):
    """Raised by a diagnosis service when it cannot give a result.

    The message must be short, plain and safe to show to a farmer: no codes,
    no file paths and no answers from a provider. Technical details go to
    the terminal only.
    """