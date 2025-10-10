"""
Сервис для формирования отчетов
"""
import csv
import io
from typing import List, Dict
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from integrations import google_sheets_service, openai_service


class ReportService:
    """Сервис для создания отчетов"""
    
    def generate_users_report(self, format_type: str = "csv") -> str:
        """
        Генерировать отчет по пользователям
        
        Args:
            format_type: Формат отчета (csv или pdf)
        
        Returns:
            Путь к файлу отчета
        """
        users = google_sheets_service.get_all_users()
        
        if format_type == "csv":
            return self._create_csv_report(users, "users_report.csv")
        elif format_type == "pdf":
            return self._create_pdf_report(
                users, 
                "users_report.pdf",
                "Отчет по пользователям"
            )
    
    def generate_applications_report(self, format_type: str = "csv") -> str:
        """
        Генерировать отчет по заявкам
        
        Args:
            format_type: Формат отчета
        
        Returns:
            Путь к файлу отчета
        """
        applications = google_sheets_service.get_applications()
        
        if format_type == "csv":
            return self._create_csv_report(applications, "applications_report.csv")
        elif format_type == "pdf":
            return self._create_pdf_report(
                applications,
                "applications_report.pdf",
                "Отчет по заявкам на вступление"
            )
    
    def generate_feedback_report(self, format_type: str = "csv") -> str:
        """
        Генерировать отчет по обратной связи с анализом
        
        Args:
            format_type: Формат отчета
        
        Returns:
            Путь к файлу отчета
        """
        feedback_data = google_sheets_service.get_feedback()
        
        # Получаем анализ от AI
        feedback_messages = [fb.get("Сообщение", "") for fb in feedback_data]
        analysis = openai_service.analyze_feedback(feedback_messages)
        
        # Добавляем анализ в начало данных
        report_data = [
            {"Тип": "АНАЛИЗ", "Содержание": analysis},
            {"Тип": "---", "Содержание": "---"},
        ]
        
        for fb in feedback_data:
            report_data.append({
                "Тип": fb.get("Категория", ""),
                "Содержание": fb.get("Сообщение", ""),
                "Дата": fb.get("Дата", "")
            })
        
        if format_type == "csv":
            return self._create_csv_report(report_data, "feedback_report.csv")
        elif format_type == "pdf":
            return self._create_pdf_report(
                report_data,
                "feedback_report.pdf",
                "Отчет по обратной связи"
            )
    
    def generate_statistics_report(self) -> Dict:
        """
        Генерировать статистику
        
        Returns:
            Словарь со статистикой
        """
        users = google_sheets_service.get_all_users()
        applications = google_sheets_service.get_applications()
        feedback = google_sheets_service.get_feedback()
        
        stats = {
            "total_users": len(users),
            "total_applications": len(applications),
            "new_applications": len([a for a in applications 
                                    if a.get("Статус") == "Новая"]),
            "total_feedback": len(feedback),
            "questions": len([f for f in feedback 
                            if f.get("Категория") == "question"]),
            "complaints": len([f for f in feedback 
                             if f.get("Категория") == "complaint"]),
            "suggestions": len([f for f in feedback 
                              if f.get("Категория") == "suggestion"]),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return stats
    
    def _create_csv_report(self, data: List[Dict], filename: str) -> str:
        """
        Создать CSV отчет
        
        Args:
            data: Данные для отчета
            filename: Имя файла
        
        Returns:
            Путь к файлу
        """
        if not data:
            return ""
        
        filepath = f"reports/{filename}"
        
        try:
            import os
            os.makedirs("reports", exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            return filepath
        except Exception as e:
            print(f"Ошибка создания CSV отчета: {e}")
            return ""
    
    def _create_pdf_report(self, data: List[Dict], filename: str, 
                          title: str) -> str:
        """
        Создать PDF отчет
        
        Args:
            data: Данные для отчета
            filename: Имя файла
            title: Заголовок отчета
        
        Returns:
            Путь к файлу
        """
        if not data:
            return ""
        
        filepath = f"reports/{filename}"
        
        try:
            import os
            os.makedirs("reports", exist_ok=True)
            
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            
            styles = getSampleStyleSheet()
            
            # Заголовок
            elements.append(Paragraph(title, styles['Title']))
            elements.append(Paragraph(
                f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                styles['Normal']
            ))
            
            # Таблица с данными
            if data:
                table_data = [list(data[0].keys())]
                for row in data:
                    table_data.append(list(row.values()))
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
            
            doc.build(elements)
            return filepath
        except Exception as e:
            print(f"Ошибка создания PDF отчета: {e}")
            return ""


report_service = ReportService()

