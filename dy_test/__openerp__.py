# -*- coding: utf-8 -*-
{
	'name': "dy test",
	'author': "zhang.jian",
	'sequence': 1,
	'summary': u'test',
	'website': "http://www.xxxx.com",
	'category': 'Yqjd Management',
	"description": """
		test
	""",
	'version': '1.0',
	'depends': ['base'],
	'data': [
		'view/dy_test.xml',
		'view/dy_test_menu.xml',
		'security/security.xml',
		'security/ir.model.access.csv',
	],
	'installable': True,
	'auto_install': False,
	'application': True,
}