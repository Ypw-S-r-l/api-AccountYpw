import smtplib
from email.message import EmailMessage

def enviarEmail(destino, code):

    msg = EmailMessage()
    msg['Subject'] = 'Recuperación de contraseña - YPW.SRL'
    msg['From'] = "app@ypw.com.do"
    msg['To'] = destino

    msg.set_content('This is a plain text email')

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
            <img style="display: block; margin-left: auto; margin-right: auto;" src="https://realtyhs.s3.us-east-2.amazonaws.com/wp-content/uploads/2021/12/10005101/descarga.png" alt="" width="189" height="189" />

            <h3 style="text-align: center;">Recuperación de contraseñas</h3>
            <p style="text-align: center;">Recientemente ha solicitado restablecer la contraseña de la cuenta asociada con esta dirección de correo electrónico.</p>
            <h2 style="text-align: center; margin=1rem; color:#006AAB">{code}</h2>
            <p style="text-align: center;">Introduzca este código en página de restablecimiento de contraseñas.</p>
            <p style="text-align: center;">¿No ha realizado esta solicitud? <a href="https://ypw.com.do/#about" target="_blank" rel="noopener" data-saferedirecturl="https://www.google.com/url?q=https://identity.cisco.com/ui/tenants/global/v1.0/about-ui/contact-us?navStateId%3D5da73358-94bd-4929-926d-72968cf6a650&amp;source=gmail&amp;ust=1655580079000000&amp;usg=AOvVaw1M_l5UPChy57e1SK6v67CC">Póngase en contacto con el servicio de asistencia en YPW.SRL</a>.</p>
            <h6 style="text-align: center;">2022 © YPW S.R.L</h6>
        </div>
    </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP_SSL('mail.privateemail.com', 465) as smtp:
        smtp.login('app@ypw.com.do', 'Y@lfry@@7991')
        smtp.send_message(msg)