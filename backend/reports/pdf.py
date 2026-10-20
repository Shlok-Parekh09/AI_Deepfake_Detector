"""Two-page English audit worksheet with embedded Times New Roman fonts."""
import base64
import io
import os
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image


@lru_cache(maxsize=1)
def register_fonts():
    from backend.models.weight_registry import local_weight, private_weight
    for name, filename in [('AuditTimes','times.ttf'),('AuditTimes-Bold','timesbd.ttf'),('AuditTimes-Italic','timesi.ttf')]:
        windows = Path('C:/Windows/Fonts') / filename
        configured = Path(os.getenv('AUDIT_FONT_DIRECTORY','model_weights/reports/fonts')) / filename
        path = configured if configured.is_file() else windows if windows.is_file() else None
        if path is None:
            artifact = 'reports/fonts/' + filename
            path = local_weight(artifact) or private_weight(artifact)
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily('AuditTimes',normal='AuditTimes',bold='AuditTimes-Bold',italic='AuditTimes-Italic',boldItalic='AuditTimes-Bold')


def text(value, limit=800):
    # Unsupported filename glyphs are represented as escapes in the English report.
    value = str(value if value is not None else 'Not recorded')[:limit]
    return escape(value.encode('ascii',errors='backslashreplace').decode('ascii'))


def build_pdf(evidence):
    register_fonts()
    output = io.BytesIO()
    document = SimpleDocTemplate(output,pagesize=A4,rightMargin=46,leftMargin=46,
        topMargin=62,bottomMargin=48,title='Media Authenticity Assessment - ' + evidence['report_id'],
        author='Deepfake Analyser - Automated Assessment',pageCompression=1)
    body = ParagraphStyle('Body',fontName='AuditTimes',fontSize=10,leading=13,spaceAfter=6,alignment=TA_JUSTIFY)
    small = ParagraphStyle('Small',parent=body,fontSize=8.8,leading=11,spaceAfter=3,alignment=0)
    heading = ParagraphStyle('Heading',parent=body,fontName='AuditTimes-Bold',fontSize=11.2,leading=14,spaceBefore=9,spaceAfter=5,alignment=0)
    title = ParagraphStyle('Title',parent=heading,fontSize=17,leading=20,spaceBefore=0,spaceAfter=5)
    italic = ParagraphStyle('Italic',parent=small,fontName='AuditTimes-Italic')
    story = []
    def p(value,style=body): return Paragraph(text(value),style)
    def section(label): story.append(p(label,heading))
    def table(rows):
        data=[[p(key,small),p(value,small)] for key,value in rows]
        block=Table(data,colWidths=[139,364],hAlign='LEFT')
        block.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f2f3f4')),
            ('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#d5d9df')),('LEFTPADDING',(0,0),(-1,-1),7),
            ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
        story.append(block)
    kind=evidence['file_type']; model=evidence.get('model',{})
    story.extend([p('MEDIA AUTHENTICITY ASSESSMENT',title),p('Automated technical audit worksheet | ' + kind.upper(),italic)])
    section('1. Identification and conclusion')
    table([('Report identifier',evidence['report_id']),('Issued (UTC)',evidence['generated_at']),
           ('Source filename',evidence['filename'][:170]),('Media / size',f"{kind.title()} / {evidence['file_bytes']:,} bytes"),
           ('Source SHA-256',evidence['file_sha256']),('Model classification',evidence['prediction'] + ' - automated prediction; human review pending')])
    section('2. Detector identity and method')
    architecture = {'gend_clip_l14':'clip_vit_large_patch14', 'spectra_aasist3':'wav2vec2_xlsr_aasist3'}.get(model.get('arch'), model.get('arch'))
    table([('Architecture',architecture),('Checkpoint revision',model.get('revision')),
           ('Weights SHA-256',model.get('weights_sha256'))])
    story.append(Spacer(1,6));story.append(p(evidence['decision_method']))
    section('3. Measured evidence and analysis scope')
    table(list(evidence.get('metrics',{}).items()))
    if kind=='audio':
        coverage=evidence.get('coverage',{})
        story.append(p(f"Coverage: {coverage.get('window_count','not recorded')} speech windows; "
            f"{coverage.get('analyzed_seconds','not recorded')} seconds of unique audio assessed. "
            'The recording-level decision does not establish that every second is manipulated.'))
    elif kind=='video':
        indices=evidence.get('frame_indices',[])
        story.append(p('Analyzed source frame indices: ' + (', '.join(map(str,indices[:20])) or 'Not recorded') + '.'))
    story.append(p(evidence.get('scope'),small))
    story.append(PageBreak())
    story.append(p('FINDINGS, LIMITATIONS AND REVIEW',title))
    section('4. Interpretation of the result')
    prediction=evidence['prediction']
    story.append(p(f"The configured detector classified the submitted {kind} as {prediction}. "
        + ('This means its aggregated learned evidence met the configured synthetic/manipulated decision rule. '
           if prediction=='Fake' else 'This means its aggregated learned evidence did not meet the configured synthetic/manipulated decision rule. ')
        + 'This is a model prediction, not a verified finding of fraud, authorship, intent, identity or authenticity. '
        'No calibrated certainty percentage is assigned. Model fingerprints establish which software artifact was used; '
        'they do not validate its accuracy on this particular file.'))
    if kind=='audio' and evidence.get('spectrogram_png_base64'):
        section('5. Signal overview and acoustic interpretation')
        image=Image(io.BytesIO(base64.b64decode(evidence['spectrogram_png_base64'])),width=503,height=100)
        story.append(image)
        story.append(p('Spectrogram overview: time increases left to right; frequency increases bottom to top (0-8 kHz). '
            'Color shows relative spectral power across an 80 dB range. Uniformly sampled display windows are not a continuous '
            'forensic trace, a manipulation heatmap or the neural model\'s internal features.',small))
        story.append(p('RMS, peak amplitude and near-full-scale sample counts describe the decoded recording. They are not '
            'standalone authenticity tests. A causal abnormality in pitch, breathing, formants, emotional expression or background '
            'noise was not established. Window predictions are screening evidence, not verified manipulation timestamps.'))
    else:
        section('5. Visual evidence interpretation')
        story.append(p('The detector analyzes learned patterns in detected face regions. It does not prove that a particular '
            'pixel, facial feature, edge or expression caused the decision. No validated localization heatmap was generated. '
            + ('The soundtrack, unsampled frames and non-face edits were not assessed. A face-video classifier does not establish '
               'audio authenticity, lip-sync correctness or the absence of other edits.' if kind=='video' else
               'Undetected faces and regions outside the analyzed face crops are not covered. For animations or multi-page '
               'formats, the selected decoded image does not establish the authenticity of all frames or pages.')))
    section('6. Limitations and alternative explanations')
    story.append(p('False positives and false negatives remain possible on unfamiliar generators, speakers, faces, languages '
        'and capture conditions. Recompression, resizing, editing, noise and distribution shift can change the model output. '
        'A Real decision does not exclude a sophisticated fake; a Fake decision does not establish a specific fabrication '
        'technique. File metadata and a cryptographic hash alone do not prove original capture or chain of custody. '
        'This report is an automated screening record, not a certified forensic opinion or an assertion of compliance with an audit standard.'))
    section('7. Independent review and disposition')
    review=('Listen to the original recording and inspect pacing, breaths, word transitions, background continuity and pitch variation. '
            'Treat each observation as a review prompt, not proof. Compare with independently sourced genuine speech when available.'
            if kind=='audio' else 'Compare with the original capture and independent source material. Inspect editing history and provenance; '
            'review the original resolution and codec, and seek independent forensic examination when the finding is consequential.')
    story.append(p(review + ' Preserve the source file and this report together. Repeat analysis only with the model version and preprocessing '
        'recorded above, and document any discrepancy. No human observations or reviewer approval were supplied at generation time.'))
    table([('Reviewer / role','_______________________________________________'),('Date / reference','_______________________________________________'),
           ('Disposition / signature','Pending independent review / unsigned')])
    def page(canvas,doc):
        canvas.saveState();w,h=A4
        canvas.setFont('AuditTimes-Bold',9);canvas.drawString(46,h-32,'DEEPFAKE ANALYSER | TECHNICAL ASSESSMENT')
        canvas.setStrokeColor(colors.HexColor('#9ba5b3'));canvas.line(46,h-39,w-46,h-39)
        canvas.setFont('AuditTimes',8);canvas.drawString(46,30,evidence['report_id'] + ' | Automated; unsigned')
        canvas.drawRightString(w-46,30,f'Page {doc.page} of 2');canvas.restoreState()
    document.build(story,onFirstPage=page,onLaterPages=page)
    return output.getvalue()
