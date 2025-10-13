from django.db import models


class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class TestOther(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Prueba Tipo"
        verbose_name_plural = "Pruebas Tipos"


class Test(models.Model):
    id = models.AutoField(primary_key=True)
    test_other = models.ForeignKey(
        TestOther, on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    counter = models.IntegerField()
    is_active = models.BooleanField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Prueba"
        verbose_name_plural = "Pruebas"
