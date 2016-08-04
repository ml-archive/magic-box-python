from django.db import models


class Blog(models.Model):
    name = models.CharField(max_length=255)


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='person')


class Article(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='articles')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='articles')


class Comment(models.Model):
    text = models.CharField(max_length=255)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
