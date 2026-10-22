import json
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from engine import new_round, respond, guidance, is_complete, checkpoint, restore_checkpoint, MENU, TOPPINGS, recipe_message, CUSTOMERS, matches_customer, bot_instructions

class ArcadeTests(unittest.TestCase):
    def boot(self):
        at=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=15).run()
        self.assertFalse(at.exception)
        return at
    def click(self,at,label):
        next(b for b in at.button if b.label==label).click().run()
        self.assertFalse(at.exception)
    def test_guided_journey(self):
        at=self.boot()
        self.assertTrue(at.button(key='nav1').disabled)
        self.assertEqual(len(at.radio),0)
        self.assertFalse(any('Voiceflow' in m.value for m in at.markdown))
        self.click(at,'Send: Can I get a milk tea please?')
        self.click(at,'Send: order milk tea')
        self.click(at,'Next: Stage 2 →')
        self.assertFalse(any(b.label=='Enable memory' for b in at.button))
        self.click(at,'Send: Lychee tea');self.click(at,'Send: 25% sugar')
        self.assertNotIn('drink',at.session_state['rounds'][1]['state']['order'])
        self.click(at,'Enable memory');self.click(at,'Send: Lychee tea')
        self.click(at,'Send: Actually, no ice');self.click(at,'Send: Confirm')
        self.click(at,'Next: Stage 3 →')
        self.click(at,'Send: Less sweet please');self.click(at,'Enable clarification')
        self.click(at,'Send: Less sweet please');self.click(at,'Send: 25% sugar')
        self.click(at,'Next: Stage 4 →')
        self.click(at,'Send: Can I get a durian milkshake?');self.click(at,'Enable menu checking')
        self.click(at,'Send: Can I get a durian milkshake?');self.click(at,'Finish the game →')
        self.assertEqual(at.session_state['completed'],[0,1,2,3])
        self.assertTrue(any('All four stages complete' in m.value for m in at.success))
        self.assertFalse(any('Meet Voiceflow' in m.value for m in at.markdown))
        self.click(at,'Reveal the next step')
        self.assertTrue(any('Meet Voiceflow' in m.value for m in at.markdown))
        self.assertIn('Toppings:',at.code[0].value)
        saved=checkpoint(at.session_state['completed'],at.session_state['stage'])
        self.assertEqual(restore_checkpoint(saved),([0,1,2,3],4))
        self.click(at,'Replay from stage 1');self.click(at,'Restart this stage')
        self.assertEqual(at.session_state['completed'],[0,1,2,3])
        self.assertEqual(len(at.session_state['rounds'][0]['messages']),1)
    def test_typed_input_and_isolation(self):
        at=self.boot()
        at.text_input(key='draft0').set_value('please give me milk tea')
        self.click(at,'Send message')
        at.text_input(key='draft0').set_value('order milk tea')
        self.click(at,'Send message')
        self.assertEqual(at.session_state['completed'],[0])
        other=self.boot();self.assertEqual(other.session_state['completed'],[])
        next(c for c in at.checkbox if c.label=='Clear every stage and stamp').check().run()
        self.click(at,'Confirm full restart')
        self.assertEqual(at.session_state['completed'],[])
    def test_guidance_recovers_from_different_first_message(self):
        for first in ['25% sugar','no ice','lychee tea 25% sugar no ice','hello','new order']:
            r=new_round(1)
            _,r['state']=respond(first,r['state'],1)
            for _ in range(15):
                if is_complete(1,r):break
                _,suggestions,repair=guidance(1,r)
                if repair:r['repaired']=True
                else:_,r['state']=respond(suggestions[0],r['state'],1,r['repaired'])
            self.assertTrue(is_complete(1,r),first)
    def test_parser_and_validation(self):
        r=new_round(2)
        _,r['state']=respond('less sweet',r['state'],2,True)
        self.assertEqual(r['state']['pending'],'sugar')
        _,r['state']=respond('25',r['state'],2,True)
        self.assertEqual(r['state']['order']['sugar'],'25%')
        _,r['state']=respond('60% sugar',r['state'],2,True)
        self.assertEqual(r['state']['order']['sugar'],'25%')
        self.assertEqual(r['state']['pending'],'sugar')
        _,r['state']=respond('confirm',r['state'],2,True)
        self.assertFalse(r['state']['confirmed'])
        for raw in ['[]','broken',json.dumps({'app':'chatbot-arcade','version':2,'completed':[1],'stage':2}),json.dumps({'app':'chatbot-arcade','version':2,'completed':[0],'stage':4}),' '*5000]:
            with self.assertRaises(ValueError):restore_checkpoint(raw)
        self.assertEqual(restore_checkpoint(checkpoint([0],1)),([0],1))
    def test_customisation_and_swaps(self):
        for drink in MENU:
            state=new_round(1)['state']
            text=recipe_message(drink,'large','75%','extra ice',['pearls','pudding'])
            _,state=respond(text,state,4,True)
            self.assertEqual(state['order'],{'drink':drink,'size':'large','sugar':'75%','ice':'extra ice','toppings':['pearls','pudding']})
            _,state=respond('remove pearls',state,4,True)
            self.assertEqual(state['order']['toppings'],['pudding'])
            _,state=respond('add aloe vera',state,4,True)
            self.assertEqual(state['order']['toppings'],['pudding','aloe vera'])
            original=state['order'].copy()
            reply,state=respond('add coconut jelly',state,4,True)
            self.assertIn('Two toppings maximum',reply)
            self.assertEqual(state['order'],original)
            _,state=respond('make it 25%',state,4,True)
            self.assertEqual(state['order']['drink'],drink)
            self.assertEqual(state['order']['toppings'],['pudding','aloe vera'])
            _,state=respond('no toppings',state,4,True)
            self.assertEqual(state['order']['toppings'],[])
    def test_freeplay_recipe_and_customer(self):
        at=self.boot()
        at.session_state['completed']=[0,1,2,3]
        at.session_state['stage']=4
        at.run()
        at.selectbox(key='flavour').set_value('taro milk tea')
        at.selectbox(key='size').set_value('large')
        at.selectbox(key='sugar').set_value('25%')
        at.selectbox(key='ice').set_value('no ice')
        at.multiselect(key='toppings').set_value(['pearls','pudding'])
        self.click(at,'Send my recipe to the bot')
        self.assertEqual(at.session_state['counter']['state']['order'],CUSTOMERS[0]['order'])
        self.click(at,'Send: Confirm')
        self.assertEqual(at.session_state['served'],[0])
        self.click(at,'Send: Confirm')
        self.assertEqual(at.session_state['served'],[0])
        self.click(at,'Send: Remove pearls')
        self.assertFalse(at.session_state['counter']['state']['confirmed'])
        self.click(at,'Surprise me with a drink')
        self.assertFalse(at.exception)
        self.assertIn(at.session_state['counter']['state']['order']['drink'],MENU)
        at.text_input(key='bot_name').set_value('Pearl Patrol').run()
        at.selectbox(key='bot_tone').set_value('Deadpan').run()
        self.click(at,'Reveal the next step')
        self.assertIn('Pearl Patrol',at.code[0].value)
        self.assertIn('Deadpan',at.code[0].value)
        self.assertIn('Maximum two',at.code[0].value)
        self.click(at,'Next customer')
        self.assertEqual(at.session_state['counter']['state']['order'],{})
        self.assertEqual(at.session_state['served'],[0])
    def test_clean_package_text(self):
        for p in Path(__file__).parent.rglob('*'):
            if p.is_file() and p.suffix in ['.py','.md','.toml','.txt']:
                text=p.read_text()
                self.assertNotIn(chr(8212),text,p.name)

if __name__=='__main__':unittest.main()
