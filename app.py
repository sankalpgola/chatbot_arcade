"""TP NextGen Chatbot Arcade: four inspect-and-repair challenges.

All responses are deterministic and local. No generative AI API is used.
"""
import streamlit as st
from engine import TITLES, LESSONS, new_round, respond, guidance, is_complete, checkpoint, restore_checkpoint
from play import render_freeplay

st.set_page_config(page_title='Chatbot Arcade | TP NextGen', page_icon='🧋', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
:root{--tp:#245a9b;--navy:#15385c;--ice:#eaf4ff}
.block-container{max-width:1080px;padding-top:1.35rem;padding-bottom:3rem}
h1{font-size:2.35rem!important;letter-spacing:-.035em;color:#214d82}h2{font-size:1.45rem!important;letter-spacing:-.025em}
h3{font-size:1.13rem!important}p,li{line-height:1.52}
[data-testid="stChatMessage"]{border:1px solid #dce7f4;border-radius:14px;padding:.5rem}
.stButton button{min-height:44px;border-radius:11px;font-weight:650}
.hero{background:linear-gradient(115deg,#214e8d,#1877af);color:#fff;padding:19px 24px;border-radius:16px;margin-bottom:12px}
.hero h2,.hero p{color:white!important;margin:0}.hero .eyebrow{letter-spacing:.1em;font-size:.74rem;font-weight:800;color:#dcecff}
.rule{background:#eff6fd;border-left:5px solid #288dd1;border-radius:9px;padding:14px 17px;color:#153b66;margin:9px 0}
.question{background:#fff8eb;border-left:5px solid #eda83d;border-radius:9px;padding:12px 16px;margin:10px 0}
.good{background:#e8f7ef;border-left:5px solid #279e73;border-radius:8px;padding:11px 15px;margin:9px 0}
.smallcaps{font-size:.72rem;font-weight:800;letter-spacing:.12em;color:#336fad}
.caption{font-size:.85rem;color:#48617d}
</style>''',unsafe_allow_html=True)

s=st.session_state
for k,v in {'stage':0,'completed':[],'rounds':{},'notice':None}.items():
    if k not in s:s[k]=v

def rd(n):
    if n not in s.rounds:s.rounds[n]=new_round(n)
    return s.rounds[n]
def advance(n):
    if 0<=n<=min(len(s.completed),4):s.stage=n

def say(value):
    value=(value or '').strip()[:300]
    if not value:return
    n=s.stage;r=rd(n)
    answer,state=respond(value,r['state'],n,r['repaired'])
    r['state']=state
    r['messages']=(r['messages']+[{'role':'user','content':value},{'role':'assistant','content':answer}])[-28:]
    if is_complete(n,r) and n not in s.completed:s.completed=sorted(s.completed+[n])

def send_typed(n):say(s.get(f'entry{n}',''))

def repair_rule():
    n=s.stage;r=rd(n)
    r['repaired']=True
    changes={
        0:'NEW RULE: Recognise common polite ways of asking for milk tea, not just one exact command.',
        1:'NEW RULE: Update only the detail that changed. Keep the rest of the order.',
        2:'NEW RULE: If the sugar preference is unclear, ask the customer to choose a percentage.',
        3:'NEW RULE: Before accepting a drink, check whether it appears on the menu.'}
    r['messages'].append({'role':'assistant','content':changes[n]})

def restart():s.rounds[s.stage]=new_round(s.stage)
def reset_all():s.clear()

STAGES=[
    {'short':'INTENT','color':'#3269af','goal':'One intention can be phrased in different ways.',
     'question':'Why does “order milk tea” work, but “Can I get a milk tea please?” fail?',
     'expected':'The original rule checks for exactly one phrase. Both messages express the same intention: ordering milk tea.',
     'before':'IF message is exactly “order milk tea” → accept; OTHERWISE → reject.',
     'options':['Accept any sentence as a drink order','Add common alternative phrases to the matching rule','Make the bot always say “I do not understand”'],
     'correct':1,'after':'IF a message expresses a known milk tea request → accept; otherwise ask for clarification.'},
    {'short':'MEMORY','color':'#8c56ac','goal':'Changing one detail should not erase the rest.',
     'question':'After setting 25% sugar, why did the selected drink disappear?',
     'expected':'The broken system overwrote the whole stored order rather than updating the sugar field only.',
     'before':'new_order = {sugar: 25%}  (all earlier fields disappear)',
     'options':['Delete the order each time a user speaks','Guess a different drink after every message','Update only the changed field and preserve the other fields'],
     'correct':2,'after':'order[sugar] = 25%  (the original drink stays saved)'},
    {'short':'CLARIFICATION','color':'#d28b29','goal':'Do not guess when the request is unclear.',
     'question':'Why is “less sweet” not enough information for the bot?',
     'expected':'Different customers mean different sugar percentages. Ask a follow-up question rather than guessing 50%.',
     'before':'IF user says “less sweet” → choose 50% automatically.',
     'options':['Always set sugar to 50%','Ask which listed sugar percentage the customer wants','Cancel every order'],
     'correct':1,'after':'IF sugar level is unclear → ask: 0%, 25%, 50%, 75% or 100%?'},
    {'short':'VALIDATION','color':'#248b79','goal':'Accept only options that actually exist.',
     'question':'Why does the broken bot accept a durian milkshake?',
     'expected':'It fails to check the order against its menu. Valid input must match an available item.',
     'before':'IF user names a drink → accept it, even when unavailable.',
     'options':['Accept the request and hope the shop has it','Check the menu before confirming the drink','Add every imaginary drink to the menu'],
     'correct':1,'after':'IF drink is on the menu → accept; ELSE → explain and show alternatives.'}
]

st.markdown('<div class="smallcaps">TEMASEK POLYTECHNIC · SCHOOL OF INFORMATICS & IT · APPLIED AI</div>', unsafe_allow_html=True)
st.title('Chatbot Arcade 🧋')
st.caption('DAY 1 • Work in pairs, one laptop per pair • Four short challenges, about 25–30 minutes • No real orders or personal data')

if s.stage==4:
    st.success('All four stages finished. You inspected and repaired four chatbot rules!')
    st.markdown('### What is happening under the hood?')
    for i,meta in enumerate(STAGES):
        st.write(f'**{i+1}. {meta["short"]}:** {meta["expected"]}')
    if st.toggle('Open optional drinks counter',value=False):render_freeplay()
    st.markdown('### Next stop: Conferbot')
    st.write('The arcade simulates a rule-based bot. In Conferbot, you will generate, inspect and **manually connect a new node** in a conversation flow.')
    st.link_button('Open Conferbot','https://www.conferbot.com/')
    st.info('Use the Day 1 worksheet prompt for your Conferbot chatbot. The arcade menu is different from the worksheet menu.')
    st.button('Review Stage 1',on_click=advance,args=(0,))
else:
    n=s.stage;r=rd(n);meta=STAGES[n];complete=is_complete(n,r)
    st.progress(len(s.completed)/4, text=f'Completed: {len(s.completed)} / 4 stages')
    st.markdown(f'<div class="hero" style="background:linear-gradient(108deg,#214d82,{meta["color"]})"><span class="eyebrow">STAGE {n+1} OF 4 · {meta["short"]}</span><h2>{TITLES[n]}</h2><p>{meta["goal"]}</p></div>',unsafe_allow_html=True)
    st.markdown('**Your mission:** Try the suggested messages, notice what goes wrong, choose a rule to fix, then send the same request again.')
    a,b=st.columns([1.2,1],gap='large')
    with a:
        st.subheader('1 · Try the chatbot')
        for msg in r['messages'][-5:]:
            with st.chat_message(msg['role'],avatar='🧋' if msg['role']=='assistant' else '🙂'):st.write(msg['content'])
        instruction,suggestions,_=guidance(n,r)
        if not complete:st.caption('NEXT: '+instruction)
        if suggestions and not complete:
            for i,t in enumerate(suggestions):st.button('Send: '+t, key=f'suggest{n}_{i}',on_click=say,args=(t,),width='stretch')
        with st.form(f'form{n}',clear_on_submit=True):
            st.text_input('Or type a message',max_chars=300,key=f'entry{n}',placeholder='What would you say to the bot?')
            st.form_submit_button('Send my message',on_click=send_typed,args=(n,),width='stretch')
        if n in (1,2,3):
            order=r['state']['order']
            with st.expander('See the bot’s stored order',expanded=n==1):
                st.write('**Drink:** '+order.get('drink','Not saved'))
                st.write('**Sugar:** '+order.get('sugar','Not saved'))
                st.write('**Ice:** '+order.get('ice','Not saved'))
                st.caption('This is the bot’s memory, not another question you need to answer.')
    with b:
        st.subheader('2 · Inspect the rule')
        st.markdown('<div class="smallcaps">BEFORE THE FIX</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="rule">{meta["before"]}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="question"><b>Discuss with your partner</b><br>{meta["question"]}</div>',unsafe_allow_html=True)
        ev=set(r['state']['events'])
        seen_problem=(('different_words' in ev and 'exact' in ev) if n==0 else ['forgot' in ev,'guessed_sugar' in ev,'invented' in ev][n-1])
        if seen_problem or r['repaired']:
            if not r['repaired']:
                st.markdown('**3 · Choose a better rule**')
                selected=st.radio('Which change would fix this?',meta['options'],index=None,key=f'fix_choice{n}')
                if st.button('Apply this rule',type='primary',key=f'fix{n}',width='stretch'):
                    if selected==meta['options'][meta['correct']]:
                        repair_rule();st.rerun()
                    else:st.error('Not quite. Consider which rule directly fixes the behaviour you observed.')
            else:
                st.markdown('<div class="smallcaps">AFTER THE FIX</div>',unsafe_allow_html=True)
                st.markdown(f'<div class="good">{meta["after"]}</div>',unsafe_allow_html=True)
                st.caption('Now test the same request again. A fix only counts when the behaviour changes.')
        else:st.info('Send the example messages until you have seen the problem. Then you can change the rule.')
        if complete:
            st.success('Stage completed!')
            with st.expander('Expected result and explanation',expanded=True):
                st.write(meta['expected'])
                st.write('**Computing connection:** '+['Intent / pattern matching','Variables / state','Selection / clarification','Input validation'][n])
            st.button('Finish the stages →' if n==3 else 'Go to next stage →',type='primary',width='stretch',on_click=advance,args=(n+1,))
        else:
            with st.expander('Need a hint?'):st.write('Look for what is missing from the bot’s decision rule. Can it use another phrase, keep a saved value, ask a question or check valid inputs?')
    st.divider()
    x,y=st.columns([1,1])
    with x:st.button('Restart this stage',on_click=restart,width='stretch')
    with y:
        if n in s.completed:st.button('Continue to next stage →',on_click=advance,args=(n+1,),width='stretch')
    with st.expander('Game settings / restore a completed-stage checkpoint'):
        st.download_button('Save progress checkpoint',checkpoint(s.completed,s.stage),'chatbot-arcade-checkpoint.json','application/json')
        up=st.file_uploader('Load a saved checkpoint',type=['json'])
        if st.button('Load saved checkpoint',disabled=up is None):
            try:
                cm,sg=restore_checkpoint(up.getvalue());s.completed=cm;s.stage=sg;s.rounds={};st.rerun()
            except ValueError as exc:st.error(str(exc))
        if st.checkbox('I want to restart the entire game'):st.button('Clear all progress',on_click=reset_all)

st.caption('A classroom simulation of a rule-based chatbot. It does not use an AI language model. The rules are simplified for learning.')
