from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import qrcode
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.form.to_dict()
    cert_type = data['type']
    filename = f"{cert_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = os.path.join("output", filename)

    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()

    # Background image (A4 size)
    bg_path = f"certificate_templates/{cert_type}_template.png"
    if os.path.exists(bg_path):
        pdf.image(bg_path, x=0, y=0, w=210, h=297)

    # Certificate Title
    pdf.set_font("Arial", size=28, style='B')
    pdf.set_text_color(0, 0, 128)
    pdf.set_xy(0, 20)
    pdf.cell(0, 15, f"{cert_type.capitalize()} Certificate", ln=True, align='C')

    # Field Data
    pdf.set_text_color(0, 0, 0)
    x = 30          # Left margin
    start_y = 70    # Start below title
    line_height = 12

    fields = [
        ("Certificate No.", data['reg_no']),
        ("Full Name", data['full_name']),
        ("Date", data['date']),
        ("Gender", data['gender']),
        ("Place", data['place']),
        ("Relative", data['relative']),
        ("Address", data['address']),
        ("Issuing Authority", data['authority']),
        ("Issue Date", str(datetime.now().date()))
    ]

    for i, (label, value) in enumerate(fields):
        y = start_y + i * line_height
        pdf.set_xy(x, y)

        pdf.set_font("Arial", size=16, style='B')   # Bold label
        pdf.cell(50, line_height, f"{label}:", ln=False)

        pdf.set_font("Arial", size=16)              # Regular value
        pdf.cell(0, line_height, value, ln=True)

    # QR Code generation
    qr_data = f"{cert_type.upper()} | {data['full_name']} | Reg No: {data['reg_no']}"
    qr = qrcode.make(qr_data)
    qr_path = os.path.join("output", "temp_qr.png")
    qr.save(qr_path)
    pdf.image(qr_path, x=150, y=240, w=40)
    os.remove(qr_path)

    # Save and return PDF
    pdf.output(output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs("output", exist_ok=True)
    app.run(debug=True)
