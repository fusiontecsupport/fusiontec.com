from django.db import models

# Contact submission - Enquiry form model

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.submitted_at.strftime('%Y-%m-%d %H:%M')})"
    

# -----------------------------------------------------------
# Tally full section database models

class Tally_1(models.Model):
    tally_name = models.CharField(max_length=255)
    tally_description = models.TextField(blank=True, null=True)
    tally_image = models.ImageField(upload_to='products/')
    tally_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.tally_name

class Tally_Product(models.Model):
    tally_1 = models.ForeignKey(Tally_1, on_delete=models.CASCADE, related_name='types')
    type_name = models.CharField(max_length=255, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="CGST @ 9%", default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="SGST @ 9%", default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.basic_amount + self.sgst + self.cgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.type_name}"

class Tally_Software_Service(models.Model):
    tally_1 = models.ForeignKey(Tally_1, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=255, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="CGST @ 9%", default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="SGST @ 9%", default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.basic_amount + self.sgst + self.cgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.type_name}"

class Tally_Upgrade(models.Model):
    tally_1 = models.ForeignKey(Tally_1, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=255, null=True)
    basic_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="CGST @ 9%", default=0)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, help_text="SGST @ 9%", default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.basic_amount + self.sgst + self.cgst
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.type_name}"

# -----------------------------------------------------------
# E-mudhra section database models
class Emudhra_2(models.Model):
    emudhra_name = models.CharField(max_length=255)
    emudhra_description = models.TextField(blank=True, null=True)
    emudhra_image = models.ImageField(upload_to='products/')
    emudhra_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.emudhra_name

class Emudhra_product(models.Model):
    emudhra_2 = models.ForeignKey(Emudhra_2, on_delete=models.CASCADE)  # Use lowercase for field name
    class_product = models.CharField(max_length=255, null=True)
    emudhra_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return f"{self.class_product} - {self.rate}"
    
# -----------------------------------------------------------
# Fusiontec section database models

class Fusiontec_3(models.Model):
    fusiontec_name = models.CharField(max_length=255)
    fusiontec_description = models.TextField(blank=True, null=True)
    fusiontec_image = models.ImageField(upload_to='products/')
    fusiontec_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.fusiontec_name

class Fusiontec_product(models.Model):
    fusiontec_3 = models.ForeignKey(Fusiontec_3, on_delete=models.CASCADE)  # ForeignKey to Fusiontec_3
    fusiontec_product = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.fusiontec_product

# -----------------------------------------------------------
# biz section database models

class Biz_4(models.Model):
    biz_name = models.CharField(max_length=255)
    biz_description = models.TextField(blank=True, null=True)
    biz_image = models.ImageField(upload_to='products/')
    biz_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.biz_name
    
class biz_product(models.Model):
    biz_4 = models.ForeignKey(Biz_4, on_delete=models.CASCADE)  
    team_name = models.CharField(max_length=255, default="For Sales Team") 
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # e.g., 3600
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # e.g., 3300
    billing_cycle = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        default="Billed for 1 Year | Per Device"
    )

    def __str__(self):
        return f"{self.team_name} ({self.new_price})"