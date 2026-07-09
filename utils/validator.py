class Validator:
    @staticmethod
    def validate_document_details(document_number: str, subject: str, date: str) -> tuple[bool, str]:
        """
        Validates the document details.
        Returns a tuple of (is_valid, error_message).
        """
        if not document_number or not document_number.strip():
            return False, "Document Number is required."
        if not subject or not subject.strip():
            return False, "Subject is required."
        if not date or not date.strip():
            return False, "Date is required."
        
        # We could add more complex date validation here if needed
        
        return True, ""
