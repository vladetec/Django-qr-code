import qrcode
from datetime import timedelta
from ninja import Router, Schema
from .models import Links, Clicks
from .schemas import ShortenUrlIn, UpdateLinkSchema, StatisticsResponse
from django.shortcuts import get_object_or_404, redirect
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings

shortener_router = Router()

@shortener_router.post("/shorten", response={200: ShortenUrlIn, 409: dict})
def shorten_url(request, shorten_url_in: ShortenUrlIn):
    data = shorten_url_in.to_model_data()
    token = data.get("token")
    
    if token and Links.objects.filter(token=token).exists():
        return 409, {"error": "Token já existe, use outro!"}
    
    link = Links(**data)
    link.save()
    return 200, ShortenUrlIn.from_model(link)

@shortener_router.get("/{token}", response={200: None, 404: dict})
def redirect_link(request, token: str):
    link = get_object_or_404(Links, token=token, activate=True)
    
    if link.expired():
        return 404, {"error": "Link expirado!"}
    
    uniques_clicks = Clicks.objects.filter(link=link).values('ip').distinct().count()
    if link.max_unique_cliques and uniques_clicks >= link.max_unique_cliques:
        return 404, {"error": "Link expirado"}
    
    click = Clicks(
        link=link,
        ip=request.META.get('REMOTE_ADDR')
    )
    click.save()
    return redirect(link.redirect_link)

@shortener_router.put('/{link_id}/', response={200: UpdateLinkSchema, 409: dict})
def update_link(request, link_id: int, link_schema: UpdateLinkSchema):
    link = get_object_or_404(Links, id=link_id)
    
    if link_schema.token and Links.objects.filter(token=link_schema.token).exclude(id=link_id).exists():
        return 409, {"error": "Token já existe, use outro!"}
    
    data = link_schema.dict(exclude_none=True)
    if 'expiration_time' in data:
        data['expiration_time'] = timedelta(minutes=data['expiration_time'])
    
    for key, value in data.items():
        setattr(link, key, value)
    
    link.save()
    return 200, UpdateLinkSchema.from_model(link)

@shortener_router.get("/statistics/{int:link_id}/", response={200: StatisticsResponse, 404: dict})
def statistics(request, link_id: int):
    try:
        link = get_object_or_404(Links, id=link_id)
        
        clicks = Clicks.objects.filter(link=link)
        uniques_clicks = clicks.values('ip').distinct().count()
        total_clicks = clicks.count()
        
        # Agrupa clicks por dia
        daily_clicks = {}
        for click in clicks:
            date = click.created_at.strftime('%Y-%m-%d')
            daily_clicks[date] = daily_clicks.get(date, 0) + 1
        
        return 200, {
            'uniques_clicks': uniques_clicks,
            'total_clicks': total_clicks,
            'daily_clicks': daily_clicks
        }
        
    except Links.DoesNotExist:
        return 404, {"error": "Link não encontrado"}

@shortener_router.get('/qrcode/{int:link_id}', response={200: None, 404: dict})
def get_qrcode(request, link_id: int):
    try:
        link = get_object_or_404(Links, id=link_id)
        
        # Gera URL completa do link
        url = f"{settings.SITE_URL}/{link.token}"
        
        # Cria QR Code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Gera imagem
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva imagem em buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        # Retorna resposta HTTP com imagem
        response = HttpResponse(buffer.getvalue(), content_type="image/png")
        response['Content-Disposition'] = f'inline; filename="qr-{link.token}.png"'
        
        return response
        
    except Links.DoesNotExist:
        return 404, {"error": "Link não encontrado"}