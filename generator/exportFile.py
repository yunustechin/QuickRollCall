import csv 
import io 
from typing import Dict, Any

class ExportFile:
    """
    A class responsible for formatting attendance data into different file types.
    """
    def __init__(self, students_data: Dict[str, Any]):
        """
        Initializes the exporter with the student data.
        Args:
            students_data: A dictionary of student records.
        """
        self.students_data = students_data

    def generate_txt(self) -> str:
        """
        Generates a human-readable TXT file content from student data.
        Returns:
            A string containing the formatted TXT content.
        """
        if not self.students_data:
            return "No student was found who participated in the roll call."
        
        txt_content = ["Quick Roll Call\n", "="*20 + "\n\n"]

        for i, student in enumerate(self.students_data.values(),1):
            txt_content.append(f" Student {i}\n")
            txt_content.append(f" - School No: {student.get('school_no', 'N/A')}\n")
            txt_content.append(f" - Name Surname: {student.get('name', '')} {student.get('surname', '')}\n")
            txt_content.append(f" - Faculty: {student.get('faculty', 'N/A')}\n")
            txt_content.append(f" - Section: {student.get('section', 'N/A')}\n")
            txt_content.append("-" * 20 + "\n")
        
        return "".join(txt_content)
    
    def generate_csv(self) -> str:
        """
        Generates CSV content from student data, ensuring UTF-8 with BOM for
        proper character encoding in programs like Excel.
        Returns:
            A string containing the formatted CSV content.
        """
        if not self.students_data:
            return "school_no,name,surname,faculty,section\n"
        
        output = io.StringIO()
        fieldnames = ['school_no', 'name', 'surname', 'faculty', 'section']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(self.students_data.values())
        return "\ufeff" + output.getvalue()
