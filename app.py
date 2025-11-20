import os
import csv
import uuid
import re
from io import BytesIO
from datetime import date
from flask import Flask, request, render_template, send_file, jsonify
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BAREMA_ANTIGO_CSV = 'barema_antigo.csv'
BAREMA_NOVO_CSV = 'barema_novo.csv'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_UESC_PATH = os.path.join(BASE_DIR, 'static', 'images', 'logo_uesc.png')
LOGO_COLCIC_PATH = os.path.join(BASE_DIR, 'static', 'images', 'logo_computacao.png')

def extract_max_hours(carga_maxima_str):
    if not carga_maxima_str: return None
    text_lower = carga_maxima_str.lower()
    if any(unidade in text_lower for unidade in ['/ano', 'por ano', '/evento', 'por evento', '/semestre', 'por semestre', '/projeto', 'por projeto', '/atividade', 'por atividade']):
        return None 
    matches = re.findall(r'm[áa]ximo de\s*(\d+)\s*h?', carga_maxima_str, re.IGNORECASE)
    if matches: return max(int(val) for val in matches)
    match = re.fullmatch(r'(\d+)\s*h(oras)?\.?', carga_maxima_str.strip(), re.IGNORECASE)
    if match: return int(match.group(1))
    return None

def ler_barema_csv(filename):
    atividades = []
    filepath = os.path.join(BASE_DIR, filename)
    try:
        with open(filepath, mode='r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            if not fieldnames or not all(key in fieldnames for key in ['id', 'atividade', 'carga_maxima']):
                infile.seek(0)
                reader = csv.DictReader(infile, delimiter=';')
            for row in reader:
                row['max_horas_num'] = extract_max_hours(row.get('carga_maxima', ''))
                atividades.append(row)
    except Exception as e: print(f"Erro ao ler CSV: {e}")
    return atividades

def gerar_barema_pdf(dados_barema):
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=landscape(A4))
    width, height = landscape(A4)
    y_center_header = height - 2.5*cm 

    try:
        img_uesc = ImageReader(LOGO_UESC_PATH)
        draw_height_uesc = 2*cm 
        img_w, img_h = img_uesc.getSize()
        draw_width_uesc = (draw_height_uesc / img_h) * img_w
        y_logo_uesc = y_center_header - (draw_height_uesc / 2)
        c.drawImage(img_uesc, 2*cm, y_logo_uesc, height=draw_height_uesc, width=draw_width_uesc, mask='auto', preserveAspectRatio=True)
    except: pass

    try:
        img_colcic = ImageReader(LOGO_COLCIC_PATH)
        draw_height_colcic = 1.5*cm 
        img_w, img_h = img_colcic.getSize()
        draw_width_colcic = (draw_height_colcic / img_h) * img_w
        x_logo_colcic = width - 2*cm - draw_width_colcic
        y_logo_colcic = y_center_header - (draw_height_colcic / 2)
        c.drawImage(img_colcic, x_logo_colcic, y_logo_colcic, height=draw_height_colcic, width=draw_width_colcic, mask='auto', preserveAspectRatio=True)
    except: pass

    c.setFont("Helvetica", 11) 
    c.drawCentredString(width / 2.0, y_center_header + 0.6*cm, "UNIVERSIDADE ESTADUAL DE SANTA CRUZ - UESC")
    c.drawCentredString(width / 2.0, y_center_header + 0.1*cm, "COLEGIADO DE CIÊNCIA DA COMPUTAÇÃO - COLCIC")
    c.setFont("Helvetica-Bold", 13) 
    c.drawCentredString(width / 2.0, y_center_header - 0.5*cm, "Barema de Atividades Complementares")
    c.setFont("Helvetica-Bold", 11)
    tipo_barema = dados_barema.get('tipo_barema', 'antigo')
    titulo_barema_2 = "(Ingressantes a partir de 2023.1)" if tipo_barema == 'novo' else "(Ingressantes até 2022.2)"
    c.drawCentredString(width / 2.0, y_center_header - 1.0*cm, titulo_barema_2)

    y_data = y_center_header - 2.2*cm 
    c.setFont("Helvetica", 9) 
    c.drawString(2*cm, y_data, f"Discente: {dados_barema.get('discente', '')}")
    c.drawString(10*cm, y_data, f"Matrícula: {dados_barema.get('matricula', '')}")
    c.drawString(15*cm, y_data, f"Email: {dados_barema.get('email', '')}")
    c.drawString(23*cm, y_data, f"Data: {dados_barema.get('data_verificacao', '')}")

    c.setFont("Helvetica-Bold", 8) 
    y_header_top = y_data - 1*cm
    y_header_text_baseline = y_header_top - 0.4*cm
    y_header_bottom = y_header_top - 0.6*cm
    x_atividade, x_ch_maxima, x_ch_cumprida, x_folha = 2*cm, 16*cm, 20.5*cm, 23*cm
    x_end = width - 2*cm 
    
    c.setStrokeColor(HexColor('#DDDDDD')) 
    c.setLineWidth(0.5) 
    c.line(x_atividade, y_header_top, x_end, y_header_top) 
    c.drawString(x_atividade + 0.2*cm, y_header_text_baseline, "Atividade")
    c.drawString(x_ch_maxima + 0.2*cm, y_header_text_baseline, "C.H. Máxima")
    c.drawString(x_ch_cumprida + 0.2*cm, y_header_text_baseline, "C.H. Cumprida")
    c.drawString(x_folha + 0.2*cm, y_header_text_baseline, "Folha")
    c.line(x_atividade, y_header_bottom, x_end, y_header_bottom) 
    
    styles = getSampleStyleSheet()
    style = ParagraphStyle(name='NormalCompact', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=TA_LEFT) 
    style_pagina = ParagraphStyle(name='PaginaCompact', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=8, alignment=TA_LEFT) 
    
    y_position = y_header_bottom - 0.5*cm
    total_horas = 0
    y_top_tabela_linhas = y_header_bottom

    for atividade in dados_barema['atividades']:
        horas, pagina = atividade.get("horas", ""), atividade.get("pagina", "")
        texto_atividade = f"{atividade['id']}. {atividade['descricao']}"
        carga_maxima = atividade.get("carga_maxima", "")
        
        p = Paragraph(texto_atividade, style)
        p_pagina = Paragraph(pagina, style_pagina)
        p_ch_maxima = Paragraph(carga_maxima, style_pagina)
        
        p_width = (x_ch_maxima - x_atividade) - 0.4*cm 
        p_ch_max_width = (x_ch_cumprida - x_ch_maxima) - 0.4*cm
        p_pagina_width = (x_end - x_folha) - 0.4*cm
        
        p_height = p.wrapOn(c, p_width, height)[1] 
        p_ch_max_height = p_ch_maxima.wrapOn(c, p_ch_max_width, height)[1]
        p_pagina_height = p_pagina.wrapOn(c, p_pagina_width, height)[1]
        
        line_height = max(p_height, p_pagina_height, p_ch_max_height)
        if y_position - line_height < 2*cm: break 

        p.drawOn(c, x_atividade + 0.2*cm, y_position - p_height) 
        p_ch_maxima.drawOn(c, x_ch_maxima + 0.2*cm, y_position - p_ch_max_height)
        first_line_baseline_y = y_position - style.leading 
        c.setFont("Helvetica", 7) 
        c.drawString(x_ch_cumprida + 0.5*cm, first_line_baseline_y, horas)
        y_drawon_pagina = first_line_baseline_y - (p_pagina_height - style_pagina.leading)
        p_pagina.drawOn(c, x_folha + 0.2*cm, y_drawon_pagina)
        
        y_position -= (line_height + 0.3*cm) 
        c.line(x_atividade, y_position + 0.15*cm, x_end, y_position + 0.15*cm)
        try:
            if horas: total_horas += int(horas)
        except ValueError: pass
    
    y_bottom_tabela = y_position + 0.15*cm
    c.line(x_atividade, y_header_top, x_atividade, y_bottom_tabela)
    c.line(x_ch_maxima, y_header_top, x_ch_maxima, y_bottom_tabela)
    c.line(x_ch_cumprida, y_header_top, x_ch_cumprida, y_bottom_tabela)
    c.line(x_folha, y_header_top, x_folha, y_bottom_tabela)
    c.line(x_end, y_header_top, x_end, y_bottom_tabela)

    c.setFont("Helvetica-Bold", 9) 
    c.drawString(x_ch_cumprida, y_position - 0.5*cm, f"TOTAL HORAS: {total_horas}")
    c.save()
    packet.seek(0)
    return packet

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_data = request.form
        barema_tipo = form_data.get('barema_tipo', 'antigo') 
        csv_filename = BAREMA_NOVO_CSV if barema_tipo == 'novo' else BAREMA_ANTIGO_CSV
        atividades = ler_barema_csv(csv_filename) 
        
        certificados_enviados = []
        for atividade in atividades:
            file_key = f"certificado_{atividade['id']}"
            files_list = request.files.getlist(file_key) 
            activity_files = []
            if files_list:
                for file in files_list:
                    if file and file.filename != '': 
                        page_count = 1
                        try:
                            reader = PdfReader(file)
                            page_count = len(reader.pages)
                        except: pass
                        file.seek(0) 
                        activity_files.append({'file': file, 'page_count': page_count})
            if activity_files: 
                certificados_enviados.append({'id': atividade['id'], 'files': activity_files})

        dados_barema_pdf = {
            'discente': form_data.get('nome', ''),
            'matricula': form_data.get('matricula', ''),
            'email': form_data.get('email', ''),
            'data_verificacao': form_data.get('data_verificacao', ''),
            'atividades': [],
            'tipo_barema': barema_tipo
        }
        
        pagina_atual = 2
        for atividade in atividades:
            horas = form_data.get(f"horas_{atividade['id']}", "")
            pagina_ranges = []
            for cert_group in certificados_enviados:
                if cert_group['id'] == atividade['id']:
                    for cert_file in cert_group['files']:
                        page_count = cert_file['page_count']
                        if page_count > 1:
                            pagina_final = pagina_atual + page_count - 1
                            pagina_ranges.append(f"{pagina_atual}-{pagina_final}")
                        else:
                            pagina_ranges.append(str(pagina_atual))
                        pagina_atual += page_count
                    break 
            
            dados_barema_pdf['atividades'].append({
                'id': atividade['id'],
                'descricao': next((item['atividade'] for item in atividades if item['id'] == atividade['id']), 'N/A'), 
                'carga_maxima': next((item['carga_maxima'] for item in atividades if item['id'] == atividade['id']), 'N/A'),
                'horas': horas,
                'pagina': ", ".join(pagina_ranges)
            })

        barema_pdf_gerado = gerar_barema_pdf(dados_barema_pdf)
        merger = PdfWriter()
        merger.append(barema_pdf_gerado)
        for cert_group in certificados_enviados:
            for cert_info in cert_group['files']:
                cert_info['file'].seek(0)
                merger.append(cert_info['file'])

        output_filename = f"documento_final_{uuid.uuid4().hex}.pdf"
        output_stream = BytesIO()
        merger.write(output_stream)
        output_stream.seek(0)
        return send_file(output_stream, as_attachment=True, download_name=output_filename)

    # --- CARREGA DADOS INICIAIS ---
    atividades = ler_barema_csv(BAREMA_ANTIGO_CSV)
    data_hoje = date.today().strftime("%d/%m/%Y")
    return render_template('index.html', data_hoje=data_hoje, atividades=atividades)

@app.route('/get_barema_data/<tipo_barema>')
def get_barema_data(tipo_barema):
    if tipo_barema == 'novo':
        atividades = ler_barema_csv(BAREMA_NOVO_CSV)
    else:
        atividades = ler_barema_csv(BAREMA_ANTIGO_CSV)
    return jsonify(atividades)

if __name__ == '__main__':
    app.run(debug=True)