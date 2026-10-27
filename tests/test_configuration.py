"""Check configuration ordering with stubs, without Telegram or worker imports."""
import builtins
import os
from pathlib import Path
import types
import unittest
from unittest.mock import Mock, patch


BOT_SOURCE = Path(__file__).resolve().parents[1] / 'src' / 'unoBot.py'


class BotConfigurationTests(unittest.TestCase):
    def execute_module(self, token=None, reject_token=False, forbid_workers=False):
        self.events = []

        def validate(value):
            self.events.append('validate')
            if reject_token:
                raise ValueError('configuration validator rejected token')

        self.validator = Mock(side_effect=validate)
        fake_bot = types.SimpleNamespace(
            message_handler=lambda *args, **kwargs: lambda function: function)

        def create_bot(value):
            self.events.append('bot')
            return fake_bot

        self.bot_constructor = Mock(side_effect=create_bot)
        telebot = types.ModuleType('telebot')
        telebot.TeleBot = self.bot_constructor
        telebot.types = types.ModuleType('telebot.types')
        util = types.ModuleType('telebot.util')
        util.validate_token = self.validator
        apihelper = types.ModuleType('telebot.apihelper')
        apihelper.ApiTelegramException = type('ApiTelegramException', (Exception,), {})
        stubs = {'telebot': telebot, 'telebot.util': util,
                 'telebot.apihelper': apihelper,
                 'logic': types.ModuleType('logic'),
                 'sharedVars': types.ModuleType('sharedVars')}
        original_import = builtins.__import__

        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in ('logic', 'sharedVars'):
                self.events.append(name)
                if forbid_workers:
                    raise AssertionError('worker imports must follow validation')
            if name in stubs:
                return stubs[name]
            return original_import(name, globals, locals, fromlist, level)

        environment = {} if token is None else {'BOT_TOKEN': token}
        namespace = {'__name__': 'unoBot'}
        code = compile(BOT_SOURCE.read_text(), str(BOT_SOURCE), 'exec')
        with patch.dict(os.environ, environment, clear=True), \
                patch('builtins.__import__', new=guarded_import):
            exec(code, namespace)
        return namespace

    def test_missing_or_blank_token_fails_before_validation_or_workers(self):
        for token in (None, '', '  '):
            with self.subTest(token=token):
                with self.assertRaisesRegex(RuntimeError, 'Set the BOT_TOKEN'):
                    self.execute_module(token, forbid_workers=True)
                self.assertEqual(self.events, [])
                self.validator.assert_not_called()
                self.bot_constructor.assert_not_called()

    def test_validator_rejection_fails_before_workers(self):
        with self.assertRaisesRegex(ValueError, 'configuration validator rejected token'):
            self.execute_module('not-a-telegram-token', reject_token=True,
                                forbid_workers=True)
        self.validator.assert_called_once_with('not-a-telegram-token')
        self.assertEqual(self.events, ['validate'])
        self.bot_constructor.assert_not_called()

    def test_configured_token_is_trimmed_and_validated_before_workers(self):
        self.execute_module('  offline-test-token  ')
        self.validator.assert_called_once_with('offline-test-token')
        self.bot_constructor.assert_called_once_with('offline-test-token')
        self.assertEqual(self.events, ['validate', 'logic', 'sharedVars', 'bot'])


if __name__ == '__main__':
    unittest.main()
