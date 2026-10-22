import streamlit as st
from play import render_freeplay, render_menu
from engine import TITLES, LESSONS, new_round, respond, guidance, is_complete, checkpoint, restore_checkpoint
st.set_page_config(page_title='Chatbot Arcade | TP Applied AI',page_icon='💬',layout='wide')
st.markdown('''<style>
.block-container{max-width:1100px;padding-top:2rem;padding-bottom:2rem}
h1{letter-spacing:-.045em}h2,h3{letter-spacing:-.025em}
[data-testid="stChatMessage"]{border:1px solid #dce5df;border-radius:14px}
.stButton>button{border-radius:10px;min-height:44px}
.kicker{font-size:.75rem;letter-spacing:.14em;color:#397357;font-weight:700}
</style>''',unsafe_allow_html=True)
s=st.session_state
for key,value in {'stage':0,'completed':[],'rounds':{},'notice':None}.items():
    if key not in s:s[key]=value

def stage_data(n):
    if n not in s.rounds:s.rounds[n]=new_round(n)
    return s.rounds[n]
def go(n):
    if 0<=n<=min(len(s.completed),4):s.stage=n

def send(text):
    text=text.strip()[:300]
    if not text:return
    n=s.stage;r=stage_data(n)
    reply,state=respond(text,r['state'],n,r['repaired'])
    r['state']=state
    r['messages']=(r['messages']+[{'role':'user','content':text},{'role':'assistant','content':reply}])[-30:]
    if is_complete(n,r) and n not in s.completed:s.completed=sorted(s.completed+[n])

def send_draft(n):
    send(s.get(f'draft{n}', ''))

def repair():
    r=stage_data(s.stage);r['repaired']=True
    r['messages'].append({'role':'assistant','content':{1:'Memory enabled. I will keep the other details when you change part of your order.',2:'Clarification enabled. I will ask which sugar level you mean.',3:'Menu checking enabled. I will only offer items from our menu.'}[s.stage]})

def replay():
    s.rounds[s.stage]=new_round(s.stage)
    s.notice='This stage has restarted. Previously earned stamps are kept.'
def reset_all():s.clear()

st.markdown('<div class="kicker">TEMASEK POLYTECHNIC · APPLIED AI</div>',unsafe_allow_html=True)
st.title('Fix the bubble-tea bot')
st.write('Repair Sip Bot in four stages, then unlock your own BBT counter. Six flavours, five toppings and plenty of combinations to try. Play in pairs and swap who types after each stage.')
nav=st.columns(4)
for n,col in enumerate(nav):
    with col:
        status='✓ Complete' if n in s.completed else '● You are here' if n==s.stage else 'Next' if n==len(s.completed) else 'Locked'
        st.button(f'{n+1}. {TITLES[n]}',key=f'nav{n}',disabled=n>len(s.completed),type='primary' if n==s.stage else 'secondary',width='stretch',on_click=go,args=(n,))
        st.caption(status)
st.progress(len(s.completed)/4,text=f'{len(s.completed)} of 4 stages complete')
if s.notice:st.info(s.notice);s.notice=None
with st.sidebar:
    st.subheader('Game menu')
    st.caption('Rule-based chatbot simulation. No AI model or external account is needed.')
    st.write('**Six flavours**\n\nMilk tea · Lychee tea · Lemon tea · Taro milk tea · Matcha milk tea · Brown sugar milk tea')
    st.write('**Sugar**\n\n0%, 25%, 50%, 75%, 100%')
    st.write('**Ice**\n\nNormal, less, none or extra')
    st.write('**Extras**\n\nRegular or large. Up to two toppings: pearls, pudding, grass jelly, aloe vera or coconut jelly.')
    st.divider()
    st.download_button('Save checkpoint',checkpoint(s.completed,s.stage),'chatbot-arcade-checkpoint.json','application/json',width='stretch')
    st.caption('Saves completed stages. After a refresh, load it below. Chats, unfinished stages and counter customisations restart.')
    with st.expander('Load a checkpoint'):
        uploaded=st.file_uploader('Choose your saved JSON',type=['json'])
        if st.button('Load checkpoint',disabled=uploaded is None):
            try:
                if uploaded.size>4096:raise ValueError('That file is too large to be a checkpoint.')
                completed,stage=restore_checkpoint(uploaded.getvalue())
                s.completed=completed;s.stage=stage;s.rounds={}
                for key in ['counter','served','customer','reveal_next','bot_name','bot_tone','flavour','size','sugar','ice','toppings','counter_draft']:
                    s.pop(key,None)
                s.notice='Checkpoint loaded. Completed stages are restored.'
                st.rerun()
            except ValueError as exc:st.error(str(exc))
    with st.expander('Restart the whole game'):
        checked=st.checkbox('Clear every stage and stamp')
        st.button('Confirm full restart',disabled=not checked,on_click=reset_all)
if s.stage==4:
    st.success('You repaired Sip Bot. All four stages complete!')
    render_freeplay()
    with st.expander('Your four discoveries'):
        for n in range(4):st.write(f'{n+1}. '+LESSONS[n])
    st.button('Replay from stage 1',on_click=go,args=(0,))

else:
    n=s.stage;r=stage_data(n)
    instruction,suggestions,repair_label=guidance(n,r);complete=is_complete(n,r)
    st.subheader(f'Stage {n+1} of 4: {TITLES[n]}')
    if complete:st.success('Stage complete. '+LESSONS[n])
    else:st.info('Your next move: '+instruction)
    render_menu()
    chat,card=st.columns([2.1,1],gap='large')
    with card:
        with st.container(border=True):
            st.markdown('**Sip Bot’s order card**');order=r['state']['order']
            st.write('Drink: '+order.get('drink','Not set'));st.write('Sugar: '+order.get('sugar','Not set'));st.write('Ice: '+order.get('ice','Not set'))
            st.write('Size: '+order.get('size','regular'))
            st.write('Toppings: '+(', '.join(order.get('toppings',[])) or 'none'))
            st.caption('Size defaults to regular. Toppings default to none.')
            st.caption('Confirmed' if r['state']['confirmed'] else 'Not confirmed')
        if n>0:
            feature={1:'Memory',2:'Clarification',3:'Menu checking'}[n]
            st.markdown(f'**{feature}: {"ON" if r["repaired"] else "OFF"}**')
            if repair_label and not complete:st.button(repair_label,key=f'repair{n}',type='primary',width='stretch',on_click=repair)
            elif not r['repaired']:st.caption('Try the conversation first. The repair button appears after you see the problem.')
        if n==1:st.caption('Target order: lychee tea, 25% sugar, no ice.')
        elif n==2:st.caption('“Less sweet” does not name an exact sugar level. Your preferred level is 25%.')
        elif n==3:st.caption('Durian milkshake is deliberately missing from today’s menu.')
        st.button('Restart this stage',key=f'replay{n}',on_click=replay,width='stretch')
        st.caption('Replays keep earned stamps. Only this chat and order are cleared.')
    with chat:
        st.caption('Latest exchange')
        with st.container(border=True):
            for msg in r['messages'][-2:]:
                with st.chat_message(msg['role'],avatar='💬' if msg['role']=='assistant' else '🙂'):st.write(msg['content'])
        if len(r['messages'])>2:
            with st.expander('Earlier messages: compare before and after'):
                for msg in r['messages'][:-2]:
                    st.markdown('**'+('Sip Bot' if msg['role']=='assistant' else 'You')+'**')
                    st.write(msg['content'])
        if not complete and suggestions:
            st.markdown('**Try a message**');st.caption('Click to send immediately. You can also type your own message below.')
            for i,text in enumerate(suggestions):st.button('Send: '+text,key=f'suggest{n}_{i}_{text}',on_click=send,args=(text,),width='stretch')
        elif repair_label and not complete:st.caption('Use the repair button next to the chat, then send another message.')
        with st.form(f'compose{n}',clear_on_submit=True):
            draft=st.text_input('Or write your own',max_chars=300,placeholder='Type here, then press Enter or Send',key=f'draft{n}')
            st.form_submit_button('Send message',width='stretch',on_click=send_draft,args=(n,))
        if not complete:
            with st.expander('Why did the bot say that?'):
                st.write({0:'This version recognises “order milk tea” exactly. A person would recognise many other ways to ask.',1:'With memory off, each new order detail replaces the previous details. With memory on, it updates only the part you mention.',2:'With clarification off, the bot picks 50%. With it on, the bot asks you to choose.',3:'With menu checking off, this deliberately broken demo accepts an unavailable item. With checking on, it offers the actual menu.'}[n])
    if (complete or n in s.completed) and n>0:
        with st.expander('Play a little: try an extra before moving on'):
            st.caption('Your earned stage stamp stays. The next button remains available.')
            for text in ['Add pearls','Make it large','Remove pearls','Show my order']:
                st.button('Send: '+text,on_click=send,args=(text,),key=f'extra{n}_{text}')
    if complete or n in s.completed:
        st.button('Finish the game →' if n==3 else f'Next: Stage {n+2} →',type='primary',width='stretch',on_click=go,args=(n+1,))
        if not complete:st.caption('You already completed this stage earlier, so you can continue or finish the replay.')
st.caption('Fictional drinks only. No real orders or payments. No speed score: explain your discovery to your partner.')
