from django.shortcuts import render
from bus_signals.models import Bus
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging
import openai
# Create your views here.
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = '__all__'

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.bus.all()
    serializer_class = BusSerializer


@csrf_exempt
def ask_ai(request):
    if request.method == "POST":
        question = request.POST.get("question")

        try:
            # Configura la clave de API
            openai.api_key = settings.OPENAI_API_KEY

            # Usa 'ChatCompletion.create' con el modelo actualizado 'gpt-3.5-turbo'
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                max_tokens=100
            )

            # Extrae la respuesta
            answer = response.choices[0].message['content'].strip()
        except openai.error.OpenAIError as e:
            logging.error(f"Error al conectar con la API de OpenAI: {e}")
            answer = f"Error al conectar con la API de OpenAI: {str(e)}"

        return JsonResponse({"answer": answer})

    return JsonResponse({"error": "Método no permitido"}, status=405)
