import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

class PDFService:
    def __init__(self):
        pass

    def generate_pdf(self, employee_data: dict, document_data: dict, logo_path: str = None, output_path: str = None) -> str:
        """
        Generates the Confidential Report PDF.
        """
        if not output_path:
            raise ValueError("output_path is required")
            
        filepath = output_path

        doc = SimpleDocTemplate(filepath, pagesize=letter,
                                rightMargin=50, leftMargin=50,
                                topMargin=36, bottomMargin=36)
        
        styles = getSampleStyleSheet()
        
        center_style = ParagraphStyle(
            'CenterTitle', parent=styles['Normal'], alignment=1, fontSize=13, spaceAfter=6, fontName="Helvetica-Bold"
        )
        sub_title_style = ParagraphStyle(
            'SubTitle', parent=styles['Normal'], alignment=1, fontSize=11, spaceAfter=10, fontName="Helvetica-Bold"
        )
        question_style = ParagraphStyle(
            'Question', parent=styles['Normal'], fontSize=10, spaceAfter=3, fontName="Helvetica-Bold"
        )
        answer_style = ParagraphStyle(
            'Answer', parent=styles['Normal'], fontSize=10, spaceAfter=8, textColor=colors.HexColor("#333333")
        )

        elements = []

        # Logo
        if logo_path and os.path.exists(logo_path):
            try:
                # 1.0 inch size so it still fits nicely on one page
                img = Image(logo_path, width=1.0*inch, height=1.0*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(1, 5))
            except Exception:
                pass

        # Title and Subtitle
        elements.append(Paragraph("Sadhu Vaswani International School, Moshi Pradhikaran", center_style))
        elements.append(Paragraph("CONFIDENTIAL REPORT", sub_title_style))
            
        elements.append(Spacer(1, 10))
        
        # 1. Name
        elements.append(Paragraph("1. Name of applicant", question_style))
        elements.append(Paragraph(employee_data.get("Full Name", ""), answer_style))
        
        # 2. How long
        elements.append(Paragraph("2. How long have you known the applicant?", question_style))
        elements.append(Paragraph(document_data.get("How Long", ""), answer_style))
        
        # 3. Activities
        elements.append(Paragraph("3. In which school activities is the applicant the happiest/ most successful?", question_style))
        acts = document_data.get("Activities", [])
        act_text = ", ".join(acts) if acts else "None selected"
        elements.append(Paragraph(act_text, answer_style))
        
        # 4. Factors
        elements.append(Paragraph("4. To which of the following factors would you ascribe the applicant's academic achievements?", question_style))
        factors = document_data.get("Factors", [])
        fact_text = ", ".join(factors) if factors else "None selected"
        elements.append(Paragraph(fact_text, answer_style))
        
        # 5. Ratings
        elements.append(Paragraph("5. Please indicate how you rate the candidate on the following attributes, on a scale of 1 to 5:", question_style))
        
        ratings = document_data.get("Ratings", {})
        rating_data = [["Attribute", "Rating (1-5)"]]
        for k, v in ratings.items():
            rating_data.append([k, v])
            
        rating_table = Table(rating_data, colWidths=[4*inch, 2*inch])
        rating_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(rating_table)
        elements.append(Spacer(1, 10))
        
        # 6. Comments
        comments = document_data.get("Comments", "").strip()
        if comments:
            elements.append(Paragraph("Any other comments, or factors you may wish to bring to our attention:", question_style))
            elements.append(Paragraph(comments, answer_style))
        
        # 7. Achievements
        achievements = document_data.get("Achievements", "").strip()
        if achievements:
            elements.append(Paragraph("Special achievements of the applicant – medals, prizes, etc:", question_style))
            elements.append(Paragraph(achievements, answer_style))
        
        # 8. Signature & Date
        elements.append(Spacer(1, 20))
        sig_data = [["_______________________", "_______________________"],
                    ["Signature of Principal", f"Date: {document_data.get('Generated_DateTime', '')}"]]
        sig_table = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ]))
        elements.append(sig_table)
        
        doc.build(elements)
        
        return filepath
