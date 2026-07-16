import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from translations import TRANSLATIONS

app = Flask(__name__)

# Translated subject lines for user confirmation auto-reply
USER_EMAIL_SUBJECTS = {
    'en': "We have received your inquiry - Geo Seasonal Exports",
    'es': "Hemos recibido su consulta - Geo Seasonal Exports",
    'de': "Wir haben Ihre Anfrage erhalten - Geo Seasonal Exports",
    'ar': "لقد تلقينا استفسارك - جيو سيزونال للصادرات",
    'zh': "我们已收到您的询盘 - Geo Seasonal Exports"
}

# Translated email body templates for user confirmation auto-reply
USER_EMAIL_BODIES = {
    'en': (
        "Hello {name},\n\n"
        "Thank you for reaching out to Geo Seasonal Exports! We have successfully received your inquiry request.\n\n"
        "Here are the details we received:\n"
        "- Product of Interest: {product}\n"
        "- Country of Import: {country}\n"
        "- Message:\n{message}\n\n"
        "Our team is currently reviewing your specifications and will get back to you shortly with custom quotes, shipping terms, and quality certificates.\n\n"
        "Best regards,\n"
        "Geo Seasonal Exports Team\n"
        "Corporate Office: Bengaluru, Karnataka, India\n"
        "Email: contact@geoseasonalexports.com\n"
        "Direct Line: +91 911 399 5083"
    ),
    'es': (
        "Hola {name},\n\n"
        "¡Gracias por contactar a Geo Seasonal Exports! Hemos recibido con éxito su solicitud de consulta.\n\n"
        "Aquí están los detalles que recibimos:\n"
        "- Producto de interés: {product}\n"
        "- País de importación: {country}\n"
        "- Mensaje:\n{message}\n\n"
        "Nuestro equipo está revisando actualmente sus especificaciones y se pondrá en contacto con usted en breve con cotizaciones personalizadas, términos de envío y certificados de calidad.\n\n"
        "Atentamente,\n"
        "El equipo de Geo Seasonal Exports\n"
        "Oficina Corporativa: Bengaluru, Karnataka, India\n"
        "Email: contact@geoseasonalexports.com\n"
        "Línea Directa: +91 911 399 5083"
    ),
    'de': (
        "Hallo {name},\n\n"
        "Vielen Dank, dass Sie sich an Geo Seasonal Exports gewandt haben! Wir haben Ihre Anfrage erfolgreich erhalten.\n\n"
        "Hier sind die Details, die wir erhalten haben:\n"
        "- Produkt von Interesse: {product}\n"
        "- Importland: {country}\n"
        "- Nachricht:\n{message}\n\n"
        "Unser Team prüft derzeit Ihre Angaben und wird sich in Kürze mit Ihnen in Verbindung setzen, um Ihnen individuelle Angebote, Versandbedingungen und Qualitätszertifikate zuzusenden.\n\n"
        "Mit freundlichen Grüßen,\n"
        "Ihr Geo Seasonal Exports Team\n"
        "Hauptsitz: Bengaluru, Karnataka, Indien\n"
        "E-Mail: contact@geoseasonalexports.com\n"
        "Telefon: +91 911 399 5083"
    ),
    'ar': (
        "مرحبًا {name}،\n\n"
        "شكرًا لتواصلك مع جيو سيزونال للصادرات! لقد تلقينا طلب استفسارك بنجاح.\n\n"
        "إليك التفاصيل التي تلقيناها:\n"
        "- المنتج المطلوب: {product}\n"
        "- بلد الاستيراد: {country}\n"
        "- الرسالة:\n{message}\n\n"
        "يقوم فريقنا حاليًا بمراجعة مواصفاتك وسيتواصل معك قريبًا لتقديم عروض أسعار مخصصة وشروط الشحن وشهادات الجودة.\n\n"
        "أطيب التحيات،\n"
        "فريق جيو سيزونال للصادرات\n"
        "المكتب الرئيسي: بنغالور، كارناتاكا، الهند\n"
        "البريد الإلكتروني: contact@geoseasonalexports.com\n"
        "الهاتف المباشر: +91 911 399 5083"
    ),
    'zh': (
        "您好 {name}，\n\n"
        "感谢您联系 Geo Seasonal Exports！我们已成功收到您的询盘请求。\n\n"
        "以下是我们收到的信息明细：\n"
        "- 感兴趣的产品：{product}\n"
        "- 进口国家：{country}\n"
        "- 详细信息：\n{message}\n\n"
        "我们的团队目前正在评估您的需求规格，并会尽快与您联系，提供定制报价、出运条款及质量证书。\n\n"
        "顺祝商祺，\n"
        "Geo Seasonal Exports 团队\n"
        "公司总部：印度卡纳塔克邦班加罗尔\n"
        "电子邮件：contact@geoseasonalexports.com\n"
        "热线电话：+91 911 399 5083"
    )
}

def send_email(subject, body, to_email):
    smtp_host = os.environ.get('SMTP_HOST', 'mail.spacemail.com')
    smtp_port = os.environ.get('SMTP_PORT', '465')
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    smtp_use_ssl = os.environ.get('SMTP_USE_SSL', 'True').lower() in ('true', '1', 'yes')

    # Local development logging fallback if environment variables are missing
    if not smtp_username or not smtp_password:
        print("\n=== [DEVELOPMENT MODE: SMTP NOT CONFIGURED] ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("================================================\n")
        return True

    # Construct standard email
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # SSL Port (465) vs. TLS/STARTTLS Port (587/others)
    if smtp_use_ssl or smtp_port == '465':
        server = smtplib.SMTP_SSL(smtp_host, int(smtp_port), timeout=10)
    else:
        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        server.starttls()
    
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, to_email, msg.as_string())
    server.quit()
    return True

@app.route("/set-lang/<lang>")
def set_language(lang):
    referrer = request.referrer or url_for('home')
    response = make_response(redirect(referrer))
    if lang in TRANSLATIONS:
        response.set_cookie('lang', lang, max_age=30*24*60*60)
    return response

@app.context_processor
def inject_translate():
    lang = request.cookies.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    def translate(key):
        return TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, key))
    return dict(t=translate, current_lang=lang)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit-inquiry", methods=["POST"])
def submit_inquiry():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    country = request.form.get("country", "").strip()
    product = request.form.get("product", "").strip()
    message = request.form.get("message", "").strip()

    # Basic server-side validation
    if not all([name, email, country, product, message]):
        return jsonify({"message": "Please fill in all required fields."}), 400

    # Detect current browser/user language
    lang = request.cookies.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'

    # Admin notification settings
    admin_receiver = os.environ.get('CONTACT_RECEIVER_EMAIL') or os.environ.get('SMTP_USERNAME', 'contact@geoseasonalexports.com')
    admin_subject = f"New Inquiry Request: {product} from {name} ({country})"
    admin_body = (
        f"New Inquiry Request Received:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Country: {country}\n"
        f"Product of Interest: {product}\n\n"
        f"Message:\n{message}\n"
    )

    # User confirmation settings
    user_subject = USER_EMAIL_SUBJECTS.get(lang, USER_EMAIL_SUBJECTS['en'])
    user_body = USER_EMAIL_BODIES.get(lang, USER_EMAIL_BODIES['en']).format(
        name=name,
        product=product,
        country=country,
        message=message
    )

    try:
        # 1. Send inquiry notification to admin
        send_email(admin_subject, admin_body, admin_receiver)
        
        # 2. Send automated confirmation back to the user
        send_email(user_subject, user_body, email)
        
        success_msg = TRANSLATIONS[lang].get('Inquiry Success')
        return jsonify({"message": success_msg}), 200
    except Exception as e:
        print(f"Failed to process inquiry request email: {str(e)}")
        error_msg = TRANSLATIONS[lang].get('Inquiry Error')
        return jsonify({"message": error_msg}), 500

if __name__ == "__main__":
    app.run(debug=True)