import qrcode, pyqrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask

from qrcode.image.styles.moduledrawers import *
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from .models import Qrcode, QrcodeLimit
from django.contrib.auth.decorators import login_required
import os

from PIL import Image
from datetime import datetime
from datetime import timedelta
from django.utils.timezone import now


def render_free(request):
    qr_image_url = None
    error_message = None  # Adicionamos uma variável para o erro
    
    # Excluímos códigos QR antigos e gratuitos
    Qrcode.objects.filter(created_at__lt=now() - timedelta(days=180), free=True).delete()
    
    user_qr = Qrcode.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    
    if request.method == "POST":
        if user_qr:  # Se o usuário já tiver um código QR
            error_message = "Você já criou um QR-code. Exclua o antigo para criar um novo."
        else:
            name = request.POST.get("name")
            link = request.POST.get("link")
            
            if not name or not link:
                return render(request, "free.html", {"error": "Preencha todos os campos.", "footer": True})
            
            print(f"Geração de QR-Code para: {link}")
            
            try:
                username = request.user.username if request.user.is_authenticated else 'anonymous'
                user_qr_folder = os.path.join("media", username)
                
                if not os.path.exists(user_qr_folder):
                    os.makedirs(user_qr_folder)
                    print(f"Pasta criada: {user_qr_folder}")
                
                qr = qrcode.make(link)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                
                filename = f"{name}.png"
                file_path = os.path.join(user_qr_folder, filename)
                
                with open(file_path, "wb") as f:
                    f.write(buffer.getvalue())
                
                if request.user.is_authenticated:
                    qr_code = Qrcode(name=name, link=link, user=request.user)
                    qr_code.image.name = f"{username}/{filename}"
                    qr_code.save()
                
                qr_image_url = f"/media/{username}/{filename}"
                print(f"QR-Code Salvo: {qr_image_url}")
            
            except Exception as e:
                print(f"Erro ao criar QR-Code: {e}")
                error_message = "Ocorreu um erro ao gerar o QR-Code."
            redirect('my_qrcodes')
    
    return render(request, "free.html", {"qr_image_url": qr_image_url, "error": error_message, "footer": True})

    




# @login_required - Mostra esta página somente se o usuário estiver logado
# Caso contrário, login_url redireciona para a página de login.
# E após o registro bem-sucedido, redireciona para nossa página de pacotes
# Ou seja, para a página que o usuário queria visitar antes do login
@login_required(login_url='login')
def render_standard(request):
    qr_image_url = None  
    error_message = None
    Qrcode.objects.filter(created_at__lt=now() - timedelta(days=365), standard=True).delete()

    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link")
        size = request.POST.get("size")
        color = request.POST.get("color")
        back_color = request.POST.get("back-color")

        if not name or not link or not size or not color:
            return render(request, "standard.html", {"error": "Preencha todos os campos."})
        
        qrcode_limit, created = QrcodeLimit.objects.get_or_create(user=request.user)
        # # Limite inicial
        user_qr_limit = qrcode_limit.limit_standard
        # # Número de QR-Code
        user_qr_count = Qrcode.objects.filter(user=request.user).count()
        print(user_qr_count)

    
        if user_qr_count >= user_qr_limit:
            error_message = f"Você já criou {user_qr_limit} Qr-Code. Exclua o antigo para criar um novo."
            print(error_message)
            return render(request, "standard.html", {"qr_image_url": qr_image_url,"footer": True, 'error': error_message})

        try:
        
            size = int(size)  

            username = request.user.username
            qr_folder = os.path.join("media", username)
            

            if not os.path.exists(qr_folder):
                os.makedirs(qr_folder)

            qr_code = Qrcode(name=name, link=link, user=request.user)

            
            qr = qrcode.QRCode(
                version=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,  
                border=2,
            )
            qr.add_data(link)
            qr.make(fit=True)

            
            img = qr.make_image(fill_color=color, back_color= back_color)

            
            img = img.resize((size, size), Image.NEAREST)

            
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            filename = f"{name}_{datetime.now().timestamp()}.png"  
            file_path = os.path.join(qr_folder, filename)
            

            with open(file_path, "wb") as f:
                f.write(buffer.getvalue())

            qr_code.image.name = f"{username}/{filename}"
            qr_code.save()

            qr_image_url = f"/media/{username}/{filename}"
            

        except Exception as e:
            print(e)
        

    return render(request, "standard.html", {"qr_image_url": qr_image_url,"footer": True})


# Função para converter formato hexadecimal para rgb. 
# Necessário para que o usuário possa inserir um valor hexadecimal
def hex_to_rgb(hex_format):
    # Remova "#" para evitar o erro 'literal inválido para int() com base 16: '#f''
    hex_format = hex_format.lstrip('#') 
    return tuple(int(hex_format[i:i+2], 16) for i in (0, 2, 4))


@login_required(login_url='login')
def render_pro(request):
    qr_image_url = None 
    error_message = None 
    Qrcode.objects.filter(created_at__lt=now() - timedelta(days=730), pro=True).delete()

    if request.method == "POST":
        name = request.POST.get("name")
        link = request.POST.get("link")
        size = request.POST.get("size")
        color = hex_to_rgb(request.POST.get("color"))
        back_color = hex_to_rgb(request.POST.get("back_color"))
        pattern = request.POST.get("pattern")
        logo = request.FILES.get("logo")
        # eye_frame = request.POST.get("eye-frame")

        if not name or not link or not size or not color:
            return render(request, "standard.html", {"error": "Preencha todos os campos."})
        
        qrcode_limit, created = QrcodeLimit.objects.get_or_create(user=request.user)
        # # Limite inicial
        user_qr_limit = qrcode_limit.limit_pro
        # # Número do QR-Code
        user_qr_count = Qrcode.objects.filter(user=request.user).count()
        print(user_qr_count)

    
        if user_qr_count >= user_qr_limit:
            error_message = f"Você já criou {user_qr_limit} QR-Code. Exclua o antigo para criar um novo."
            print(error_message)
            return render(request, "pro.html", {"qr_image_url": qr_image_url,"footer": True, 'error': error_message})     

        try:
        
            size = int(size)  

            username = request.user.username
            user_qr_folder = os.path.join("media", username)


            if not os.path.exists(user_qr_folder):
                os.makedirs(user_qr_folder)

            qr_code = Qrcode(name=name, link=link, user=request.user)


        
           
            pattern_modules = {
                "default": SquareModuleDrawer(),
                "squares": GappedSquareModuleDrawer(),
                "dots": CircleModuleDrawer(),
                "rounded": RoundedModuleDrawer(),
                "vertical_lines": VerticalBarsDrawer(),
                "horizontal_lines": HorizontalBarsDrawer(),
            }

            #  Defina um modelo padrão
            module_drawer = pattern_modules.get(pattern, SquareModuleDrawer())


            qr = qrcode.QRCode(
                version=5,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,  
                border=4,
            )


            qr.add_data(link)
            qr.make(fit=True)

 
            img = qr.make_image(
                image_factory= StyledPilImage, 
                color_mask = SolidFillColorMask(back_color=back_color, front_color=color),
                module_drawer = module_drawer, 
            )


            img = img.resize((size, size), Image.NEAREST)

            
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            filename = f"{name}_{datetime.now().timestamp()}.png"  
            file_path = os.path.join(user_qr_folder, filename)

            with open(file_path, "wb") as f:
                f.write(buffer.getvalue())

            qr_code.image.name = f"{username}/{filename}"
            qr_code.save()

            qr_image_url = f"/media/{username}/{filename}"


             # Adicionamos um logotipo se o usuário o adicionar
            if logo:
                #
                width, height = img.size
                # Abra a imagem do logotipo
                logo_img = Image.open(logo)
                # Converter para o formato RGBA para que, se houver um fundo na imagem do logotipo,
                #torne transparente
                logo_img = logo_img.convert("RGBA")
                # Especifique o tamanho do logotipo do Qr-Code
                logo_size = 40
                # Calculamos o centro do código QR e do logotipo horizontalmente e verticalmente
                xmin = ymin = int((width / 2) - (logo_size / 2))
                xmax = ymax = int((height / 2) + (logo_size / 2))
                # Dimensione o logotipo
                logo_img = logo_img.resize((xmax - xmin, ymax - ymin))
                # Inserindo o logotipo no Qr-Code
                img.paste(logo_img, (xmin, ymin, xmax, ymax), mask = logo_img)
                img.save(file_path, format="PNG")

            
            


        except Exception as e:
            print(e)
       


    return render(request, 'pro.html', {"qr_image_url": qr_image_url, 'footer': True, 'error': error_message})