import smtplib
from email.message import EmailMessage


def enviarEmail(destino, code, header, body, support, footer, titulo, asunto):
    
    msg = EmailMessage()
    msg['Subject'] = titulo
    msg['From'] = "notificacion@suport.com.do"
    msg['To'] = destino
    
    msg.set_content(asunto)
    
    msg.add_alternative(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap" rel="stylesheet">
    </head>
    <body style="background-color:#F9F9F9; font-family: 'Poppins', sans-serif; text-align: center;">
        <div class="cuerpo" style="background-color:#FFFFFF; padding:2em;">
            <h1 style="text-align: center;">{header}</h1>
            <h3 style="text-align: center;">{titulo}</h3>
            <h1style="text-align: center;">{body}</h1>
            <h2 style="text-align: center; margin=1rem; color:#006AAB">{code}</h2>
            
            <p style="text-align: center;">{support}</p>
            
            <h6 style="text-align: center;">{footer}</h6>
        </div>
    </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP_SSL('mail.suport.com.do', 465) as smtp:
        smtp.login('notificacion@suport.com.do', "r%bg$&El$gR,")
        smtp.send_message(msg)
