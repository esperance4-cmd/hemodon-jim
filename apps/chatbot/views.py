from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json

from .models import Conversation, Message
from .intents import get_intent, get_response


@login_required
def chatbot_view(request):
    """Page principale du chatbot"""
    conversations = Conversation.objects.filter(user=request.user, is_active=True)
    active_conversation = conversations.first()
    
    if not active_conversation:
        active_conversation = Conversation.objects.create(
            user=request.user,
            title="Nouvelle conversation"
        )
    
    context = {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': active_conversation.messages.all(),
    }
    return render(request, 'chatbot/chatbot.html', context)


@csrf_exempt
@login_required
def send_message(request):
    """Endpoint pour envoyer un message et recevoir une réponse"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        message_content = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message_content:
            return JsonResponse({'error': 'Message vide'}, status=400)
        
        # Récupérer ou créer la conversation
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        else:
            conversation = Conversation.objects.create(
                user=request.user,
                title=message_content[:50]
            )
        
        # Sauvegarder le message de l'utilisateur
        user_message = Message.objects.create(
            conversation=conversation,
            sender='user',
            content=message_content
        )
        
        # Générer la réponse du bot
        intent = get_intent(message_content)
        bot_response = get_response(intent)
        
        # Sauvegarder la réponse du bot
        bot_message = Message.objects.create(
            conversation=conversation,
            sender='bot',
            content=bot_response
        )
        
        # Mettre à jour le titre de la conversation si c'est la première
        if conversation.messages.count() <= 2:
            conversation.title = message_content[:50] + ('...' if len(message_content) > 50 else '')
            conversation.save()
        
        return JsonResponse({
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'created_at': user_message.created_at.strftime('%H:%M'),
            },
            'bot_message': {
                'id': bot_message.id,
                'content': bot_message.content,
                'created_at': bot_message.created_at.strftime('%H:%M'),
            },
            'conversation_id': conversation.id,
            'intent': intent,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_conversation(request, conversation_id):
    """Supprimer une conversation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.is_active = False
    conversation.save()
    
    return JsonResponse({'success': True})


@login_required
def get_conversations(request):
    """Récupérer la liste des conversations"""
    conversations = Conversation.objects.filter(user=request.user, is_active=True)
    data = {
        'conversations': [
            {
                'id': c.id,
                'title': c.title,
                'updated_at': c.updated_at.strftime('%d/%m/%Y %H:%M'),
                'message_count': c.messages.count(),
            }
            for c in conversations
        ]
    }
    return JsonResponse(data)