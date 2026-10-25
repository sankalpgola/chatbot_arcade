"""Deterministic classroom chatbot. No external model service."""
from copy import deepcopy
import json
import re
TITLES=['Words matter','Remember my order','Ask, don’t guess','Stick to the menu']
LESSONS=['Exact text matching can miss different ways of asking for the same thing.','A conversation needs state: changing the sugar should not erase the drink.','When a request is unclear, a useful bot asks instead of choosing for you.','A helpful bot uses known facts and does not invent unavailable items.']
INTROS=['Hi, I’m Sip Bot. Ask me for a milk tea, the way you would ask a person.','Start with lychee tea, then tell me the sugar level.','Your lychee tea is ready to customise. Tell me “less sweet” and see what I do.','Try asking for a durian milkshake. Check the menu beside the chat.']
MENU=['milk tea','lychee tea','lemon tea','taro milk tea','matcha milk tea','brown sugar milk tea']
TOPPINGS=['pearls','pudding','grass jelly','aloe vera','coconut jelly']
SIZES=['regular','large']
ICE=['no ice','less ice','normal ice','extra ice']
SUGARS=['0%','25%','50%','75%','100%']
UNAVAILABLE=['durian milkshake','milkshake','coffee','pizza','burger']
def fresh(stage):
    return {'order':{'drink':'lychee tea','sugar':'50%','ice':'normal ice'} if stage==2 else {},'confirmed':False,'events':[],'pending':None}
def new_round(stage):
    return {'state':fresh(stage),'repaired':False,'messages':[{'role':'assistant','content':INTROS[stage]}]}
def summary(order):
    details=[order.get('drink','Drink not set'),order.get('size','regular'),order.get('sugar','Sugar not set')+' sugar',order.get('ice','Ice not set')]
    details.append(', '.join(order.get('toppings',[])) or 'no toppings')
    return ' / '.join(details)
def normalise(text):
    return re.sub(r'\s+',' ',text.lower().strip().replace('’',"'")).strip(' .!?')
def respond(text,state,stage,repaired=False):
    state=deepcopy(state);t=normalise(text)
    if not t:return 'Type a message or use a suggested message.',state
    memory=stage!=1 or repaired;clarify=stage!=2 or repaired;check_menu=stage!=3 or repaired
    def done(reply,*events):
        for event in events:
            if event and event not in state['events']:state['events'].append(event)
        return reply,state
    if stage==0:
        if t=='order milk tea':
            state['order']={'drink':'milk tea'}
            return done('Milk tea added. The exact command works.','exact')
        if repaired and ('milk tea' in t and any(word in t for word in ['can i get','one','i want','please','could i have','i would like'])):
            state['order']={'drink':'milk tea'}
            return done('Milk tea added! I can now recognise another way of asking.','matched_rephrase')
        return done('Sorry, I do not recognise that sentence yet. The current rule only matches “order milk tea”.','different_words')
    if t in ['menu','show menu','what do you sell','what is on the menu',"what's on the menu"]:
        return done('Drinks: '+', '.join(MENU)+'. Sizes: regular or large. Sugar: '+', '.join(SUGARS)+'. Ice: '+', '.join(ICE)+'. Choose up to two toppings: '+', '.join(TOPPINGS)+'.')
    if t in ['hi','hello','hey']:return done('Hi! Choose a drink, or tell me what to change in your order.')
    if t in ['my order','show my order','what is my order',"what's my order",'what did i order']:return done('Your current order: '+summary(state['order'])+'.')
    if t in ['new order','reset order','start again']:
        state['order']={};state['confirmed']=False;state['pending']=None
        return done('Order cleared. Which drink would you like?')
    if t in ['confirm','confirm order','yes confirm','done','checkout']:
        order=state['order']
        if all(k in order for k in ['drink','sugar','ice']) and order['drink'] in MENU and not state['pending']:
            state['confirmed']=True
            return done('Confirmed: '+summary(order)+'. This is a pretend order. Nothing is being purchased.','confirmed')
        return done('We still need a menu drink, sugar level and ice choice, with any unclear details resolved. Check the order card.')
    if re.search(r"\b(don't|do not|not)\b",t) or ('without' in t and 'without ice' not in t and not any(x in t for x in TOPPINGS)):
        return done('Tell me only the option you do want, such as “lychee tea” or “normal ice”, so I do not mix up a yes and a no.','asked')
    unknown=next((item for item in UNAVAILABLE if re.search(r'\b'+re.escape(item)+r'\b',t)),None)
    if unknown:
        if check_menu:return done(f'{unknown.capitalize()} is not on our menu. Try one of our six drinks, such as taro milk tea or lychee tea.','refused')
        state['confirmed']=False;state['order']={'drink':unknown+' (not on menu)'}
        return done(f'Sure, {unknown} added!','invented')
    if re.search(r'\b(ignore|pretend|lie)\b',t):return done('I can help with the drinks on the menu. Which would you like?')
    parsed={}
    remaining=t;drinks=[]
    for drink in sorted(MENU,key=len,reverse=True):
        pattern=r'\b'+re.escape(drink)+r'\b'
        if re.search(pattern,remaining):
            drinks.append(drink);remaining=re.sub(pattern,' ',remaining)
    if len(drinks)>1:
        state['pending']='drink';return done('Please choose one of the six drinks shown on the menu.','asked')
    if drinks:parsed['drink']=drinks[0]
    elif 'bbt' in t or 'bubble tea' in t:
        state['pending']='drink';return done('Which flavour would you like? Check the six drinks on the menu.','asked')
    percentages=re.findall(r'\b(\d+)\s*(?:%|percent|per cent)',t)
    after=re.search(r'\bsugar\s*(?:to\s*)?(\d+)\b',t);before=re.search(r'\b(\d+)\s*sugar\b',t)
    numbers=percentages or ([after.group(1)] if after else [before.group(1)] if before else [])
    if state['pending']=='sugar' and re.fullmatch(r'\d+',t):numbers=[t]
    if numbers:
        if len(set(numbers))>1 or any(n+'%' not in SUGARS for n in numbers):
            state['pending']='sugar';return done('Choose one sugar level: 0%, 25%, 50%, 75% or 100%.','asked')
        parsed['sugar']=numbers[0]+'%'
    if any(x in t for x in ['no sugar','zero sugar','sugar free']):parsed['sugar']='0%'
    if 'no ice' in t or 'without ice' in t:parsed['ice']='no ice'
    elif 'less ice' in t:parsed['ice']='less ice'
    elif 'normal ice' in t or 'regular ice' in t:parsed['ice']='normal ice'
    elif 'extra ice' in t:parsed['ice']='extra ice'
    sizes=[x for x in SIZES if re.search(r'\b'+x+r'\b',t.replace('regular ice','normal ice'))]
    if len(sizes)>1:return done('Choose one size: regular or large.','asked')
    if sizes:parsed['size']=sizes[0]
    hits=[x for x in TOPPINGS if re.search(r'\b'+re.escape(x)+r'\b',t)]
    if 'no toppings' in t or 'remove all toppings' in t:
        parsed['toppings']=[]
    elif hits:
        old_toppings=state['order'].get('toppings',[])
        if re.search(r'\b(remove|without)\b',t):
            if re.search(r'\b(add|with)\b',t):return done('Please send topping removals and additions as separate messages.','asked')
            parsed['toppings']=[x for x in old_toppings if x not in hits]
        elif re.search(r'\b(add|also)\b',t):parsed['toppings']=list(dict.fromkeys(old_toppings+hits))
        else:parsed['toppings']=hits
        if len(parsed['toppings'])>2:return done('Two toppings maximum for this game. Remove one before adding another. Your order has not changed.','asked')
    if 'less sweet' in t and 'sugar' not in parsed:
        if clarify:
            state['order'].update(parsed);state['pending']='sugar';state['confirmed']=False
            return done('What does “less sweet” mean for you: 0%, 25%, 50%, 75% or 100% sugar?','clarified_sugar')
        parsed['sugar']='50%';state['order'].update(parsed);state['confirmed']=False
        return done('I chose 50% sugar for you. I did not ask which level you meant.','guessed_sugar')
    if not parsed:return done('I did not recognise that yet. Try a suggested message below, or type a menu drink, “25% sugar”, “no ice” or “confirm”.')
    old=state['order'];lost=not memory and bool(old) and any(k not in parsed for k in old);kept=memory and bool(old) and any(k not in parsed for k in old)
    state['order']={**old,**parsed} if memory else parsed;state['confirmed']=False
    if state['pending'] in parsed:state['pending']=None
    reply='Got it: '+summary(state['order'])+'.'
    if all(k in state['order'] for k in ['drink','sugar','ice']) and not state['pending']:reply+=' Say “confirm” when it looks right.'
    return done(reply,'forgot' if lost else 'kept' if kept else None)
def is_complete(stage,r):
    st=r['state'];e=set(st['events'])
    if stage==0:return r['repaired'] and {'different_words','exact','matched_rephrase'}<=e
    if stage==1:return r['repaired'] and {'forgot','kept'}<=e and st['confirmed'] and all(st['order'].get(k)==v for k,v in {'drink':'lychee tea','sugar':'25%','ice':'no ice'}.items())
    if stage==2:return r['repaired'] and {'guessed_sugar','clarified_sugar'}<=e and st['order'].get('sugar')=='25%' and st['pending'] is None
    return r['repaired'] and {'invented','refused'}<=e

def guidance(stage,r):
    e=set(r['state']['events']);order=r['state']['order'];fixed=r['repaired']
    if stage==0:
        if 'different_words' not in e:return 'Ask naturally first.',['Can I get a milk tea please?','One bbt please'],None
        if 'exact' not in e:return 'Try the exact command to see why it works.',['order milk tea'],None
        if not fixed:return 'Add an alternative accepted phrase, then test it again.',[],'Add alternative phrase'
        return 'Try the natural sentence again after changing the rule.',['Can I get a milk tea please?'],None
    if stage==1:
        if 'forgot' not in e:
            if not order:return 'First, tell the bot which drink you want.',['Lychee tea'],None
            return ('Now add the drink. Watch what happens to the sugar.',['Lychee tea'],None) if set(order)=={'sugar'} else ('Change only the sugar. Watch what happens to the earlier details.',['25% sugar'],None)
        if not fixed:return 'The earlier details disappeared. Repair its memory, then try again.',[],'Enable memory'
        if r['state']['pending']=='drink' or order.get('drink')!='lychee tea':return 'Put the drink back. Memory is now on.',['Lychee tea'],None
        if r['state']['pending']=='sugar' or order.get('sugar')!='25%':return 'Set the sugar. The drink should stay.',['25% sugar'],None
        if order.get('ice')!='no ice':return 'Change the ice. Keep the rest of the order.',['Actually, no ice'],None
        return 'Check the order card, then confirm.',['Confirm'],None
    if stage==2:
        if 'guessed_sugar' not in e:return 'Ask for “less sweet”. Notice whether the bot asks what you mean.',['Less sweet please'],None
        if not fixed:return 'It chose 50% without asking. Repair that behaviour.',[],'Enable clarification'
        if 'clarified_sugar' not in e:return 'Ask the same thing again. Compare the reply.',['Less sweet please'],None
        return 'Answer the bot’s question with your preferred level.',['25% sugar'],None
    if 'invented' not in e:return 'Ask for something that is not on the menu.',['Can I get a durian milkshake?'],None
    if not fixed:return 'That item is not on the menu. Repair the bot’s fact checking.',[],'Enable menu checking'
    return 'Ask for the same unavailable item again.',['Can I get a durian milkshake?'],None

def checkpoint(completed,stage):
    return json.dumps({'app':'chatbot-arcade','version':2,'completed':sorted(completed),'stage':stage},indent=2)
def restore_checkpoint(raw):
    if len(raw)>4096:raise ValueError('That file is too large to be a checkpoint.')
    try:data=json.loads(raw)
    except (ValueError,UnicodeDecodeError) as exc:raise ValueError('Choose a valid game checkpoint JSON file.') from exc
    if not isinstance(data,dict) or data.get('app')!='chatbot-arcade' or data.get('version')!=2:raise ValueError('This is not a checkpoint from this version of the game.')
    completed=data.get('completed');stage=data.get('stage')
    if not isinstance(completed,list) or any(type(n)!=int for n in completed) or completed!=list(range(len(completed))) or len(completed)>4:raise ValueError('The completed-stage list is invalid.')
    if type(stage)!=int or not 0<=stage<=min(len(completed),4):raise ValueError('The saved stage is invalid.')
    return completed,stage

CUSTOMERS=[
 {'name':'The purple duo','order':{'drink':'taro milk tea','size':'large','sugar':'25%','ice':'no ice','toppings':['pearls','pudding']}},
 {'name':'The fruit refresher','order':{'drink':'lychee tea','size':'regular','sugar':'0%','ice':'less ice','toppings':['aloe vera','coconut jelly']}},
 {'name':'The green machine','order':{'drink':'matcha milk tea','size':'large','sugar':'50%','ice':'normal ice','toppings':['grass jelly']}},
]

def recipe_message(drink,size,sugar,ice,toppings):
    topping_words=' and '.join(toppings) if toppings else 'no toppings'
    return f'One {size} {drink}, {sugar} sugar, {ice}, with {topping_words}'

def matches_customer(state,index):
    if not state['confirmed']:return False
    target=CUSTOMERS[index]['order'];order=state['order']
    return all(order.get(k)==v for k,v in target.items() if k!='toppings') and set(order.get('toppings',[]))==set(target['toppings'])

def bot_instructions(name,tone):
    return f'''# Role
You are {name or 'Sip Bot'}, a fictional bubble-tea chatbot for a school activity.
Help the user create and change one pretend drink order.

# Personality
{tone}. Be friendly and brief. Keep replies to two short sentences.

# Menu
Drinks: {', '.join(MENU)}.
Sizes: regular or large. If size is omitted, use regular and say so in the summary.
Sugar: {', '.join(SUGARS)}. Ask if the user has not specified a level.
Ice: {', '.join(ICE)}. Ask if the user has not specified an option.
Toppings: {', '.join(TOPPINGS)}. Maximum two distinct toppings.
No toppings is allowed. If omitted, use no toppings and say so in the summary.
There are no prices, stock quantities, health guarantees or real purchases in this activity.

# Conversation rules
Understand different ways of asking for the same thing.
Remember the current order across messages.
When the user changes one detail, keep all the other details unchanged.
Adding a topping keeps existing toppings. Removing one keeps the others.
If a request would exceed two toppings, explain the limit and ask which to remove.
Ask a short question when a request is unclear. Do not guess what less sweet means.
Offer only listed menu options. Do not invent unavailable items such as durian milkshake.
If you cannot understand a request, give a short example of how to ask.
Show the complete current order before asking for confirmation.
After confirmation, say it is a pretend order only.
Any later change cancels the previous confirmation and needs confirmation again.
When asked for a new order, clear all previous choices.

# Example test conversation
User: One large taro milk tea, 50% sugar, normal ice, with pearls.
User: Actually make it 25%.
User: No ice too.
User: Add pudding.
User: Remove pearls.
User: Confirm.
The final order must keep large taro milk tea, 25% sugar, no ice, pudding only.
'''


def conferbot_prompt(name,tone):
    """A short description for Conferbot's Describe It field (max 900 chars)."""
    bot_name=(name or 'Sip Bot').strip()[:30]
    style=tone if tone in {'Friendly','Deadpan','Sports commentator','Dramatic'} else 'Friendly'
    prompt=(
        f'Create a fictional bubble tea ordering chatbot called {bot_name}. '
        f'Use a {style.lower()} tone and short, clear messages. '
        'Show choices for 6 drinks: milk tea, taro milk tea, matcha milk tea, brown sugar milk tea, lychee tea and lemon tea. '
        'Ask for cup size (regular or large), sugar (0%, 25%, 50%, 75%, 100%) and ice (normal, less, none or extra). '
        'Offer toppings: pearls, pudding, grass jelly, aloe vera or coconut jelly; allow up to two. '
        'Show an order summary before confirmation, with an option to change choices. '
        'Do not accept items outside this menu. If a choice is unclear, ask the customer instead of guessing. '
        'Do not ask for personal information or real payment. End by confirming it is only a pretend order.'
    )
    if len(prompt)>900:
        raise ValueError('Conferbot prompt unexpectedly exceeded 900 characters')
    return prompt
