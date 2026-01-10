from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse email")
    subject = models.CharField(max_length=200, verbose_name="Sujet", blank=True)
    reason = models.CharField(max_length=200, verbose_name="Motif", blank=True)
    message = models.TextField(verbose_name="Message")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.name} - {self.email}"