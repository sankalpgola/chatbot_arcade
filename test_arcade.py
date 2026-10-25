"""Optional Streamlit AppTest smoke checks; requires the Streamlit dependency."""
import unittest
from pathlib import Path
from engine import new_round, respond, guidance, is_complete, checkpoint, restore_checkpoint

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None

@unittest.skipIf(AppTest is None, 'Install requirements.txt to run Streamlit browser simulation')
class TestStreamlitUI(unittest.TestCase):
    def test_app_initial_stage(self):
        app=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=20).run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('Chatbot Arcade' in t.value for t in app.title))
        self.assertTrue(any('Send: Can I get a milk tea please?' == x.label for x in app.button))

    def test_full_flow(self):
        app=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=20).run()
        def click(label):
            buttons=[x for x in app.button if x.label==label]
            self.assertTrue(buttons, f'Expected button {label}; saw {[x.label for x in app.button]}')
            buttons[0].click().run()
            self.assertEqual(len(app.exception),0)
        def fix(choice):
            app.radio[0].set_value(choice).run();click('Apply this rule')
        click('Send: Can I get a milk tea please?');click('Send: order milk tea')
        fix('Add common alternative phrases to the matching rule')
        click('Send: Can I get a milk tea please?');click('Go to next stage →')
        click('Send: Lychee tea');click('Send: 25% sugar')
        fix('Update only the changed field and preserve the other fields')
        click('Send: Lychee tea');click('Send: Actually, no ice');click('Send: Confirm');click('Go to next stage →')
        click('Send: Less sweet please');fix('Ask which listed sugar percentage the customer wants')
        click('Send: Less sweet please');click('Send: 25% sugar');click('Go to next stage →')
        click('Send: Can I get a durian milkshake?');fix('Check the menu before confirming the drink')
        click('Send: Can I get a durian milkshake?');click('Finish the stages →')
        self.assertEqual(app.session_state['completed'],[0,1,2,3])
        self.assertEqual(app.session_state['stage'],4)

if __name__ == '__main__':unittest.main()
