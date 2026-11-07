from django.db import models

from applications.core.keyValue import Applications



#######################################
#  Actions
#######################################m     مثل (اضافه کردن مدیر ، دیدن مدیر و ...)
class Actions(models.Model):
    model = models.CharField(max_length=50, choices=Applications(), verbose_name="ماژول")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    action = models.CharField(max_length=255, verbose_name="فعالیت")

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'role_actions'


#######################################
#  Role
#######################################
class Role(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="عنوان")
    action_ids = models.JSONField()

    def __str__(self):
        return self.title

    class Meta:
        db_table ='role_role'
        verbose_name_plural = "نقش ها"
        verbose_name = "نقش"


#############################################################################
#############################################################################
#############################################################################
#############################################################################
def formFields(item=None):
    select2 = []
    for ac in Actions.objects.all():
        select2.append({'label': ac.title, 'id': ac.id, 'model': ac.get_model_display()})

    data = [
        {
            'l': 'نام',
            'n': 'title',
            'v': item.title if item else '',
            'id': 'thetitle',
            'r': None,
            'c': 'col-md-12',
            'b': 'textBox.html'
        },
        {
            'l': 'نقش',
            'n': 'action_id',
            'v': item.action_ids if item else [],
            'id': 'theaction_id',
            'r': None,
            'data': select2,
            'c': 'col-md-3',
            'b': 'roleComponent.html'
        }
    ]
    return data
