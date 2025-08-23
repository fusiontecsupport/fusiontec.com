#!/usr/bin/env python3
"""
DSC Price List PDF Generator
Creates a professional DSC price list with company logo and current rates
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import os

def create_dsc_price_list_pdf():
    """Create a professional DSC price list PDF"""
    
    # Output file path
    output_path = "products/static/products/dsc_price_list.pdf"
    
    # Create the PDF document
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f3c88')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=colors.white,
        backColor=colors.HexColor('#1f3c88')
    )
    
    # Add company logo
    logo_path = "products/static/products/img/fusiontec.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*inch, height=1*inch)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 20))
    
    # Add title
    title = Paragraph("Digital Signature Certificate (DSC) Price List", title_style)
    story.append(title)
    
    # Add subtitle
    subtitle = Paragraph("Professional DSC Solutions for Business & Individuals", subtitle_style)
    story.append(subtitle)
    
    # Add company tagline
    tagline = Paragraph("Celebrating 25 Years of Simplifying Complexity - Your Trusted Partner in Innovative Solutions", 
                       styles['Normal'])
    tagline.alignment = TA_CENTER
    story.append(tagline)
    story.append(Spacer(1, 30))
    
    # Define the pricing data based on the screenshot
    pricing_data = [
        ['Product', 'DSC Charges', 'Token', 'Service Charges', 'Total', 'GST 18%', 'Nett Amount'],
        ['Class 3 - 1 Year', '₹1,350', '₹600', '₹499', '₹2,449', '₹441', '₹2,890'],
        ['Class 3 - 2 Year', '₹1,500', '₹600', '₹499', '₹2,599', '₹468', '₹3,067'],
        ['Class 3 - 3 Year', '₹2,250', '₹600', '₹499', '₹3,349', '₹603', '₹3,952'],
        ['', '', '', '', '', '', ''],
        ['Class 3 Combo - 1 Year', '₹2,000', '₹600', '₹499', '₹3,099', '₹558', '₹3,657'],
        ['Class 3 Combo - 2 Year', '₹2,250', '₹600', '₹499', '₹3,349', '₹603', '₹3,952'],
        ['Class 3 Combo - 3 Year', '₹3,350', '₹600', '₹499', '₹4,449', '₹801', '₹5,250'],
        ['', '', '', '', '', '', ''],
        ['DGFT - 1 Year', '₹1,800', '₹600', '₹499', '₹2,899', '₹522', '₹3,421'],
        ['DGFT - 2 Year', '₹2,000', '₹600', '₹499', '₹3,099', '₹558', '₹3,657'],
        ['', '', '', '', '', '', ''],
        ['Hyp2003 (HyperSecu / ePass) Auto Token', '₹600', '₹600', '', '₹1,200', '₹216', '₹1,416'],
        ['', '', '', '', '', '', ''],
        ['Foreign Class 3 - 2 Years', '₹10,000', '₹600', '₹2,000', '₹12,600', '₹2,268', '₹14,868'],
        ['Foreign Class 3 Combo - 2 Years', '₹15,000', '₹600', '₹2,000', '₹17,600', '₹3,168', '₹20,768']
    ]
    
    # Create the table
    table = Table(pricing_data, colWidths=[2.2*inch, 1.2*inch, 0.8*inch, 1.2*inch, 1.0*inch, 1.0*inch, 1.2*inch])
    
    # Define table style
    table_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f3c88')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        
        # Data rows styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product column left-aligned
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Other columns center-aligned
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Alternating row colors
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 9), (-1, 9), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 11), (-1, 11), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 13), (-1, 13), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 15), (-1, 15), colors.HexColor('#f8f9fa')),
        
        # Empty rows styling
        ('BACKGROUND', (0, 4), (-1, 4), colors.white),
        ('BACKGROUND', (0, 8), (-1, 8), colors.white),
        ('BACKGROUND', (0, 12), (-1, 12), colors.white),
        ('BACKGROUND', (0, 14), (-1, 14), colors.white),
        
        # Border styling
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1f3c88')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1f3c88')),
        
        # Column specific styling
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Product names in bold
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),  # Prices in regular font
        
        # Price columns right-aligned for better readability
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
    ])
    
    table.setStyle(table_style)
    story.append(table)
    
    # Add additional information
    story.append(Spacer(1, 30))
    
    # Add features section
    features_title = Paragraph("Key Features & Benefits", header_style)
    story.append(features_title)
    
    features = [
        "✓ Government Licensed Certifying Authority Partner",
        "✓ Used for GST, MCA, Income Tax, Tenders, EPFO and more",
        "✓ 2048 bit encryption • 24/7 support",
        "✓ Quick and secure paperless eKYC",
        "✓ Instant issuance and installation help",
        "✓ Trusted by businesses from MSMEs to enterprises across India"
    ]
    
    for feature in features:
        feature_para = Paragraph(feature, styles['Normal'])
        story.append(feature_para)
        story.append(Spacer(1, 5))
    
    story.append(Spacer(1, 20))
    
    # Add contact information
    contact_title = Paragraph("Contact Information", header_style)
    story.append(contact_title)
    
    contact_info = [
        "📧 Email: info@fusiontec.com",
        "📱 Phone: +91-XXXXXXXXXX",
        "🌐 Website: www.fusiontec.com",
        "📍 Address: [Your Company Address]"
    ]
    
    for contact in contact_info:
        contact_para = Paragraph(contact, styles['Normal'])
        story.append(contact_para)
        story.append(Spacer(1, 5))
    
    # Build the PDF
    doc.build(story)
    
    print(f"DSC Price List PDF created successfully at: {output_path}")

if __name__ == "__main__":
    try:
        create_dsc_price_list_pdf()
        print("✅ DSC Price List PDF generated successfully!")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
