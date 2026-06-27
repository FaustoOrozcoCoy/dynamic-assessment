from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Course, Enrollment, User
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate, EnrollmentCreate, EnrollmentRead


class CourseService:
    @staticmethod
    def _user_has_role(
        db: Session,
        user_id: int,
        role_name: str,
    ) -> bool:
        return RoleRepository.user_has_role(
            db=db,
            user_id=user_id,
            role_name=role_name,
        )

    @staticmethod
    def _ensure_course_exists(
        db: Session,
        course_id: int,
    ) -> Course:
        course = CourseRepository.get_by_id(
            db=db,
            course_id=course_id,
        )

        if course is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        return course

    @staticmethod
    def _ensure_course_manager(
        db: Session,
        course: Course,
        current_user: User,
    ) -> None:
        is_admin = CourseService._user_has_role(
            db=db,
            user_id=current_user.id,
            role_name="admin",
        )

        if is_admin:
            return

        is_teacher = CourseService._user_has_role(
            db=db,
            user_id=current_user.id,
            role_name="teacher",
        )

        if is_teacher and course.teacher_id == current_user.id:
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this course",
        )

    @staticmethod
    def create_course(
        db: Session,
        course_data: CourseCreate,
        current_user: User,
    ) -> CourseRead:
        is_admin = CourseService._user_has_role(
            db=db,
            user_id=current_user.id,
            role_name="admin",
        )

        is_teacher = CourseService._user_has_role(
            db=db,
            user_id=current_user.id,
            role_name="teacher",
        )

        if is_admin and course_data.teacher_id is not None:
            teacher_id = course_data.teacher_id

        elif is_teacher:
            teacher_id = current_user.id

        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins or teachers can create courses",
            )

        teacher = UserRepository.get_by_id(
            db=db,
            user_id=teacher_id,
        )

        if teacher is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher not found",
            )

        teacher_has_role = CourseService._user_has_role(
            db=db,
            user_id=teacher.id,
            role_name="teacher",
        )

        if not teacher_has_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user must have teacher role",
            )

        course = Course(
            teacher_id=teacher_id,
            name=course_data.name,
            description=course_data.description,
            is_active=True,
        )

        CourseRepository.create(
            db=db,
            course=course,
        )

        db.commit()
        db.refresh(course)

        return CourseRead.model_validate(course)

    @staticmethod
    def list_courses(
        db: Session,
        current_user: User,
    ) -> list[CourseRead]:
        is_admin = CourseService._user_has_role(
            db=db,
            user_id=current_user.id,
            role_name="admin",
        )

        if is_admin:
            courses = CourseRepository.list_all_active(db=db)
        else:
            courses = CourseRepository.list_by_teacher(
                db=db,
                teacher_id=current_user.id,
            )

        return [
            CourseRead.model_validate(course)
            for course in courses
        ]

    @staticmethod
    def get_course(
        db: Session,
        course_id: int,
        current_user: User,
    ) -> CourseRead:
        course = CourseService._ensure_course_exists(
            db=db,
            course_id=course_id,
        )

        CourseService._ensure_course_manager(
            db=db,
            course=course,
            current_user=current_user,
        )

        return CourseRead.model_validate(course)

    @staticmethod
    def update_course(
        db: Session,
        course_id: int,
        course_data: CourseUpdate,
        current_user: User,
    ) -> CourseRead:
        course = CourseService._ensure_course_exists(
            db=db,
            course_id=course_id,
        )

        CourseService._ensure_course_manager(
            db=db,
            course=course,
            current_user=current_user,
        )

        if course_data.name is not None:
            course.name = course_data.name

        if course_data.description is not None:
            course.description = course_data.description

        if course_data.is_active is not None:
            course.is_active = course_data.is_active

        db.commit()
        db.refresh(course)

        return CourseRead.model_validate(course)

    @staticmethod
    def deactivate_course(
        db: Session,
        course_id: int,
        current_user: User,
    ) -> None:
        course = CourseService._ensure_course_exists(
            db=db,
            course_id=course_id,
        )

        CourseService._ensure_course_manager(
            db=db,
            course=course,
            current_user=current_user,
        )

        course.is_active = False

        db.commit()

    @staticmethod
    def enroll_student(
        db: Session,
        course_id: int,
        enrollment_data: EnrollmentCreate,
        current_user: User,
    ) -> EnrollmentRead:
        course = CourseService._ensure_course_exists(
            db=db,
            course_id=course_id,
        )

        CourseService._ensure_course_manager(
            db=db,
            course=course,
            current_user=current_user,
        )

        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot enroll students in an inactive course",
            )

        student = UserRepository.get_by_id(
            db=db,
            user_id=enrollment_data.student_id,
        )

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        student_has_role = CourseService._user_has_role(
            db=db,
            user_id=student.id,
            role_name="student",
        )

        if not student_has_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user must have student role",
            )

        existing_enrollment = EnrollmentRepository.get_by_course_and_student(
            db=db,
            course_id=course.id,
            student_id=student.id,
        )

        if existing_enrollment is not None:
            if existing_enrollment.is_active:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Student is already enrolled in this course",
                )

            existing_enrollment.is_active = True
            db.commit()
            db.refresh(existing_enrollment)

            return EnrollmentRead.model_validate(existing_enrollment)

        enrollment = Enrollment(
            course_id=course.id,
            student_id=student.id,
            is_active=True,
        )

        EnrollmentRepository.create(
            db=db,
            enrollment=enrollment,
        )

        db.commit()
        db.refresh(enrollment)

        return EnrollmentRead.model_validate(enrollment)

    @staticmethod
    def list_course_enrollments(
        db: Session,
        course_id: int,
        current_user: User,
    ) -> list[EnrollmentRead]:
        course = CourseService._ensure_course_exists(
            db=db,
            course_id=course_id,
        )

        CourseService._ensure_course_manager(
            db=db,
            course=course,
            current_user=current_user,
        )

        enrollments = EnrollmentRepository.list_by_course(
            db=db,
            course_id=course.id,
        )

        return [
            EnrollmentRead.model_validate(enrollment)
            for enrollment in enrollments
        ]

    @staticmethod
    def remove_enrollment(
        db: Session,
        course_id: int,
        student_id: int,
        current_user: User,
    ) -> None:
        course = CourseService._ensure_course_exists(
            db=db,
            course_id=course_id,
        )

        CourseService._ensure_course_manager(
            db=db,
            course=course,
            current_user=current_user,
        )

        enrollment = EnrollmentRepository.get_by_course_and_student(
            db=db,
            course_id=course.id,
            student_id=student_id,
        )

        if enrollment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )

        enrollment.is_active = False

        db.commit()

    @staticmethod
    def list_my_courses(
        db: Session,
        current_user: User,
    ) -> list[CourseRead]:
        is_student = CourseService._user_has_role(
            db=db,
            user_id=current_user.id,
            role_name="student",
        )

        if not is_student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Student role is required",
            )

        courses = EnrollmentRepository.list_courses_by_student(
            db=db,
            student_id=current_user.id,
        )

        return [
            CourseRead.model_validate(course)
            for course in courses
        ]