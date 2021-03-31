# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    job_id = fields.Many2one(comodel_name='hr.job', string="Job Position")
    job_title_id = fields.Many2one(comodel_name='hr.job.title', string="Job Title")
    job_department_id = fields.Many2one(related='job_id.department_id')
    syndicate_id = fields.Many2one(comodel_name='hr.syndicate', string="Syndicate Subscription")


class TrainingSubject(models.Model):
    _name = "hr.training.subject"
    _description = "HR Training Subject"

    name = fields.Char(string="Course Name", required='True')
    categ_id = fields.Many2one('hr.subject.catg', required='True')
    description = fields.Text()
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    training_type = fields.Selection(string="Training Type",
                                     selection=[('course', 'Course'),
                                                ('scholarship', 'Scholarship'),
                                                ('conference', 'Conference')])
    training_place_id = fields.Many2one('hr.training.place', string="Training Place")
    responsible_id = fields.Many2one('hr.employee', ondelete='set null', string="Responsible", index=True)
    in_comp_training_check = fields.Boolean(compute='_check_training_place')
    trainer_type = fields.Selection(string="Trainer Type", selection=[('internal', 'Internal Trainer'),
                                                                      ('external', 'External Trainer')])
    training_duration = fields.Integer(help="Training duration per day/s.")
    participant_ids = fields.Many2many(comodel_name="hr.employee", string="Participants")
    evaluation_ids = fields.One2many(comodel_name="hr.training.evaluation", inverse_name="subject_id",
                                     string="Participants")

    @api.depends('training_place_id.training')
    def _check_training_place(self):
        for rec in self:
            if rec.training_place_id.training == 'in_company':
                rec.in_comp_training_check = True
            else:
                rec.in_comp_training_check = False

    # @api.onchange('participant_ids')
    # def onchage_participant_ids(self):
    #     for rec in self:
    #         x = rec.participant_ids
    #         pass
    # @api.model
    # def create(self, values):
    #     if values['participant_ids'][0][2]:
    #         x = 1
    #     # return super(TrainingSubject, self).create(values)

    def write(self, values):
        old_users = []
        updated_users = []
        if self.participant_ids:
            old_users = self.participant_ids.ids
        if values.get('participant_ids'):
            updated_users = values.get('participant_ids')[0][2]
        added_users = list(set(updated_users) - set(old_users))
        removed_users = list(set(old_users) - set(updated_users))
        if added_users:
            for user in added_users:
                self.env['hr.training.evaluation'].create({
                    'subject_id': self.id,
                    'trainee_id': user,
                })

        return super(TrainingSubject, self).write(values)


class TrainingPlace(models.Model):
    _name = "hr.training.place"
    _description = "HR Training Place"

    name = fields.Char(string="Training Place", required='True')
    training = fields.Selection(string="In or Out company",
                                selection=[('in_company', 'Inside the company'),
                                           ('out_company', 'Outside the company'), ])
    subject_ids = fields.One2many(comodel_name="hr.training.subject", inverse_name="training_place_id",
                                  string="Course Subject", required=False)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    training_cost_type = fields.Selection(string="Training Cost Type",
                                          selection=[('paid', 'Paid'), ('unpaid', 'Unpaid')])
    training_cost = fields.Monetary(string="Training Cost")


class SubjectCategory(models.Model):
    _name = 'hr.subject.catg'
    _description = 'HR Subject Category'

    name = fields.Char(string="Category")
    subject_ids = fields.One2many('hr.training.subject', 'categ_id')


class Session(models.Model):
    _name = 'hr.session'
    _description = 'HR Sessions'

    name = fields.Char(string="Session", required=True)
    subject_id = fields.Many2one('hr.training.subject', string="Course Subject", required=True)
    session_date = fields.Datetime(string="Session Date")
    session_duration = fields.Float(string="Duration", digits=(6, 2), help="Session duration per hours.")
    session_duration_display = fields.Char(string="Duration", help="Session duration per hours.",
                                           compute="_compute_session_duration")
    seats = fields.Integer(string="Number of seats")
    instructor_id = fields.Many2one('hr.employee', string="Instructor")
    attendee_ids = fields.Many2many('hr.employee', string='Attendees')

    @api.onchange('subject_id')
    def onchange_subject_id(self):
        for rec in self:
            rec.instructor_id = rec.subject_id.responsible_id

    @api.onchange('session_duration')
    def _compute_session_duration(self):
        for rec in self:
            rec.session_duration_display = str(rec.session_duration) + "  ساعة  "


class TrainingEvaluation(models.Model):
    _name = "hr.training.evaluation"
    _description = "HR Training Evaluation"

    name = fields.Char()
    # evaluation = fields.Char(string="Evaluation", compute='_compute_grade')
    # grade_name = fields.Selection(string="Grade", selection=[('excelent', 'ممتاز'),
    #                                                     ('very_good', 'جيد جدا'),
    #                                                     ('good', 'جيد'),
    #                                                     ('accepted', 'مقبول')])
    subject_id = fields.Many2one('hr.training.subject')
    trainee_id = fields.Many2one('hr.employee')
    grade = fields.Integer()

    @api.onchange('grade')
    def _compute_grade(self):
        for rec in self:
            if rec.grade:
                if rec.grade < 60:
                    rec.name = ""
                elif 60 <= rec.grade <= 65:
                    rec.name = ""
                elif 66 <= rec.grade <= 75:
                    rec.name = "Good"
                elif 76 <= rec.grade <= 89:
                    rec.name = "Very Good"
                elif 90 <= rec.grade <= 100:
                    rec.name = "Excellent"
                else:
                    raise ValidationError(_("Enter a valid number ..."))


class Reassignment(models.Model):
    _name = "hr.reassignment"
    _description = "HR Reassignment"

    name = fields.Char(string="Reassignment")
    employee_id = fields.Many2one('hr.employee', string="Employee Name", required=True)
    certificate = fields.Selection('Certificate Level', related='employee_id.certificate', default='other',
                                   readonly=True, tracking=True)
    # payment_mode = fields.Selection(related='expense_line_ids.payment_mode', default='own_account', readonly=True,
    #                                   string="Paid By", tracking=True)
    new_certificate = fields.Selection([
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'other'),
    ], 'New Certificate Level', required=True, tracking=True)
    date_reassignment = fields.Date(string="Reassignment Date", default=fields.Date.today())
    job_functional_id = fields.Many2one('hr.job.functional', string="Job Functional Group")
    job_qualitative_id = fields.Many2one('hr.job.qualitative', string="Job Qualitative")
    job_title_id = fields.Many2one('hr.job.title', string="Job Title", required=True)
    full_name = fields.Char('Job Full Name', related='employee_id.job_title_id.full_name')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """
        This function -onchange the employee_id- change the value of:
            certeficate = employee certeficate
            job_functional_id = employee job_functional_id
            job_qualitative_id = employee job_qualitative_id
            job_title_id = employee job_title_id
            name = employee name + the new job position
        """
        for rec in self:
            if rec.employee_id:
                rec.job_functional_id = False
                rec.job_qualitative_id = False
                rec.job_title_id = False
                rec.name = rec.employee_id.name + " / " + rec.employee_id.name

    @api.onchange('job_functional_id')
    def onchange_job_functional_id(self):
        """
        This function filters job_qualitative_id domain according the value in  job_functional_id.
        :return: domain
        """
        for rec in self:
            rec.job_qualitative_id = False
            rec.job_title_id = False
            return {'domain': {'job_qualitative_id': [('job_functional_id', '=', rec.job_functional_id.id)]}}

    @api.onchange('job_qualitative_id')
    def onchange_job_qualitative_id(self):
        """
        This function filters job_title_id domain according the value in  job_qualitative_id.
        :return: domain
        """
        for rec in self:
            rec.job_title_id = False
            return {'domain': {'job_title_id': [('job_qualitative_id', '=', rec.job_qualitative_id.id)]}}

    @api.onchange('job_title_id')
    def onchange_job_title_id(self):
        """
        This function -onchange job_title_id- change the value of the name to concatenates:
            employee name + the new job
        """
        for rec in self:
            if rec.employee_id and rec.job_title_id:
                job_name = ' / '.join([rec.employee_id.name, rec.job_title_id.name])
                rec.name = job_name

    @api.model
    def create(self, values):
        if values.get('job_title_id', False) and values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values['employee_id'])
            employee.certificate = values['new_certificate']
            employee.job_title_id = values['job_title_id']
        return super(Reassignment, self).create(values)

    def write(self, values):
        """Update the job_title_id of current employee to be equal to current job_title_id"""
        if values.get('employee_id', False) or \
                values.get('job_title_id', False) or \
                values.get('new_certificate', False):
            employee = self.env['hr.employee'].browse(values.get('employee_id', self.employee_id.id))
            employee.job_title_id = values.get('job_title_id', self.job_title_id)
            employee.certificate = values.get('new_certificate', self.new_certificate)
        return super(Reassignment, self).write(values)


class HRSyndicate(models.Model):
    _name = "hr.syndicate"
    _description = "HR Syndicate"

    name = fields.Char(string="Syndicate Subscription", required=True)
    code = fields.Char(string="Code", required=True)
