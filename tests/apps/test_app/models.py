from django.db import models


class ShellCompleteTester(models.Model):
    char_field = models.CharField(max_length=15, db_index=True, default="")
    text_field = models.TextField(default="")
    float_field = models.FloatField(db_index=True, default=None, null=True)
    decimal_field = models.DecimalField(
        db_index=True, default=None, null=True, max_digits=10, decimal_places=2
    )
    uuid_field = models.UUIDField(null=True, default=None, unique=True)

    binary_field = models.BinaryField(null=True, default=None)

    ip_field = models.GenericIPAddressField(null=True, default=None, db_index=True)

    email_field = models.EmailField(null=True, default=None, db_index=True)

    url_field = models.URLField(null=True, default=None, db_index=True)

    file_field = models.FileField(
        null=True, default=None, upload_to="documents/", db_index=True
    )

    file_path_field = models.FilePathField(null=True, default=None, db_index=True)
