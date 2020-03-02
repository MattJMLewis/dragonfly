import shutil
import unittest
from unittest import TestCase

from click.testing import CliRunner

from tests.builder.builder import *

from dragonfly.db.database import DB

from MySQLdb._exceptions import OperationalError

from config import ROOT_DIR

os.chdir(ROOT_DIR + '/tests/builder')

class TestBuilder(TestCase):

    def tearDown(self):
        shutil.rmtree('controllers')
        shutil.rmtree('middleware')
        shutil.rmtree('models')
        shutil.rmtree('storage')
        shutil.rmtree('templates')

    def test_setup(self):
        runner = CliRunner()
        result = runner.invoke(setup)

        self.assertTrue(os.path.exists('controllers'))
        self.assertTrue(os.path.exists('middleware'))
        self.assertTrue(os.path.exists('models'))
        self.assertTrue(os.path.exists('storage'))
        self.assertTrue(os.path.exists('templates'))

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Successfully created directories!\n")

    def test_generate(self):
        runner = CliRunner()
        runner.invoke(setup)

        result = runner.invoke(generate, ['--type', 'model', 'model'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Successfully created model!\n")

        result = runner.invoke(generate, ['--type', 'controller', 'controller'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Successfully created controller!\n")

        result = runner.invoke(generate, ['--type', 'middleware', 'middleware'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Successfully created middleware!\n")

        self.assertTrue(os.path.exists('controllers/controller.py'))
        self.assertTrue(os.path.exists('middleware/middleware.py'))
        self.assertTrue(os.path.exists('models/model.py'))

    def test_auth(self):
        runner = CliRunner()
        runner.invoke(setup)

        os.makedirs('templates/users', exist_ok=True)

        result = runner.invoke(auth)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output,
                         "Successfully generated auth scaffold!\nPlease add 'middleware.csrf_middleware' and 'middleware.user_middleware' to the MIDDLEWARE list in 'config.py'.\nPlease remigrate your tables.\n")

        self.assertTrue(os.path.exists('routes.py'))
        self.assertTrue(os.path.exists('templates/users/login.html'))
        self.assertTrue(os.path.exists('templates/users/register.html'))
        self.assertTrue(os.path.exists('models/user.py'))
        self.assertTrue(os.path.exists('models/session.py'))
        self.assertTrue(os.path.exists('middleware/user_middleware.py'))
        self.assertTrue(os.path.exists('middleware/csrf_middleware.py'))

        os.remove('routes.py')

    def test_migrate(self):
        runner = CliRunner()
        runner.invoke(setup)

        result = runner.invoke(migrate)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Migrating users model\nMigrated users successfully!\nMigrating sessions model\nMigrated sessions successfully!\n")

        DB().table('dragonfly_testing').custom_sql("DROP TABLE sessions")
        DB().table('dragonfly_testing').custom_sql("DROP TABLE users")

    def test_drop(self):
        runner = CliRunner()

        runner.invoke(setup)
        runner.invoke(migrate)

        result = runner.invoke(drop)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, "Deleting sessions model\nDeleted sessions successfully!\nDeleting users model\nDeleted users successfully!\n")

        with self.assertRaises(OperationalError):
            DB().table('dragonfly_testing').custom_sql("DROP TABLE sessions")
            DB().table('dragonfly_testing').custom_sql("DROP TABLE users")