from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    teacher_id: int | None = None


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    is_active: bool | None = None


class CourseRead(BaseModel):
    id: int
    teacher_id: int
    name: str
    description: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class EnrollmentCreate(BaseModel):
    student_id: int


class EnrollmentRead(BaseModel):
    id: int
    course_id: int
    student_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)