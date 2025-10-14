from django.db import models
from django.utils.text import slugify


class Roulette(models.Model):
    # Texts
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        verbose_name="Slug",
        help_text="url autogenerada para la ruleta.",
    )
    subtitle = models.CharField(
        max_length=255, default="", blank=True, verbose_name="Subtítulo"
    )
    bottom_text = models.TextField(
        default="", blank=True, verbose_name="Texto inferior"
    )

    # Settings
    spins_space_hours = models.IntegerField(
        default=0,
        verbose_name="Espacio entre giros (horas)",
        help_text="e.g. 2 (girar una vez cada 2 horas)",
    )
    spins_ads_limit = models.IntegerField(
        default=0,
        verbose_name="Límite de giros (ads)",
        help_text="e.g. 2 (girar 2 veces extra, en base al Espacio entre giros)",
    )
    
    # Images
    logo = models.ImageField(upload_to="roulette/logos/", verbose_name="Logo")
    bg_image = models.ImageField(
        upload_to="roulette/backgrounds/", verbose_name="Imagen de fondo"
    )
    wrong_icon = models.ImageField(
        upload_to="roulette/icons/", verbose_name="Icono de error (sin premio)"
    )

    # Messages
    message_no_spins = models.CharField(
        max_length=255, verbose_name="Mensaje de error (sin mas giros)"
    )
    message_lose = models.CharField(
        max_length=255, verbose_name="Mensaje de error (perdió)"
    )
    message_win = models.CharField(
        max_length=255, verbose_name="Mensaje de felicitaciones (ganó)"
    )

    # Colors
    color_spin_1 = models.CharField(
        max_length=7, verbose_name="Color 1", help_text="Hex color code, e.g., #FFFFFF"
    )
    color_spin_2 = models.CharField(
        max_length=7, verbose_name="Color 2", help_text="Hex color code, e.g., #FFFFFF"
    )
    color_spin_3 = models.CharField(
        max_length=7, verbose_name="Color 3", help_text="Hex color code, e.g., #FFFFFF"
    )
    color_spin_4 = models.CharField(
        max_length=7, verbose_name="Color 4", help_text="Hex color code, e.g., #FFFFFF"
    )

    # dates
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Ruleta"
        verbose_name_plural = "Rouletas"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Create slug based on name
        self.slug = slugify(self.name)

        # Save the model
        super().save(*args, **kwargs)


class Award(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    roulette = models.ForeignKey(
        Roulette, on_delete=models.CASCADE, related_name="awards", verbose_name="Ruleta"
    )
    name = models.CharField(max_length=255, verbose_name="Nombre")
    description = models.TextField(default="", blank=True, verbose_name="Descripción")
    min_spins = models.IntegerField(
        verbose_name="Mínimo de giros",
        help_text="Mínimo de giros requeridos para ser elegible para este premio.",
    )
    image = models.ImageField(upload_to="awards/", verbose_name="Imagen del premio")
    active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Si está activo, el premio se mostrará en la ruleta.",
    )

    # dates
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Premio"
        verbose_name_plural = "Premios"

    def __str__(self):
        return f"{self.name} ({self.roulette.name})"


class Participant(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Nombre")
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    # dates
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"

    def __str__(self):
        return f"{self.name} ({self.email})"


class ParticipantSpin(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="Participante"
    )
    roulette = models.ForeignKey(
        Roulette, on_delete=models.CASCADE, verbose_name="Ruleta"
    )
    is_extra_spin = models.BooleanField(
        default=False, verbose_name="Es giro extra (ads)"
    )

    # dates
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Giro de Participante"
        verbose_name_plural = "Giros de Participantes"

    def __str__(self):
        return f"{self.participant.name} ({self.last_spin})"


class ParticipantAward(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE, verbose_name="Participante"
    )
    award = models.ForeignKey(Award, on_delete=models.CASCADE, verbose_name="Premio")

    # dates
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha y hora de cuando el premio fue ganado."
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Premio de Participante"
        verbose_name_plural = "Premios de Participantes"

    def __str__(self):
        return f"{self.participant.name} won {self.award.name}"
