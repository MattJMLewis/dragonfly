from unittest import TestCase
from dragonfly.db.database import DB
from ..models.article import Article

class TestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = Article()
        cls.db = DB().table('articles')
        cls.db.custom_sql("CREATE TABLE articles (\ntitle VARCHAR(50) UNIQUE,\ntext TEXT,\nid INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,\ncreated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\nupdated_at TIMESTAMP ON UPDATE NOW() DEFAULT NOW()\n)")

        for i in range(1, 10):
            cls.model.create({'title': f"Article {i}", 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'})

    def tearDown(self):
        self.db.custom_sql("DROP TABLE articles")

    def test_create(self):
        self.model.create({'title': 'Test Article', 'text': 'Testing'})
        model = self.model.where('title', '=', 'Test Article').first().to_dict()

        del model['created_at']
        del model['updated_at']
        del model['id']

        self.assertEqual(model, {'title': 'Test Article', 'text': 'Testing'})

    def test_first(self):
        model =

    def test_find(self):
        model = self.model.find(1)
        self.assertEqual([model.id, model.title, model.text], [1, 'Article 1', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'])

