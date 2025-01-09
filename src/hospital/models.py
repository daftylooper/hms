from django.db import models

class Hospital(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    addr = models.CharField(max_length=256)

    def __str__(self):
        return f'hospital@{self.id}@{self.name}'
    
class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f'department@{self.id}@{self.name}'
    
# a table holding the m:n relations beween hospital and department
class HospitalDepartment(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('hospital', 'department')

    def __str__(self):
        return f'{self.hospital.name}@{self.department.name}'
    