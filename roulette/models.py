from django.db import models


class Roulette(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255, unique=True, help_text="A unique slug for the roulette URL."
    )
    logo = models.ImageField(upload_to="roulette/logos/")
    subtitle = models.CharField(max_length=255, default="", blank=True)
    bottom_text = models.TextField(default="", blank=True)
    bg_image = models.ImageField(upload_to="roulette/backgrounds/")
    current_spins = models.IntegerField(
        default=0, help_text="Tracks the total number of spins for this roulette."
    )
    wrong_icon = models.ImageField(upload_to="roulette/icons/")
    message_error_no_spin = models.CharField(max_length=255)
    message_lose_lose = models.CharField(max_length=255)
    message_win = models.CharField(max_length=255)

    # accepts hex color code, e.g., #FFFFFF
    color_spin_1 = models.CharField(
        max_length=7, help_text="Hex color code, e.g., #FFFFFF"
    )
    color_spin_2 = models.CharField(
        max_length=7, help_text="Hex color code, e.g., #FFFFFF"
    )
    color_spin_3 = models.CharField(
        max_length=7, help_text="Hex color code, e.g., #FFFFFF"
    )
    color_spin_4 = models.CharField(
        max_length=7, help_text="Hex color code, e.g., #FFFFFF"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Award(models.Model):
    roulette = models.ForeignKey(
        Roulette, on_delete=models.CASCADE, related_name="awards"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    min_spins = models.IntegerField(
        help_text="Minimum spins required to be eligible for this award."
    )
    image = models.ImageField(upload_to="awards/")
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.roulette.name})"


class Participant(models.Model):
    roulette = models.ForeignKey(
        Roulette, on_delete=models.CASCADE, related_name="participants"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(
        unique=True, help_text="Each participant must have a unique email."
    )
    last_spin = models.DateTimeField(null=True, blank=True)
    last_extra_spin = models.DateTimeField(null=True, blank=True)

    # Many-to-Many relationship
    awards = models.ManyToManyField(
        Award, through="ParticipantAward", related_name="winners"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} <{self.email}>"


class ParticipantAward(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp of when the award was won."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Participant's Award"
        verbose_name_plural = "Participant's Awards"

    def __str__(self):
        return f"{self.participant.name} won {self.award.name}"
