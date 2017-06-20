# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.addons.base.res.res_request import referenceable_models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.exceptions import UserError
from odoo import tools
import logging
_logger = logging.getLogger(__name__)

class DyTest (models.Model):
	'''工作量'''
	_name = 'dy.test'
	_order = 'id desc'
	# _inherit = ['mail.thread', 'ir.needaction_mixin']

	state = fields.Selection([('draft', u'草稿'),
								('start', u'启用中'),
								('cancel',u'取消'),
								('close', u'已完成')], u'状态', default='draft')
	READONLY_STATES = {
			'cancel': [('readonly', True)],
			'close': [('readonly', True)]
		}

	name = fields.Char(u'名称')

	occur_time = fields.Datetime(u'事件发生时间',required=True,track_visibility='onchange',default=fields.Datetime.now,readonly=True,states=READONLY_STATES)

	event_action_id = fields.Selection([('ok', u'成功'),('defeated', u'失败')], u'事件处理结果', default='ok')

	test_id = fields.Selection([('one', u'项目1'),('two', u'项目2')], u'项目', default='one')

	doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

	# teamName = fields.Many2one('team.name',u'团队名称',domain="[('mark','=','team')]",track_visibility='onchange')

	# teamUser = fields.Many2one('dy.team.user',u'团队人员',domain="[('parent_id','=', teamName)]")

	@api.model
	def _get_proposer_id(self):
		if self.env.uid:
			return self.env.uid
		raise UserError(u'请确认帐号')

	proposer_id = fields.Many2one('res.users',u'申请人',required=True,default=_get_proposer_id)

	def _get_team_name(self):
		if self.env.uid:
			return self.env['dy.team.user'].search([('name', '=', self.env.uid)]).parent_id


	team = fields.Many2one('team.name',u'团队',default=_get_team_name)

	# team_id = fields.Many2one('team.name',u'团队',store=False,default=_get_team_name)

	# @api.one
	# @api.depends('proposer_id')
	# def onchange_proposer_id(self):
	# 	self.env.cr.execute("select name from dy_team_user where parent_id= (select parent_id from dy_team_user where name = %d)" % (self.proposer_id))
	# 	teamsName = self.env.cr.fetchall()
	# 	users=[]
	# 	for user in range(len(teamsName)):
	# 		users.append(teamsName[user][0])
	# 		self.otherUser = users

	# otherUser = fields.Char(u'团队其它人员',store=True,compute=onchange_proposer_id)

	# @api.one
	# @api.depends('otherUser','test')
	# def is_teams(self):
	# 	teamUser = str(self.env.uid)
	# 	for r in self:
	# 		teamStr = str(r.otherUser)
	# 		otherUser = []
	# 		otherUser = teamStr
	# 		if teamUser in otherUser:
	# 			r.test = True
	# 		else:
	# 			r.test = False

	# # test = fields.Boolean(u'测试',store=False,compute=is_teams,select=True, translate=True)
	# test = fields.Boolean(u'团队中',store=False,compute=is_teams,select=True, translate=True)

	teamUser = fields.Many2many('res.users','ref_user_team',string=u'可修改人员')

	# res = models.execute_kw(db, uid, password,
	# 	'dy.test', 'search_read',
	# 	[['test', '=', 'show']],
	# 	{'fields': ['name'], 'limit': 5})

	@api.onchange('teamUser')
	def change_test(self):
		teams = []
		cacheUser = str(self.teamUser.ids)
		teams.append(cacheUser)
		self.test = teams[0]

	test = fields.Char(u'测试1')

	@api.one
	def work_start(self):
		''' 启用 '''
		self.state = 'start'


	@api.one
	def work_close(self):
		''' 已完成 '''
		self.state = 'close'

	@api.one
	def work_cancel(self):
		''' 取消 '''
		self.state = 'cancel'

	def _compute_attached_docs_count(self):
		Attachment = self.env['ir.attachment']
		for project in self:
			project.doc_count = Attachment.search_count([
				'|',
				('res_model', '=', 'dy.test'), ('res_id', '=', project.id)
			])

	@api.multi
	def attachment_tree_view(self):
		self.ensure_one()
		domain = [
			'|',('res_model', '=', 'dy.test'), ('res_id', 'in', self.ids)]
		return {
			'name': (u'附件名称'),
			'domain': domain,
			'res_model': 'ir.attachment',
			'type': 'ir.actions.act_window',
			'view_id': False,
			'view_mode': 'kanban,tree,form',
			'view_type': 'form',
			'limit': 80,
			'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
		}

	refers_to = fields.Reference(
		# Set a Selection list, such as:
		# [('res.user', 'User'), ('res.partner', 'Partner')],
		# Or use standard "Referencable Models":
		referenceable_models,
		'Refers to',  # string= (title)
	)

class DyTeamUser (models.Model):
	'''团队人员'''
	_name = 'dy.team.user'
	_description = "dy.team.user"

	name = fields.Many2one('res.users',u'团队人员')

	parent_id = fields.Many2one('team.name',u'团队名称',domain="[('mark','=','team')]",track_visibility='onchange')

	active = fields.Boolean(u'活跃')
