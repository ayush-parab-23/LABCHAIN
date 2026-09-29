import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_lab_report(filename, patient_name, patient_id, age, gender, test_type, test_results):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Page setup - 0.75 in margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor("#0f172a") # Slate 900
    secondary_color = colors.HexColor("#0284c7") # Sky 600
    border_color = colors.HexColor("#cbd5e1") # Slate 300
    text_color = colors.HexColor("#334155") # Slate 700
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=secondary_color
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color
    )
    
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=text_color
    )
    
    cell_bold_style = ParagraphStyle(
        'CellBold',
        parent=cell_style,
        fontName='Helvetica-Bold'
    )
    
    cell_high_style = ParagraphStyle(
        'CellHigh',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#ef4444") # Red 500
    )
    
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b"),
        alignment=1 # Center
    )

    # 1. Header Section
    story.append(Paragraph("LABCHAIN CLINICAL DIAGNOSTIC CENTER", title_style))
    story.append(Paragraph("100 Health Science Parkway, Suite 400 | Phone: (555) 019-2834 | Email: lab@labchain.org", subtitle_style))
    story.append(Spacer(1, 15))
    
    # Horizontal line
    line_table = Table([[""]], colWidths=[504])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, secondary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 15))
    
    # 2. Patient Info Block (Table format)
    info_data = [
        [
            Paragraph("<b>Patient Name:</b>", cell_style), Paragraph(patient_name, cell_bold_style),
            Paragraph("<b>Report ID:</b>", cell_style), Paragraph(patient_id.replace("PAT", "LAB"), cell_bold_style)
        ],
        [
            Paragraph("<b>Patient ID:</b>", cell_style), Paragraph(patient_id, cell_style),
            Paragraph("<b>Report Date:</b>", cell_style), Paragraph("2026-08-13", cell_style)
        ],
        [
            Paragraph("<b>Age / Gender:</b>", cell_style), Paragraph(f"{age} / {gender}", cell_style),
            Paragraph("<b>Referred By:</b>", cell_style), Paragraph("Dr. Sarah Jenkins, M.D.", cell_style)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[90, 162, 90, 162])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 25))
    
    # 3. Test Section Title
    story.append(Paragraph(f"{test_type.upper()} RESULTS", header_style))
    story.append(Spacer(1, 10))
    
    # 4. Results Table
    # Table Header
    results_data = [[
        Paragraph("<b>Test Parameter</b>", cell_bold_style),
        Paragraph("<b>Observed Value</b>", cell_bold_style),
        Paragraph("<b>Reference Range</b>", cell_bold_style),
        Paragraph("<b>Flag</b>", cell_bold_style)
    ]]
    
    # Add test parameter rows
    for test_param, obs_val, ref_range, flag in test_results:
        val_style = cell_style
        flag_style = cell_style
        if flag == "HIGH" or flag == "LOW":
            val_style = cell_high_style
            flag_style = cell_high_style
            
        results_data.append([
            Paragraph(test_param, cell_style),
            Paragraph(obs_val, val_style),
            Paragraph(ref_range, cell_style),
            Paragraph(flag, flag_style)
        ])
        
    results_table = Table(results_data, colWidths=[180, 108, 126, 90])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 40))
    
    # 5. Cryptographic Verification & Footer
    story.append(Paragraph("------------------ END OF REPORT ------------------", footer_style))
    story.append(Spacer(1, 20))
    
    footer_text = (
        "Notice: This document is cryptographically signed and registered on the LABCHAIN "
        "Blockchain Integrity Verification Network. Any alteration to the text, layout, or numbers "
        "of this PDF will invalidate the file hash registry. To verify authenticity, upload this file "
        "or scan the report QR code in the LABCHAIN hospital validation portal."
    )
    story.append(Paragraph(footer_text, footer_style))
    
    doc.build(story)
    print(f"Generated report: {filename}")

def generate_all_reports():
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)
    
    # 1. Ayush (Original)
    create_lab_report(
        os.path.join(downloads_dir, "Ayush_report.pdf"),
        "Ayush",
        "PAT-2001",
        24,
        "Male",
        "Lipid Profile",
        [
            ("Cholesterol, Total", "185 mg/dL", "< 200 mg/dL", "NORMAL"),
            ("Triglycerides", "130 mg/dL", "< 150 mg/dL", "NORMAL"),
            ("HDL Cholesterol", "52 mg/dL", "> 40 mg/dL", "NORMAL"),
            ("LDL Cholesterol (Calc)", "107 mg/dL", "< 100 mg/dL", "NORMAL")
        ]
    )
    
    # 2. Ayush (Tampered) - Cholesterol changed from 185 to 385 (HIGH)
    create_lab_report(
        os.path.join(downloads_dir, "Ayush_temp.pdf"),
        "Ayush",
        "PAT-2001",
        24,
        "Male",
        "Lipid Profile",
        [
            ("Cholesterol, Total", "385 mg/dL", "< 200 mg/dL", "HIGH"),
            ("Triglycerides", "130 mg/dL", "< 150 mg/dL", "NORMAL"),
            ("HDL Cholesterol", "52 mg/dL", "> 40 mg/dL", "NORMAL"),
            ("LDL Cholesterol (Calc)", "107 mg/dL", "< 100 mg/dL", "NORMAL")
        ]
    )
    
    # 3. Arya
    create_lab_report(
        os.path.join(downloads_dir, "Arya_report.pdf"),
        "Arya",
        "PAT-2002",
        22,
        "Male",
        "Thyroid Profile",
        [
            ("TSH (Third Generation)", "2.45 uIU/mL", "0.45 - 4.50 uIU/mL", "NORMAL"),
            ("Free T3", "3.1 pg/mL", "2.0 - 4.4 pg/mL", "NORMAL"),
            ("Free T4", "1.2 ng/dL", "0.8 - 1.8 ng/dL", "NORMAL")
        ]
    )
    
    # 4. Piyush (Original)
    create_lab_report(
        os.path.join(downloads_dir, "Piyush_report.pdf"),
        "Piyush",
        "PAT-2003",
        25,
        "Male",
        "Liver Function Test",
        [
            ("Alanine Aminotransferase (ALT)", "28 U/L", "7 - 56 U/L", "NORMAL"),
            ("Aspartate Aminotransferase (AST)", "24 U/L", "10 - 40 U/L", "NORMAL"),
            ("Bilirubin, Total", "0.8 mg/dL", "0.2 - 1.2 mg/dL", "NORMAL"),
            ("Alkaline Phosphatase (ALP)", "72 U/L", "44 - 147 U/L", "NORMAL")
        ]
    )

    # 4b. Piyush (Tampered) - Bilirubin altered from 0.8 to 4.8 mg/dL (HIGH) and ALT from 28 to 145 U/L (HIGH)
    create_lab_report(
        os.path.join(downloads_dir, "Piyush_temp.pdf"),
        "Piyush",
        "PAT-2003",
        25,
        "Male",
        "Liver Function Test",
        [
            ("Alanine Aminotransferase (ALT)", "145 U/L", "7 - 56 U/L", "HIGH"),
            ("Aspartate Aminotransferase (AST)", "24 U/L", "10 - 40 U/L", "NORMAL"),
            ("Bilirubin, Total", "4.8 mg/dL", "0.2 - 1.2 mg/dL", "HIGH"),
            ("Alkaline Phosphatase (ALP)", "72 U/L", "44 - 147 U/L", "NORMAL")
        ]
    )
    
    # 5. Rohan
    create_lab_report(
        os.path.join(downloads_dir, "Rohan_report.pdf"),
        "Rohan",
        "PAT-2004",
        23,
        "Male",
        "Kidney Function Test",
        [
            ("Urea", "26 mg/dL", "15 - 45 mg/dL", "NORMAL"),
            ("Creatinine", "0.9 mg/dL", "0.6 - 1.2 mg/dL", "NORMAL"),
            ("Uric Acid", "5.4 mg/dL", "3.5 - 7.2 mg/dL", "NORMAL")
        ]
    )

    # 6. Archie
    create_lab_report(
        os.path.join(downloads_dir, "Archie_report.pdf"),
        "Archie",
        "PAT-2005",
        21,
        "Female",
        "Complete Blood Count",
        [
            ("White Blood Cell (WBC)", "6.5 x10^3/uL", "4.5 - 11.0 x10^3/uL", "NORMAL"),
            ("Red Blood Cell (RBC)", "4.8 x10^6/uL", "4.3 - 5.9 x10^6/uL", "NORMAL"),
            ("Hemoglobin (Hb)", "14.2 g/dL", "13.5 - 17.5 g/dL", "NORMAL"),
            ("Platelets", "250 x10^3/uL", "150 - 450 x10^3/uL", "NORMAL")
        ]
    )

    # 7. Manaswi
    create_lab_report(
        os.path.join(downloads_dir, "Manaswi_report.pdf"),
        "Manaswi",
        "PAT-2006",
        22,
        "Female",
        "Diabetes Panel",
        [
            ("HbA1c", "5.4 %", "< 5.7 %", "NORMAL"),
            ("Glucose, Fasting", "92 mg/dL", "70 - 99 mg/dL", "NORMAL"),
            ("Post-Prandial Glucose", "120 mg/dL", "< 140 mg/dL", "NORMAL")
        ]
    )

    # 8. Riya
    create_lab_report(
        os.path.join(downloads_dir, "Riya_report.pdf"),
        "Riya",
        "PAT-2007",
        23,
        "Female",
        "Vitamin Panel",
        [
            ("Vitamin D (25-Hydroxy)", "35 ng/mL", "30 - 100 ng/mL", "NORMAL"),
            ("Vitamin B12", "420 pg/mL", "200 - 900 pg/mL", "NORMAL")
        ]
    )

if __name__ == '__main__':
    generate_all_reports()
