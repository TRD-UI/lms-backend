"""
Entity package imports.

Import all ORM entities to ensure they are registered with SQLAlchemy when the
application starts. Keeping this module simple avoids circular import issues.
"""

from app.entities.auth_tables import RefreshToken
from app.entities.profiles import StudentProfile, InstructorProfile, Expertise
from app.entities.users import User
# from app.entities.courses import Enrollment, Course, CourseRating, CourseCategory