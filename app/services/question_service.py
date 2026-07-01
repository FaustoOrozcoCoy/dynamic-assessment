import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models import Question, QuestionOption, User
from app.models.question import QuestionType
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, QuestionRead, QuestionOptionCreate, QuestionOptionRead

IMAGES_DIR = Path("app/static/images")
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
_EXTENSION_MAP = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
}

class QuestionService:
    
    @staticmethod
    def _validate_options(question_type: QuestionType, options_data: list[QuestionOptionCreate]):
        # Regla: single_choice solo debe tener UNA correcta (domain.md)
        if question_type == QuestionType.single_choice:
            correct_count = sum(1 for opt in options_data if opt.is_correct)
            if correct_count > 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="single_choice questions can only have one correct option."
                )

    @staticmethod
    def create_question(db: Session, question_data: QuestionCreate, current_user: User) -> QuestionRead:
        
        QuestionService._validate_options(question_data.question_type, question_data.options)

        question = Question(
            created_by_id=current_user.id,
            question_type=question_data.question_type,
            statement=question_data.statement,
            image_path=question_data.image_path,
            config_json=question_data.config_json,
            is_active=True
        )

        for opt in question_data.options:
            option = QuestionOption(
                label=opt.label,
                value=opt.value,
                is_correct=opt.is_correct,
                is_exclusive=opt.is_exclusive,
                order_index=opt.order_index
            )
            question.options.append(option)

        QuestionRepository.create(db=db, question=question)
        db.commit()
        db.refresh(question)

        return QuestionRead.model_validate(question)

    @staticmethod
    def list_questions(db: Session) -> list[QuestionRead]:
        # Las preguntas son de un banco compartido, todos los activos las ven
        questions = QuestionRepository.list_all_active(db)
        return [QuestionRead.model_validate(q) for q in questions]

    @staticmethod
    def get_question(db: Session, question_id: int) -> QuestionRead:
        question = QuestionRepository.get_by_id(db, question_id)
        if not question or not question.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        return QuestionRead.model_validate(question)

    @staticmethod
    def upload_image(db: Session, question_id: int, file: UploadFile, current_user: User) -> QuestionRead:
        question = QuestionRepository.get_by_id(db, question_id)
        if not question or not question.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: png, jpg, gif, webp.",
            )

        contents = file.file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum allowed size is 5 MB.",
            )

        # Remove previous image file if one exists
        if question.image_path:
            old_file = Path("app") / question.image_path.lstrip("/")
            if old_file.exists():
                old_file.unlink()

        extension = _EXTENSION_MAP[file.content_type]
        filename = f"{uuid.uuid4().hex}{extension}"
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        (IMAGES_DIR / filename).write_bytes(contents)

        question.image_path = f"/static/images/{filename}"
        db.commit()
        db.refresh(question)

        return QuestionRead.model_validate(question)

    @staticmethod
    def deactivate_question(db: Session, question_id: int):
        question = QuestionRepository.get_by_id(db, question_id)
        if not question or not question.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        
        # Soft delete
        question.is_active = False
        db.commit()

    @staticmethod
    def add_option(db: Session, question_id: int, option_data: QuestionOptionCreate) -> QuestionOptionRead:
        question = QuestionRepository.get_by_id(db, question_id)
        if not question or not question.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
        
        option = QuestionOption(
            question_id=question.id,
            label=option_data.label,
            value=option_data.value,
            is_correct=option_data.is_correct,
            is_exclusive=option_data.is_exclusive,
            order_index=option_data.order_index
        )
        QuestionRepository.add_option(db, option)
        db.commit()
        db.refresh(option)
        return QuestionOptionRead.model_validate(option)
    
    @staticmethod
    def delete_option(db: Session, question_id: int, option_id: int):
        option = QuestionRepository.get_option_by_id(db, option_id)
        if not option or option.question_id != question_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
        
        db.delete(option)
        db.commit()