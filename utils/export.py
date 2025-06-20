import csv
import io
from typing import Dict, Any

class StudentDataExporter:
    NO_DATA_MSG = "No student was found who participated in the roll call."
    CSV_HEADER = ['school_no', 'name', 'surname', 'faculty', 'section']

    def __init__(self, students_data: Dict[str, Dict[str, Any]]):
        self.students_data = students_data

    def is_empty(self) -> bool:
        return not bool(self.students_data)

    def generate_txt(self) -> str:
        """Generate a human-readable TXT representation of student data."""
        if self.is_empty():
            return self.NO_DATA_MSG

        lines = ["Quick Roll Call\n", "=" * 20 + "\n\n"]
        for i, student in enumerate(self.students_data.values(), 1):
            lines.append(f" Student {i}\n")
            lines.append(f" - School No: {student.get('school_no', 'N/A')}\n")
            lines.append(f" - Name Surname: {student.get('name', '')} {student.get('surname', '')}\n")
            lines.append(f" - Faculty: {student.get('faculty', 'N/A')}\n")
            lines.append(f" - Section: {student.get('section', 'N/A')}\n")
            lines.append("-" * 20 + "\n")
        return "".join(lines)

    def generate_csv(self) -> str:
        """Generate CSV content with UTF-8 BOM for Excel compatibility."""
        if self.is_empty():
            return ",".join(self.CSV_HEADER) + "\n"

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.CSV_HEADER)
        writer.writeheader()
        writer.writerows(self.students_data.values())

        return "\ufeff" + output.getvalue()
