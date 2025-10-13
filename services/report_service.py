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
        feedback = google_sheets_service.get_feedback()
        complaints = google_sheets_service.get_complaints()
        events = google_sheets_service.get_events()
        legislation = google_sheets_service.get_legislation()
        chat_analytics = google_sheets_service.get_chat_analytics()
        
        stats = {
            "total_users": len(users),
            "total_feedback": len(feedback),
            "questions": len([f for f in feedback 
                            if f.get("Категория") == "question"]),
            "complaints": len([f for f in feedback 
                             if f.get("Категория") == "complaint"]),
            "suggestions": len([f for f in feedback 
                              if f.get("Категория") == "suggestion"]),
            "total_complaints": len(complaints),
            "total_events": len(events),
            "total_legislation": len(legislation),
            "total_chat_sessions": len(chat_analytics),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Дополнительная статистика по жалобам
        if complaints:
            stats["complaints_by_status"] = {}
            for complaint in complaints:
                status = complaint.get("Статус", "Неизвестно")
                stats["complaints_by_status"][status] = stats["complaints_by_status"].get(status, 0) + 1
        
        # Дополнительная статистика по мероприятиям
        if events:
            stats["events_by_status"] = {}
            for event in events:
                status = event.get("Статус", "Неизвестно")
                stats["events_by_status"][status] = stats["events_by_status"].get(status, 0) + 1
        
        # Дополнительная статистика по аналитике чата
        if chat_analytics:
            total_messages = 0
            total_documents = 0
            response_times = []
            
            for a in chat_analytics:
                try:
                    messages = a.get("Количество сообщений", 0)
                    if isinstance(messages, (int, float)):
                        total_messages += int(messages)
                    elif isinstance(messages, str) and messages.isdigit():
                        total_messages += int(messages)
                except (ValueError, TypeError):
                    pass
                
                try:
                    documents = a.get("Создано документов", 0)
                    if isinstance(documents, (int, float)):
                        total_documents += int(documents)
                    elif isinstance(documents, str) and documents.isdigit():
                        total_documents += int(documents)
                except (ValueError, TypeError):
                    pass
                
                try:
                    response_time = a.get("Среднее время ответа (сек)", 0)
                    if isinstance(response_time, (int, float)):
                        response_times.append(float(response_time))
                    elif isinstance(response_time, str):
                        response_times.append(float(response_time))
                except (ValueError, TypeError):
                    pass
            
            stats["total_messages"] = total_messages
            stats["total_documents_created"] = total_documents
            stats["avg_response_time"] = sum(response_times) / len(response_times) if response_times else 0
        
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

