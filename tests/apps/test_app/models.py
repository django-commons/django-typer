from django.db import models
import django


def get_ip_choices():
    return [
        ("192.168.0.1", "Private Residential"),
        ("10.0.0.1", "Private Gateway"),
        ("172.16.0.1", "Corporate Network Gateway"),
        ("8.8.8.8", "Google DNS"),
        ("127.0.0.1", "Localhost IPv4"),
        ("::1", "Localhost IPv6"),
        ("2001:4860:4860::8888", "Google DNS IPv6"),
        ("fe80::1", "Link-Local IPv6"),
        ("fd00::1", "Private Network IPv6"),
        ("2001:db8::1", "Documentation Example IPv6"),
    ]


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

    date_field = models.DateField(null=True, default=None, db_index=True)

    datetime_field = models.DateTimeField(null=True, default=None, db_index=True)

    time_field = models.TimeField(null=True, default=None, db_index=True)

    duration_field = models.DurationField(null=True, default=None, db_index=True)


class ChoicesShellCompleteTester(models.Model):
    CHAR_CHOICES = [
        ("git", "Git"),
        ("svn", "Subversion (SVN)"),
        ("hg", "Mercurial (Hg)"),
        ("bzr", "Bazaar (Bzr)"),
        ("cvs", "CVS"),
        ("perforce", "Perforce"),
        ("fossil", "Fossil"),
        ("darcs", "Darcs"),
        ("monotone", "Monotone"),
    ]

    char_choice = models.CharField(
        max_length=12,
        choices=CHAR_CHOICES,
        db_index=True,
        default=None,
        null=True,
    )

    INT_CHOICES = [
        (1, "One"),
        (2, "Two"),
        (3, "Mercurial (Hg)"),
        (4, "Bazaar (Bzr)"),
        (5, "CVS"),
        (6, "Perforce"),
        (7, "Fossil"),
        (8, "Darcs"),
        (9, "Monotone"),
        (10, "Ten"),
        (11, "Eleven"),
        (12, "Twelve"),
    ]

    int_choice = models.PositiveSmallIntegerField(
        choices=INT_CHOICES,
        db_index=True,
        default=None,
        null=True,
    )

    IP_CHOICES = [
        ("192.168.0.1", "Private Residential"),
        ("10.0.0.1", "Private Gateway"),
        ("172.16.0.1", "Corporate Network Gateway"),
        ("8.8.8.8", "Google DNS"),
        ("127.0.0.1", "Localhost IPv4"),
        ("::1", "Localhost IPv6"),
        ("2001:4860:4860::8888", "Google DNS IPv6"),
        ("fe80::1", "Link-Local IPv6"),
        ("fd00::1", "Private Network IPv6"),
        ("2001:db8::1", "Documentation Example IPv6"),
    ]

    ip_choice = models.GenericIPAddressField(
        choices=IP_CHOICES,
        db_index=True,
        default=None,
        null=True,
    )
