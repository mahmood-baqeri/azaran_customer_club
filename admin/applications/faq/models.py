# applications/faq/models.py

from django.db import models
from applications.core.baseModel import BaseModel
from applications.user.models import User

class Category(BaseModel): 
    title = models.CharField(max_length=255, verbose_name="عنوان دسته‌بندی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        db_table = "faq_category"                              
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.title


class FAQ(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="faqs", verbose_name="دسته‌بندی") 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="faqs", verbose_name="کاربر پرسش‌کننده")
    question = models.TextField(verbose_name="سوال")
    
    is_active = models.BooleanField(default=False, verbose_name="فعال")

    class Meta:
        db_table = "faq_faq"                              
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.question[:50]


class Answer(BaseModel): 
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name="answers", verbose_name="پرسش")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="faq_answers", verbose_name="کاربر پاسخ‌دهنده")
    answer = models.TextField(verbose_name="پاسخ")
    
    is_active = models.BooleanField(default=False, verbose_name="فعال")
    
    class Meta:
        db_table = "faq_answer" 
        ordering = ["-created_at"]

    def __str__(self):
        return f"پاسخ به: {self.faq.question[:30]}"


class AnswerReaction(BaseModel):
    class ReactionType(models.TextChoices):
        LIKE = "like", "پسندیدن"
        DISLIKE = "dislike", "نپسندیدن"

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="reactions", verbose_name="پاسخ") 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="faq_reactions", verbose_name="کاربر")
    
    reaction = models.CharField(max_length=10, choices=ReactionType.choices, verbose_name="واکنش")

    class Meta:
        db_table = "faq_answer_reaction"                            
        ordering = ["-created_at"]
        constraints = [
            # ✅ یک کاربر فقط می‌تواند یک واکنش (لایک یا دیس‌لایک) برای هر پاسخ ثبت کند
            models.UniqueConstraint(
                fields=["answer", "user"],
                name="unique_user_answer_reaction"
            )
        ]

    def __str__(self):
        return f"{self.user.mobile} - {self.get_reaction_display()} - Answer {self.answer_id}"