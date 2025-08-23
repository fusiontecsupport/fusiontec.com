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
        fontSize=28,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f3c88')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2563eb')
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        alignment=TA_CENTER,
        textColor=colors.white,
        backColor=colors.HexColor('#1f3c88')
    )
    
    # Add company logo with reduced top spacing
    logo_path = "products/static/products/img/fusiontec.png"
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.8*inch, height=0.9*inch)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 15))  # Reduced spacing
    
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
    story.append(Spacer(1, 25))  # Reduced spacing
    
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
        ['Hyp2003 (HyperSecu / ePass) Auto Token', '₹600', '₹600', '-', '₹1,200', '₹216', '₹1,416'],
        ['', '', '', '', '', '', ''],
        ['Foreign Class 3 - 2 Years', '₹10,000', '₹600', '₹2,000', '₹12,600', '₹2,268', '₹14,868'],
        ['Foreign Class 3 Combo - 2 Years', '₹15,000', '₹600', '₹2,000', '₹17,600', '₹3,168', '₹20,768']
    ]
    
    # Create the table with better column widths
    table = Table(pricing_data, colWidths=[2.4*inch, 1.1*inch, 0.8*inch, 1.1*inch, 1.0*inch, 1.0*inch, 1.2*inch])
    
    # Define improved table style
    table_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f3c88')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        
        # Data rows styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product column left-aligned
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Price columns right-aligned
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
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1f3c88')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1f3c88')),
        
        # Column specific styling
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Product names in bold
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),  # Prices in regular font
        
        # Row heights
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        
        # Cell padding
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])
    
    table.setStyle(table_style)
    story.append(table)
    
    # Add additional information with side-by-side layout
    story.append(Spacer(1, 25))
    
    # Create a proper two-column layout for features and contact info
    # Left column: Key Features & Benefits
    features_title = Paragraph("Key Features & Benefits", header_style)
    features = [
        "✓ Government Licensed Certifying Authority Partner",
        "✓ Used for GST, MCA, Income Tax, Tenders, EPFO and more",
        "✓ 2048 bit encryption • 24/7 support",
        "✓ Quick and secure paperless eKYC",
        "✓ Instant issuance and installation help",
        "✓ Trusted by businesses from MSMEs to enterprises across India"
    ]
    
    # Right column: Contact Information
    contact_title = Paragraph("Contact Information", header_style)
    contact_info = [
        "📧 Email: info@fusiontec.com",
        "📱 Phone: +91-XXXXXXXXXX",
        "🌐 Website: www.fusiontec.com",
        "📍 Address: [Your Company Address]"
    ]
    
    # Create the two-column data structure
    # Each row will contain left and right content
    two_column_data = []
    
    # Add titles row
    two_column_data.append([features_title, contact_title])
    
    # Add features and contact info in parallel rows
    max_items = max(len(features), len(contact_info))
    for i in range(max_items):
        left_item = Paragraph(features[i], styles['Normal']) if i < len(features) else Paragraph("", styles['Normal'])
        right_item = Paragraph(contact_info[i], styles['Normal']) if i < len(contact_info) else Paragraph("", styles['Normal'])
        two_column_data.append([left_item, right_item])
    
    # Create the two-column table
    two_column_table = Table(two_column_data, colWidths=[3.2*inch, 3.2*inch])
    
    # Style the two-column table
    two_column_style = TableStyle([
        # Remove all borders and grids
        ('GRID', (0, 0), (-1, -1), 0, colors.white),  # White grid (invisible)
        ('BOX', (0, 0), (-1, -1), 0, colors.white),    # White border (invisible)
        
        # Align content to top
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Remove padding to allow natural spacing
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        
        # Add some spacing between columns
        ('LEFTPADDING', (1, 0), (1, -1), 20),  # Right column left padding
    ])
    
    two_column_table.setStyle(two_column_style)
    story.append(two_column_table)
    
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
