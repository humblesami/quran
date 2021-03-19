from django.db import models


class Sura(models.Model):
    name = models.CharField(max_length=127)
    transliteration_en = models.CharField(max_length=127)
    translation_en = models.CharField(max_length=127)
    total_verses = models.PositiveIntegerField()
    revelation_type = models.CharField(max_length=63)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('id',)

    def save(self, *args, **kwargs):
        return

    def delete(self, *args, **kwargs):
        return


class Aya(models.Model):
    sura = models.ForeignKey(Sura, on_delete=models.RESTRICT)
    aya = models.PositiveIntegerField()
    arabic = models.CharField(max_length=4095)
    ur_maududi = models.CharField(max_length=4095)
    en_maududi = models.CharField(max_length=4095)

    def __str__(self):
        return self.sura.name + '-' + str(self.id)

    class Meta:
        ordering = ('id',)

    def save(self, *args, **kwargs):
        return

    def delete(self, *args, **kwargs):
        return

