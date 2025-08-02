# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField, SelectField, IntegerField, DateTimeField, RadioField
from wtforms.validators import DataRequired, Optional, Length, Email, EqualTo, ValidationError, NumberRange
from core.models import User, Subject, Chapter

class LoginForm(FlaskForm):
    """Main login form (matches fields in login.html)."""
    # The template uses name="username", name="password" directly,
    # but defining the form helps with CSRF and potential validation later.
    # Let's match template 'placeholder' names for clarity
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me') # Assuming you might add a checkbox
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Matches fields in the Create Account modal."""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Register')

    # Custom validators (optional but good practice)
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email address already registered.')

class ForgotPasswordForm(FlaskForm):
    """Matches fields in the Forgot Password modal."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

'''
# ResetPasswordForm later if implementing the full flow
# class ResetPasswordForm(FlaskForm):
#     password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=128)])
#     confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Reset Password')
'''

class SubjectForm(FlaskForm):
    """Form for adding/editing Subjects."""
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description') # Optional description
    submit = SubmitField('Save')

    # Optional: Add validation to prevent duplicate subject names during edit/add
    def __init__(self, original_name=None, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
    
    def validate_name(self, name):
        if name.data != self.original_name:
            subject = Subject.query.filter_by(name=name.data).first()
            if subject:
                raise ValidationError('Subject name already exists. Please choose a different name.')

class ChapterForm(FlaskForm):
    """Form for adding/editing Chapters."""
    name = StringField('Chapter Name', validators=[DataRequired(), Length(max=100)])
    # subject_id will likely be passed via URL or a hidden field if needed,
    # or selected if adding chapter from a general page.
    # For adding within a subject accordion, we'll get subject_id from URL.
    # subject_id = HiddenField() # Example if passing via form
    submit = SubmitField('Save Chapter')

class QuizForm(FlaskForm):
    """Form for adding/editing Quizzes."""
    title = StringField('Quiz Title', validators=[DataRequired(), Length(max=150)])
    chapter_id = SelectField('Chapter', coerce=int, validators=[DataRequired()])
    duration_minutes = IntegerField('Duration (Minutes)', validators=[DataRequired(), NumberRange(min=1)])
    is_active = BooleanField('Is Active', default=True)
    submit = SubmitField('Save Quiz')

class QuestionWithOptionsForm(FlaskForm):
    """Form for adding/editing a Question and its 4 Options."""
    text = TextAreaField('Question Text', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired(), Length(max=255)])
    option2 = StringField('Option 2', validators=[DataRequired(), Length(max=255)])
    option3 = StringField('Option 3', validators=[DataRequired(), Length(max=255)])
    option4 = StringField('Option 4', validators=[DataRequired(), Length(max=255)])
    # 'coerce=int' converts submitted value ('1', '2', etc.) to integer
    # Choices set dynamically: (value, label)
    correct_option = RadioField(
        'Correct Answer',
        choices=[('1', 'Option 1'), ('2', 'Option 2'), ('3', 'Option 3'), ('4', 'Option 4')],
        coerce=int,
        validators=[DataRequired(message="Please select the correct option.")]
    )
    submit = SubmitField('Save Question')