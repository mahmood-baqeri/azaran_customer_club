# applications/review/models.py

from django.db import models
from applications.core.baseModel import BaseModel
from applications.user.models import User


#######################################
# ReviewQuestion (سوالات نظرسنجی)
#######################################
class ReviewQuestion(BaseModel):    
    question = models.CharField(max_length=255, verbose_name="سوال")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = 'review_question'
        verbose_name = "سوال نظرسنجی"
        verbose_name_plural = "سوالات نظرسنجی"

    def __str__(self):
        return self.question 


#######################################
# ReviewAnswer (پاسخ‌های کاربران)
#######################################
class ReviewAnswer(BaseModel):
    class AnswerItem(models.TextChoices):
        VeryLittle = "very_little", "خیلی کم"
        Little = "little", "کم"
        Average = "average", "متوسط"
        ALot = "a_lot", "زیاد"
        VeryMuch = "very_much", "خیلی زیاد"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_answers', verbose_name="کاربر")
    question = models.ForeignKey(ReviewQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name="سوال")
    answer = models.CharField(
        max_length=50, 
        choices=AnswerItem.choices, 
        default=AnswerItem.VeryLittle, 
        verbose_name="پاسخ"
    )

    class Meta:
        db_table = 'review_answer'
        verbose_name = "پاسخ نظرسنجی"
        verbose_name_plural = "پاسخ‌های نظرسنجی"
        # 👈 این خط تضمین می‌کند هر کاربر فقط یک بار به هر سوال جواب می‌دهد
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name='unique_user_question_answer')
        ]

    def __str__(self):
        return f"پاسخ {self.user.mobile} به سوال {self.question_id}"