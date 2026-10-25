"""Dependency-free smoke checks for engine behaviour and Conferbot hand-off."""
import unittest
from engine import new_round, respond, guidance, is_complete, conferbot_prompt, MENU, SUGARS, ICE, TOPPINGS, recipe_message, restore_checkpoint, checkpoint

class Smoke(unittest.TestCase):
    def test_all_stages(self):
        r = new_round(0)
        for phrase in ['Can I get a milk tea please?', 'order milk tea']:
            _,r['state'] = respond(phrase,r['state'],0,r['repaired'])
        r['repaired']=True
        _,r['state']=respond('Can I get a milk tea please?',r['state'],0,r['repaired'])
        self.assertTrue(is_complete(0,r))
        for stage in [1,2,3]:
            r=new_round(stage)
            for _ in range(20):
                if is_complete(stage,r):break
                _,suggestions,repair_label=guidance(stage,r)
                if repair_label:r['repaired']=True
                else:
                    self.assertTrue(suggestions)
                    _,r['state']=respond(suggestions[0],r['state'],stage,r['repaired'])
            self.assertTrue(is_complete(stage,r),f'stage {stage}')
    def test_menu_replies_and_prompt(self):
        for drink in MENU:
            state=new_round(1)['state']
            reply,state=respond(recipe_message(drink,'large','25%','no ice',['pearls','pudding']),state,4,True)
            self.assertEqual(state['order'].get('drink'),drink)
            self.assertEqual(state['order'].get('size'),'large')
            self.assertEqual(state['order'].get('sugar'),'25%')
            self.assertEqual(state['order'].get('toppings'),['pearls','pudding'])
            self.assertNotIn('Voiceflow',reply)
        for tone in ['Friendly','Deadpan','Sports commentator','Dramatic']:
            prompt=conferbot_prompt('Sip Bot',tone)
            self.assertLessEqual(len(prompt),900)
            self.assertIn('Conferbot', 'Conferbot')
            self.assertIn('cup size',prompt)
    def test_checkpoint(self):
        self.assertEqual(restore_checkpoint(checkpoint([0,1],2)),([0,1],2))

if __name__ == '__main__': unittest.main()
