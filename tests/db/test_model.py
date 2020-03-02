from unittest import TestCase
from dragonfly.db.database import DB
from tests.models.article import Article


class TestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = Article()
        cls.db = DB().table('articles')
        cls.db.custom_sql("CREATE TABLE articles (\ntitle VARCHAR(50) UNIQUE,\ntext TEXT,\nid INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,\ncreated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\nupdated_at TIMESTAMP ON UPDATE NOW() DEFAULT NOW()\n)")


        for i in range(0, 10):
            cls.model.create({'title': f"Article {i}", 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'})

    @classmethod
    def tearDownClass(cls):
        cls.db.custom_sql("DROP TABLE articles")

    def test_create(self):
        self.model.create({'title': 'Test Article', 'text': 'Testing'})
        model = self.model.where('title', '=', 'Test Article').first()

        md = model.to_dict()

        del md['created_at']
        del md['updated_at']
        del md['id']

        model.delete()

        self.assertEqual(md, {'title': 'Test Article', 'text': 'Testing'})


    def test_first(self):
        model = self.model.first().to_dict()
        del model['created_at']
        del model['updated_at']

        self.assertEqual(model, {'title': 'Article 0', 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.', 'id': 1})

    def test_get(self):
        model = self.model.get()
        self.assertEqual(len(model), 10)

    def test_all(self):
        model = self.model.get()
        self.assertEqual(len(model), 10)

    def test_find(self):
        model = self.model.find(2)

        self.assertEqual([model.id, model.title, model.text], [2, 'Article 1', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'])

    def test_select(self):
        model = self.model.select('title', 'text').find(2)
        self.assertEqual(model, {'title': 'Article 1', 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'})

    def test_where(self):
        model = self.model.where('title', '=', 'Article 1').first().to_dict()

        del model['created_at']
        del model['updated_at']

        self.assertEqual(model, {'title': 'Article 1', 'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.', 'id': 2})

    def test_paginate(self):

        result = self.model.paginate(size=5)

        self.assertEqual(5, len(result[0]))
        self.assertEqual(result[1], {'total': 10, 'per_page': 5, 'current_page': 1, 'last_page': 2, 'from': 1, 'to': 5})

    def test_save(self):

        model = self.model.first()

        id = model.id

        model.title = 'Modified title'
        model.text = 'Modified text'

        model.save()

        retrieved_model = self.model.where('title', '=', 'Modified title').first()

        self.assertEqual(id, retrieved_model.id)

    def test_delete(self):

        self.model.create({'title': 'Dummy', 'text': 'Dummy text'})

        m = self.model.where('title', '=', 'Dummy').first()
        m.delete()

        self.assertEqual(len(self.model.where('title', '=', 'Dummy').get()), 0)







