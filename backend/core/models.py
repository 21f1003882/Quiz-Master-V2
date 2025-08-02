from core.extensions import db 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import uuid
from flask_security import UserMixin, RoleMixin 



user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'), primary_key=True)
)

class Role(db.Model, RoleMixin):
    """Model for user roles (Admin, User)."""
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'

class SecretQuestion(db.Model):
    """Model to store predefined secret questions."""
    __tablename__ = 'secret_question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), unique=True, nullable=False)


class User(db.Model, UserMixin):
    """Model for users (Admin and regular Users)."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean(), default=True, nullable=False) # Required by Flask-Security
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Many-to-Many relationship with Role
    roles = db.relationship('Role', secondary=user_roles,
                            backref=db.backref('users')) # Use dynamic if many users per role

    # Relationship to quiz attempts made by the user
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    secret_question_id = db.Column(db.Integer, db.ForeignKey('secret_question.id'), nullable=False)
    secret_answer_hash = db.Column(db.String(128), nullable=False)
    
    # Relationship to the chosen secret question
    secret_question = db.relationship('SecretQuestion', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def set_secret_answer(self, secret_answer):
        """Hashes and stores the secret answer."""
        if secret_answer:
            self.secret_answer_hash = generate_password_hash(secret_answer.lower().strip())

    def check_secret_answer(self, secret_answer):
        if not self.secret_answer_hash:
            return False
        return check_password_hash(self.secret_answer_hash, secret_answer.lower().strip())
    # Helper method (optional but convenient)
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.set_password(password)

    def __repr__(self):
        return f'<User {self.username}>'


class Subject(db.Model):
    """Model for subjects (e.g., Math, Science)."""
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-Many relationship with Chapter
    chapters = db.relationship('Chapter', backref='subject', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Subject {self.name}>'


class Chapter(db.Model):
    """Model for chapters within a subject."""
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Optional: Link to the admin who created it
    # created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # One-to-Many relationship with Quiz
    quizzes = db.relationship('Quiz', backref='chapter', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Chapter {self.name} in {self.subject.name}>'


class Quiz(db.Model):
    """Model for quizzes within a chapter."""
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    scheduled_date = db.Column(db.DateTime, nullable=True) # Allows for optional scheduling

    # One-to-Many relationship with Question
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade="all, delete-orphan")
    # One-to-Many relationship with QuizAttempt
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Quiz {self.title} in {self.chapter.name}>'


class Question(db.Model):
    """Model for MCQ questions within a quiz."""
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    # One-to-Many relationship with Option
    options = db.relationship('Option', backref='question', lazy='dynamic', cascade="all, delete-orphan")

    # You need a way to get the correct option. Using the relationship is one way.
    def get_correct_option(self):
      return self.options.filter_by(is_correct=True).first()

    def __repr__(self):
        return f'<Question Q{self.id} for {self.quiz.title}>'


class Option(db.Model):
    """Model for options for an MCQ question."""
    __tablename__ = 'option'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)

    def __repr__(self):
        return f'<Option {self.id}: {self.text} Correct={self.is_correct}>'


class QuizAttempt(db.Model):
    """Model to record user attempts at quizzes."""
    __tablename__ = 'quiz_attempt'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False) 
    total_questions = db.Column(db.Integer, nullable=False) 
    start_time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    @property
    def percentage_score(self):
        return round((self.score / self.total_questions) * 100, 2) if self.total_questions > 0 else 0

    @property
    def time_taken(self):
        if self.submitted_at and self.start_time:
            return self.submitted_at - self.start_time
        return None

    def __repr__(self):
        return f'<QuizAttempt User:{self.user_id} Quiz:{self.quiz_id} Score:{self.score}/{self.total_questions}>'
    
