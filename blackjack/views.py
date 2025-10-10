import random
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# ---- Константы ----
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# ---- Хелперы ----

def new_deck():
    """Создаёт и тасует новую колоду"""
    deck = [f"{r}{s}" for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def card_value(card: str) -> int:
    """Возвращает числовое значение карты"""
    rank = card[:-1]
    if rank in ['J', 'Q', 'K']:
        return 10
    if rank == 'A':
        return 11
    return int(rank)


def hand_value(hand):
    """Считает очки руки (учитывает тузы как 11 или 1)"""
    total = 0
    aces = 0
    for c in hand:
        v = card_value(c)
        total += v
        if c[:-1] == 'A':
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def serialize_state(session):
    """Формирует состояние для фронтенда"""
    reveal = session.get('reveal_dealer', False)
    dealer_hand = session.get('dealer_hand', [])
    dealer_display = dealer_hand if reveal else [dealer_hand[0], '🂠'] if dealer_hand else []

    return {
        'player_hand': session.get('player_hand', []),
        'dealer_hand': dealer_display,
        'player_value': hand_value(session.get('player_hand', [])),
        'dealer_value': hand_value(session.get('dealer_hand', [])) if reveal else None,
        'status': session.get('status', 'playing'),
        'message': session.get('message', ''),
    }

# ---- Views ----

@login_required
def blackjack_page(request):
    """Страница игры"""
    return render(request, 'blackjack/blackjack.html')


@require_POST
@login_required
def blackjack_start(request):
    """Начать новую игру"""
    deck = new_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    request.session['deck'] = deck
    request.session['player_hand'] = player_hand
    request.session['dealer_hand'] = dealer_hand
    request.session['status'] = 'playing'
    request.session['message'] = ''
    request.session['reveal_dealer'] = False

    pv = hand_value(player_hand)
    dv = hand_value(dealer_hand)

    if pv == 21 and dv == 21:
        request.session.update({
            'status': 'push',
            'reveal_dealer': True,
            'message': 'Ничья — у обоих блэкджек.'
        })
    elif pv == 21:
        request.session.update({
            'status': 'player_win',
            'reveal_dealer': True,
            'message': 'Блэкджек! Вы выиграли 🎉'
        })
    elif dv == 21:
        request.session.update({
            'status': 'dealer_win',
            'reveal_dealer': True,
            'message': 'Дилер получил блэкджек. Вы проиграли 😞'
        })

    request.session.modified = True
    return JsonResponse(serialize_state(request.session))


@require_POST
@login_required
def blackjack_hit(request):
    """Игрок берёт карту"""
    if request.session.get('status') != 'playing':
        return JsonResponse(serialize_state(request.session))

    deck = request.session.get('deck', [])
    player_hand = request.session.get('player_hand', [])

    if not deck:
        deck = new_deck()

    player_hand.append(deck.pop())

    request.session['deck'] = deck
    request.session['player_hand'] = player_hand

    pv = hand_value(player_hand)
    if pv > 21:
        request.session.update({
            'status': 'player_bust',
            'reveal_dealer': True,
            'message': 'Вы перебрали! 😵 Проигрыш.'
        })

    request.session.modified = True
    return JsonResponse(serialize_state(request.session))


@require_POST
@login_required
def blackjack_stand(request):
    """Игрок останавливается — дилер добирает карты"""
    if request.session.get('status') != 'playing':
        return JsonResponse(serialize_state(request.session))

    deck = request.session.get('deck', [])
    dealer_hand = request.session.get('dealer_hand', [])
    player_hand = request.session.get('player_hand', [])

    request.session['reveal_dealer'] = True

    while hand_value(dealer_hand) < 17:
        if not deck:
            deck = new_deck()
        dealer_hand.append(deck.pop())

    request.session['deck'] = deck
    request.session['dealer_hand'] = dealer_hand

    pv = hand_value(player_hand)
    dv = hand_value(dealer_hand)

    if dv > 21:
        request.session.update({
            'status': 'dealer_bust',
            'message': 'Дилер перебрал! Вы выиграли 🎉'
        })
    elif pv > dv:
        request.session.update({
            'status': 'player_win',
            'message': 'Вы выиграли! 💰'
        })
    elif pv < dv:
        request.session.update({
            'status': 'dealer_win',
            'message': 'Дилер победил 😞'
        })
    else:
        request.session.update({
            'status': 'push',
            'message': 'Ничья 🤝'
        })

    request.session.modified = True
    return JsonResponse(serialize_state(request.session))
