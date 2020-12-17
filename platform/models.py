from __future__ import unicode_literals

import json
from django.db import models

class User(models.Model):
	name = models.CharField(max_length=512, unique=True)

	def export(self):
		data = {}
		data['name'] = self.name
		data['id'] = unicode(self.id)
		return data

class Document(models.Model):
	doc_id = models.CharField(max_length=32, unique=True)
	title = models.CharField(max_length=255)
	content = models.TextField()
	version = models.IntegerField(default=0)

	def export(self):
		data = {}
		data['id'] = self.doc_id
		data['title'] = self.title
		data['content'] = self.content
		data['version'] = self.version
		return data

class DocumentChange(models.Model):
	document = models.ForeignKey(Document)
	version = models.IntegerField(default=0, db_index=True)
	request_id = models.CharField(max_length=64, unique=True)
	time = models.DateTimeField(auto_now_add=True, db_index=True)
	parent_version = models.IntegerField(default=0)
	data = models.TextField()

	class Meta:
		unique_together = (
			('document', 'version'),
			('document', 'request_id', 'parent_version'),
		)

	def export(self):
		data = {}
		data['version'] = self.version
		data['time'] = self.time.isoformat()
		data['op'] = json.loads(self.data)
		return data
