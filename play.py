"""Free play and the end-of-game reveal. No external calls."""
import random
from html import escape
import streamlit as st
from engine import MENU, TOPPINGS, SIZES, SUGARS, ICE, CUSTOMERS, fresh, respond, summary, recipe_message, matches_customer, bot_instructions

TONES=['Friendly','Deadpan','Sports commentator','Dramatic']
COLORS={'milk tea':'#C49A6C','lychee tea':'#E8A6AD','lemon tea':'#EDCF68','taro milk tea':'#AD8BC9','matcha milk tea':'#8BAC73','brown sugar milk tea':'#9F714D'}

def render_menu():
    with st.expander('Explore the BBT menu: 6 flavours + sizes, sugar, ice and toppings',expanded=True):
        a,b=st.columns(2)
        with a:
            st.markdown('**Choose a flavour**')
            st.write('Milk tea · Taro milk tea · Matcha milk tea\n\nBrown sugar milk tea · Lychee tea · Lemon tea')
            st.markdown('**Choose a size**');st.write('Regular or large')
        with b:
            st.markdown('**Make it yours**')
            st.write('Sugar: '+', '.join(SUGARS))
            st.write('Ice: '+', '.join(ICE))
            st.write('Up to two toppings: '+', '.join(TOPPINGS)+'. Or no toppings.')
        st.caption('From stage 2, try “add pearls”, “remove pearls”, “make it large” or “extra ice”. Finish the stages to unlock the full drinks counter.')

def cup(order):
    color=COLORS.get(order.get('drink'),'#E4EAE6')
    toppings=order.get('toppings',[])
    shapes=[]
    for i,name in enumerate(toppings):
        for j in range(6):
            x=73+j*17;y=189+i*14
            if name=='pearls':shapes.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#45362C"/>')
            else:
                fill={'pudding':'#F6DA74','grass jelly':'#645A50','aloe vera':'#D1E5BB','coconut jelly':'#FFF6D9'}[name]
                shapes.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" rx="2" fill="{fill}"/>')
    ice=''
    if order.get('ice') not in [None,'no ice']:
        count={'less ice':2,'normal ice':4,'extra ice':6}[order['ice']]
        ice=''.join(f'<rect x="{63+i*19}" y="85" width="13" height="14" rx="3" fill="#FFFFFF" opacity=".65"/>' for i in range(count))
    height='240' if order.get('size')=='large' else '210'
    label=escape('Cup preview: '+summary(order),quote=True)
    svg=f'''<div style="text-align:center"><svg role="img" aria-label="{label}" width="210" height="{height}" viewBox="0 0 250 260"><path d="M153 15 L135 112" stroke="#397357" stroke-width="10" stroke-linecap="round"/><path d="M48 65 L65 225 Q125 246 185 225 L202 65 Z" fill="{color}" stroke="#345444" stroke-width="3"/>{ice}{''.join(shapes)}<rect x="44" y="58" width="162" height="16" rx="7" fill="#E3EEE5" stroke="#345444" stroke-width="3"/><path d="M70 86 L80 166" stroke="white" stroke-width="5" opacity=".3" stroke-linecap="round"/></svg></div>'''
    st.markdown(svg,unsafe_allow_html=True)
    st.caption('Illustrated preview. The order card lists your exact choices.')

def _new_counter():
    return {'state':fresh(4),'messages':[{'role':'assistant','content':'The counter is open! Build a drink, send the recipe, then change it through chat.'}]}

def counter_send(text):
    s=st.session_state;r=s.counter
    reply,state=respond(text[:300],r['state'],4,True)
    tone=s.get('bot_tone','Friendly')
    if tone=='Deadpan':reply+=' That is the situation.'
    elif tone=='Sports commentator':reply='From the drinks counter: '+reply
    elif tone=='Dramatic':reply='The next chapter of your drink: '+reply
    r['state']=state
    r['messages']=(r['messages']+[{'role':'user','content':text[:300]},{'role':'assistant','content':reply}])[-30:]
    if matches_customer(state,s.customer) and s.customer not in s.served:s.served.append(s.customer)

def send_builder():
    s=st.session_state
    counter_send(recipe_message(s.flavour,s.size,s.sugar,s.ice,s.toppings))

def surprise():
    counter_send(recipe_message(random.choice(MENU),random.choice(SIZES),random.choice(SUGARS),random.choice(ICE),random.sample(TOPPINGS,random.randint(0,2))))

def next_customer():
    s=st.session_state;s.customer=(s.customer+1)%len(CUSTOMERS);s.counter=_new_counter()

def counter_draft():counter_send(st.session_state.get('counter_draft','')) if st.session_state.get('counter_draft','').strip() else None

def render_freeplay():
    s=st.session_state
    for key,val in {'counter':_new_counter(),'served':[],'customer':0,'reveal_next':False}.items():
        if key not in s:s[key]=val
    st.subheader('The drinks counter is yours')
    st.write('Invent a combination, change your mind, or take a customer challenge. All the repairs are on. Try a topping swap and see what the bot remembers.')
    render_menu()
    builder,preview=st.columns([1.5,1],gap='large')
    with builder:
        with st.form('recipe_builder'):
            st.markdown('**Build a drink**')
            st.selectbox('Flavour',MENU,key='flavour')
            c1,c2=st.columns(2)
            with c1:
                st.selectbox('Cup size',SIZES,key='size')
                st.selectbox('Sugar',SUGARS,index=2,key='sugar')
            with c2:st.selectbox('Ice',ICE,index=2,key='ice')
            st.multiselect('Toppings: pick up to two',TOPPINGS,max_selections=2,key='toppings')
            st.form_submit_button('Send my recipe to the bot',type='primary',on_click=send_builder,width='stretch')
        st.button('Surprise me with a drink',on_click=surprise,width='stretch')
        st.caption('The builder and Surprise me send a chat message. The order card changes after the bot processes it.')
    with preview:
        with st.container(border=True):
            st.markdown('**Your current drink**');cup(s.counter['state']['order'])
            st.write(summary(s.counter['state']['order']))
            st.caption('Confirmed' if s.counter['state']['confirmed'] else 'Still customising. Send Confirm when ready.')
    with st.expander('Optional: serve a customer',expanded=True):
        customer=CUSTOMERS[s.customer]
        st.markdown('**Customer '+str(s.customer+1)+': '+customer['name']+'**')
        st.write(summary(customer['order']))
        st.caption('Build this exact order and confirm it. '+str(len(s.served))+'/3 customer stamps earned. No time limit.')
        if s.customer in s.served:st.success('Customer served. Nice memory work!')
        st.button('Next customer',on_click=next_customer)
        st.caption('Next customer starts a fresh counter chat. Earned customer stamps are kept.')
    st.markdown('**Give your bot some character**')
    n,t=st.columns(2)
    with n:st.text_input('Bot name',value='Sip Bot',max_chars=30,key='bot_name')
    with t:st.selectbox('Reply style',TONES,key='bot_tone')
    st.caption('Style changes apply to the next reply. The facts and order rules stay the same.')
    st.markdown('**Chat at the counter**')
    for message in s.counter['messages'][-2:]:
        with st.chat_message(message['role']):
            if message['role']=='assistant':st.caption(s.bot_name or 'Sip Bot')
            st.write(message['content'])
    if len(s.counter['messages'])>2:
        with st.expander('Earlier counter messages'):
            for message in s.counter['messages'][:-2]:st.write(('Bot: ' if message['role']=='assistant' else 'You: ')+message['content'])
    quick=['Make it large','Add pearls','Remove pearls','No toppings','Actually, no ice','25% sugar','My order','Confirm','New order']
    for row in range(3):
        cols=st.columns(3)
        for offset,col in enumerate(cols):
            text=quick[row*3+offset]
            with col:st.button('Send: '+text,on_click=counter_send,args=(text,),key='quick_'+text,width='stretch')
    with st.form('counter_compose',clear_on_submit=True):
        st.text_input('Write your own counter message',key='counter_draft',max_chars=300,placeholder='Try: add pudding, or change to taro milk tea')
        st.form_submit_button('Send to counter',on_click=counter_draft,width='stretch')
    st.divider()
    st.subheader('Ready to make a chatbot of your own?')
    if st.button('Reveal the next step',type='primary'):s.reveal_next=True
    if s.reveal_next:
        st.markdown('### Meet Voiceflow')
        st.write('You have been playing with a rule-based chatbot. Voiceflow lets you create an AI chatbot that responds to more varied messages. Take the same menu, memory and clarification rules with you.')
        prompt=bot_instructions(s.bot_name or 'Sip Bot',s.bot_tone)
        st.write('**For later:** use the copy icon in the top-right of the instructions box, or download the text file. Your chosen bot name and reply style are included.')
        st.code(prompt,language=None)
        st.download_button('Download my chatbot instructions',prompt,'my-bbt-chatbot-instructions.txt','text/plain')
        st.link_button('Open Voiceflow when your lecturer says to start','https://creator.voiceflow.com/')
        st.markdown('1. Sign in using your lecturer’s account instructions.\n2. Create a project and choose **Start from scratch**.\n3. Paste the instructions into the **Global agent description / prompt**.\n4. Test a drink order, then change only the sugar or a topping. Check that the other choices remain.')
        st.caption('Voiceflow is a separate service with account and usage limits. Your lecturer will guide the setup. The game does not need it.')
